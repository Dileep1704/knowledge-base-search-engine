# 🔍 Knowledge Base Search Engine

A **Retrieval-Augmented Generation (RAG)** powered knowledge base search engine that lets you upload documents and ask natural language questions — getting synthesized, cited answers from Claude (Anthropic).

---

## 📸 Demo

> Upload `.txt`, `.md`, `.pdf`, `.csv`, or `.json` files → Ask questions → Get LLM-synthesized answers with source attribution.

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────────┐
│   Frontend UI   │  ← Drag & drop upload, chat interface
│  (index.html)   │
└────────┬────────┘
         │ HTTP / Direct API
         ▼
┌─────────────────┐
│  Backend API    │  ← FastAPI (Python) — optional
│  (server.py)    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         RAG Pipeline                    │
│                                         │
│  1. RETRIEVAL: Score & rank documents   │
│     by query relevance                  │
│                                         │
│  2. AUGMENTATION: Inject top-k chunks   │
│     into LLM system prompt             │
│                                         │
│  3. GENERATION: Claude synthesizes      │
│     answer from document context        │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Anthropic API  │  ← claude-sonnet-4-20250514
│  (Claude LLM)   │
└─────────────────┘
```

---

## 🚀 Quick Start

### Option A: Frontend Only (No Setup Required)

1. Open `frontend/index.html` in your browser
2. Enter your [Anthropic API key](https://console.anthropic.com/)
3. Upload documents from `sample-docs/` or your own files
4. Ask questions!

### Option B: Full Stack (Frontend + Backend API)

#### Prerequisites
- Python 3.9+
- Anthropic API key from [console.anthropic.com](https://console.anthropic.com/)

#### Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/knowledge-base-search-engine
cd knowledge-base-search-engine

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Set your API key
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Start the backend server
python server.py
# Server runs at http://localhost:8000
```

Open `frontend/index.html` in your browser. The frontend can work standalone (direct API) or connect to the backend.

---

## 📁 Project Structure

```
knowledge-base-search-engine/
├── frontend/
│   └── index.html          # Complete UI — drag & drop upload, chat interface
├── backend/
│   ├── server.py           # FastAPI backend with RAG pipeline
│   └── requirements.txt    # Python dependencies
├── sample-docs/
│   ├── artificial_intelligence.txt
│   └── climate_change.txt
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ingest` | Upload a document |
| `GET` | `/documents` | List all documents |
| `DELETE` | `/documents/{name}` | Remove a document |
| `POST` | `/query` | Ask a question (RAG query) |
| `GET` | `/health` | Health check |

### Example: Query via cURL

```bash
# Upload a document
curl -X POST http://localhost:8000/ingest \
  -F "file=@sample-docs/artificial_intelligence.txt"

# Ask a question
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main applications of AI?"}'
```

### Example Response

```json
{
  "answer": "According to the AI overview document, the main applications of AI include: Healthcare (disease diagnosis, drug discovery), Finance (fraud detection, algorithmic trading), Transportation (self-driving cars), Education (personalized learning), and Retail (product recommendations).",
  "sources": ["artificial_intelligence.txt"],
  "model": "claude-sonnet-4-20250514"
}
```

---

## ⚙️ RAG Pipeline Details

### Retrieval
The current implementation uses **keyword frequency scoring** to rank documents by relevance to the query. For production use, upgrade to:
- **Embeddings**: Use `text-embedding-3-small` (OpenAI) or similar to embed chunks
- **Vector Store**: Store embeddings in [Chroma](https://www.trychroma.com/), [Pinecone](https://www.pinecone.io/), or [Weaviate](https://weaviate.io/)
- **Semantic Search**: Retrieve top-k chunks by cosine similarity

### Augmentation
Top-k retrieved document chunks (up to 8,000 chars each) are injected into Claude's system prompt.

### Generation (LLM Prompt)
```
"You are a precise knowledge-base search assistant using RAG. 
Answer the user's question using ONLY the provided document context. 
Be concise but thorough. Always mention which document(s) you drew from."
```

---

## 🛠️ Supported File Types

| Extension | Notes |
|-----------|-------|
| `.txt` | Plain text — fully supported |
| `.md` | Markdown — fully supported |
| `.csv` | CSV data — read as text |
| `.json` | JSON data — read as text |
| `.pdf` | Requires `pypdf` for text extraction |

---

## 🔐 API Key Security

- **Frontend mode**: Key is entered in the UI and stored in memory only — never persisted
- **Backend mode**: Key is loaded from the `ANTHROPIC_API_KEY` environment variable — never exposed to the frontend

---

## 📈 Upgrade Path

| Feature | Current | Production Upgrade |
|---------|---------|-------------------|
| Retrieval | Keyword scoring | Embeddings + vector DB |
| Storage | In-memory | PostgreSQL / S3 |
| Chunking | Full document | Sliding window chunking |
| PDF parsing | Basic | `pymupdf` / `pdfplumber` |
| Auth | None | JWT / OAuth |

---

## 📝 License

MIT License — free to use and modify.

---

## 🙏 Built With

- [Anthropic Claude](https://anthropic.com) — LLM for answer synthesis
- [FastAPI](https://fastapi.tiangolo.com/) — Backend API framework
- Vanilla HTML/CSS/JS — Zero-dependency frontend
