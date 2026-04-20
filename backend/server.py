from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import List, Optional
import uvicorn

# ✅ NEW Gemini SDK
from google import genai

app = FastAPI(title="Knowledge Base Search Engine", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory document store
document_store: dict[str, str] = {}

# ✅ Configure Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---------- Models ----------

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    model: str


class DocumentInfo(BaseModel):
    name: str
    size: int
    preview: str


# ---------- Routes ----------

@app.get("/")
def root():
    return {"status": "ok", "message": "Knowledge Base Search Engine API"}


@app.post("/ingest", response_model=DocumentInfo)
async def ingest_document(file: UploadFile = File(...)):
    allowed_types = {".txt", ".md", ".csv", ".json", ".pdf"}
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in allowed_types:
        raise HTTPException(status_code=400, detail=f"File type {ext} not supported.")

    content = await file.read()

    if ext == ".pdf":
        try:
            import pypdf
            import io
            reader = pypdf.PdfReader(io.BytesIO(content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except:
            text = "[PDF parsing failed - install pypdf]"
    else:
        text = content.decode("utf-8", errors="ignore")

    if not text.strip():
        text = "[Document contains no readable text]"

    document_store[file.filename] = text

    return DocumentInfo(
        name=file.filename,
        size=len(content),
        preview=text[:200]
    )


@app.post("/query", response_model=QueryResponse)
def query_knowledge_base(req: QueryRequest):

    if not document_store:
        raise HTTPException(status_code=400, detail="No documents uploaded")

    # 🔍 Simple keyword retrieval
    def score_doc(text: str, query: str):
        words = set(query.lower().split())
        return sum(text.lower().count(w) for w in words)

    ranked = sorted(document_store.items(), key=lambda x: score_doc(x[1], req.query), reverse=True)
    top_docs = ranked[:req.top_k]

    context_parts = []
    sources = []

    for name, content in top_docs:
        if content.strip():
            context_parts.append(f"=== {name} ===\n{content[:6000]}")
            sources.append(name)

    context = "\n\n".join(context_parts)

    if not context.strip():
        return QueryResponse(
            answer="No readable content found in documents.",
            sources=sources,
            model="models/gemini-2.5-flash"
        )

    # ✅ RAG Prompt
    prompt = f"""
You are a precise knowledge-base search assistant using Retrieval-Augmented Generation (RAG).

Answer the user's question using ONLY the provided document context.
Be concise but thorough.
Mention which document(s) you used.
If answer is not found, clearly say so.

DOCUMENT CONTEXT:
{context}

Question:
{req.query}
"""

    # 🔥 SMALL IMPROVEMENT (retry for Gemini errors)
    import time
    answer = None

    for attempt in range(2):  # keep small to stay similar
        try:
            response = client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=prompt
            )

            answer = response.text or "No answer generated."
            break

        except Exception as e:
            print("Gemini error:", e)
            time.sleep(1)

    if not answer:
        answer = "Gemini is busy. Try again."

    return QueryResponse(
        answer=answer,
        sources=sources,
        model="models/gemini-2.5-flash"
    )


# ✅ Test Gemini connection
@app.get("/test-gemini")
def test_gemini():
    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents="Say hello in one sentence."
        )
        return {"response": response.text}
    except Exception as e:
        return {"error": str(e)}
# ✅ List available models
@app.get("/list-models")
def list_models():
    try:
        models = client.models.list()
        return {"models": [{"name": m.name} for m in models]}
    except Exception as e:
        return {"error": str(e)}


@app.get("/health")
def health():
    return {"status": "healthy", "documents_loaded": len(document_store)}


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)