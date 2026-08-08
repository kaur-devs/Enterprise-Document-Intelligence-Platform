# KnowledgeHub AI

A document intelligence platform: upload PDFs, DOCX, TXT, or Markdown files and query them through a grounded RAG chat or semantic search — with source citations and a hard guarantee against hallucinated answers.

Built with FastAPI, LangChain, Google Gemini, ChromaDB, and React.

## Why this exists

Most "chat with your PDF" projects skip the parts that make retrieval actually trustworthy: what happens when nothing relevant is found, how duplicates are handled, what a chunk boundary should respect, how failures get surfaced instead of swallowed. This project is built around those decisions — see [docs/PRD.md](docs/PRD.md) for the full feature list and what's still open, and [docs/SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md) for the architecture and the reasoning behind the non-obvious choices.

## Key features

- **Grounded chat, not a guessing machine** — if no chunk clears the similarity threshold, the system says so instead of letting the LLM answer from general knowledge
- **Source citations** on every grounded answer (document, page, chunk)
- **Document-scoped chat and search** — restrict retrieval to specific uploaded documents
- **Format-aware chunking** — PDF chunks never cross page boundaries; DOCX and Markdown are split along heading structure, not blind character windows
- **Two-stage duplicate detection** — filename+size match (overridable) and SHA-256 content hash (hard block)
- **Re-indexing** — reprocess a document without re-uploading it
- **Per-request latency instrumentation** — every chat/search call logs an embed/retrieval/generation/serialize breakdown and flags budget overruns
- **A live dashboard** of document/chunk/storage stats and recent chats

## Tech stack

| Layer | Choice |
|---|---|
| Backend | Python, FastAPI |
| RAG orchestration | LangChain |
| LLM | Google Gemini |
| Vector store | ChromaDB (persistent) |
| Relational store | SQLite |
| Frontend | React + Vite |

## Project structure

```
RAG/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # HTTP layer
│   │   ├── services/        # orchestration
│   │   ├── rag/              # loader, splitter, embeddings, vectorstore, retriever, chain
│   │   ├── repositories/     # SQL access
│   │   ├── schemas/          # Pydantic models
│   │   └── models/           # SQLAlchemy models
│   └── main.py
├── frontend/
│   └── src/
│       ├── components/       # Dashboard, KnowledgeBase, Chat, Search
│       └── api.js
└── docs/
    ├── PRD.md                # feature status tracker (what's done vs. remaining)
    ├── SRS.md                 # functional/non-functional requirements
    ├── SYSTEM_DESIGN.md       # architecture, sequence diagrams, key decisions
    ├── WIREFRAMES.md          # UI layout reference
    └── openapi.json           # auto-generated API spec
```

## Setup

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
```

Add your key to `backend/.env`:

```
GOOGLE_API_KEY=your_key_here
```

Get a free key at [Google AI Studio](https://aistudio.google.com). All other config values (chunk size, similarity threshold, model names, latency budgets) have sensible defaults in `.env` — see [docs/SRS.md](docs/SRS.md) for what each one controls.

Run it:

```bash
python -m uvicorn main:app --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:5173`.

## Docs

- [docs/PRD.md](docs/PRD.md) — what's built, what's not, and why
- [docs/SRS.md](docs/SRS.md) — formal requirements
- [docs/SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md) — architecture and design decisions
- [docs/WIREFRAMES.md](docs/WIREFRAMES.md) — UI layout reference
- [docs/openapi.json](docs/openapi.json) — API spec (regenerate with `curl localhost:8000/openapi.json`)
