# KnowledgeHub AI — Product Requirements Document (v1.3, implementation-tracked)

> This supersedes the original pasted PRD for day-to-day use. It reflects what's actually in the codebase, what bugs were fixed, and what's left to build for a complete v1. Status legend: ✅ Done · 🔧 To build · ⚠️ Partial/needs rework.

## 1. What this project is

An enterprise-style document intelligence platform: upload documents, they get chunked and embedded into a vector store, and you can chat with or semantically search across them — with source citations and a hard guarantee against hallucinated answers (no relevant chunks → no answer, not a guess).

## 2. Feature list (v1 scope)

### 2.1 Document ingestion
- ✅ Upload PDF / DOCX / TXT / Markdown with extension + max-size validation
- ✅ Duplicate detection — filename+size ("likely duplicate", overridable) then SHA-256 content hash ("exact duplicate", blocked)
- ✅ Format-aware chunking — PDF is page-aware (PyPDFLoader loads per-page, chunks never cross page boundaries); DOCX is heading-aware (headings converted to Markdown-style headers via `python-docx`, then split through the same header-aware pipeline as Markdown)
- ✅ Chunk metadata: document_id, document_name, page, chunk_number, upload_time, file_type
- ✅ Pipeline status tracking per document: `uploaded → loaded → split → embedded → indexed`, with `failed` on error (logged with full traceback)

### 2.2 Knowledge base management
- ✅ List uploaded documents (`GET /documents`)
- ✅ Delete a document — removes vectors (Chroma), DB row, and file from disk; failure paths are logged instead of silently swallowed
- ✅ Re-index a document — clears existing vectors, resets status, re-runs the pipeline (`POST /documents/{id}/reindex`)
- ✅ Dashboard — total documents, total chunks/embeddings, storage used, recent chats (`GET /dashboard`, default landing view)

### 2.3 Chat (RAG)
- ✅ Full pipeline: question → retriever → relevant chunks → prompt → Gemini → answer
- ✅ Similarity threshold (0.72, configurable) — chunks below it are discarded
- ✅ Grounding guarantee — if no chunk clears the threshold, returns a fixed "couldn't find relevant information" response instead of letting the LLM guess; `grounded: bool` field on every response
- ✅ Hallucination guardrail in the system prompt
- ✅ Document-scoped chat — optional `document_ids` filter to restrict retrieval to specific docs
- ✅ Source citations on every grounded answer (document name, page, chunk number)
- ✅ Chat history stored and retrievable (`GET /history`)
- ✅ Gemini failures return 503 with a clear message; other bugs return 500 and get logged

### 2.4 Semantic search
- ✅ Separate `/search` endpoint — same retrieval, no generation step, returns chunks + similarity scores + source

### 2.5 Reliability / config
- ✅ `/health` reports Chroma and Gemini reachability
- ✅ Similarity threshold, chunk size/overlap, embedding model, Gemini model, max upload size — all environment-configurable
- ✅ Embedding model pinned (`text-embedding-004`) with a startup dimension check
- ✅ Per-stage latency instrumentation — chat logs embed/retrieval/prompt/generation/serialize/total per request; search logs embed/retrieval/total; both compare against configurable budgets (`CHAT_LATENCY_BUDGET_MS`, `SEARCH_LATENCY_BUDGET_MS`) and log a warning on overrun

### 2.6 Frontend
- ✅ React app wired to the full API surface: dashboard (stats + recent chats), upload (drag-drop, duplicate-override modal), chat (citations, grounded/ungrounded indicator, document scoping), search (ranked results with scores), knowledge base table (status badges, delete, re-index)

### 2.7 Explicitly out of scope for v1
- Authentication / multi-user accounts
- Hybrid search (BM25 + vector), query rewriting, reranking, near-duplicate detection
- Streaming chat responses
- Redis semantic caching
- Evaluation dashboard / automated eval suite
- Agents, LangGraph workflows, tool calling, multi-agent orchestration

## 3. Non-functional requirements
| Requirement | Status |
|---|---|
| Chat response < 5s end-to-end | Instrumented and logged per-request; not yet load-tested at scale |
| Search response < 1s end-to-end | Instrumented and logged per-request; not yet load-tested at scale |
| Handles 100+ documents | Untested at that scale |
| Embeddings persist across restart | ✅ Chroma persistent mode configured |
| Config externalized, not hardcoded | ✅ |
| Errors fail loudly, not silently | ✅ |

## 4. Bug-fix / build log
1. Document pipeline failures were swallowed with no logging → now logged with full traceback.
2. Document delete swallowed DB/filesystem errors → now logged; orphaned-file-on-disk case (DB row gone, file removal failed) now logs loudly since there's no dashboard yet to flag it against.
3. Chat endpoint reported every error as "Gemini unavailable" (503) → now only real Gemini failures return 503; everything else returns 500 and gets logged.
4. Gemini model name was hardcoded → now `GEMINI_MODEL` in config/`.env`.
5. Frontend built: Knowledge Base, Chat, Search views, all wired to the real backend.
6. Re-index endpoint added (`POST /documents/{id}/reindex`), wired into the frontend.
7. Dashboard endpoint (`GET /dashboard`) and view added — document/chunk/storage stats + recent chats.
8. DOCX loading switched from `docx2txt` to `python-docx`, converting heading styles to Markdown-style headers so DOCX now shares the header-aware splitting pipeline with Markdown. Verified PDF was already page-aware by design (PyPDFLoader's per-page documents never get merged across pages during splitting).
9. Latency instrumentation added: retrieval is split into separately-timed embed/retrieval stages, generation is split into prompt-construction/generation stages, and chat/search each log a full per-request breakdown plus a warning if the configurable budget is exceeded.

## 5. Tech stack (as built)
| Layer | Choice |
|---|---|
| Backend | Python, FastAPI |
| RAG orchestration | LangChain |
| LLM | Google Gemini (`gemini-1.5-flash`, configurable) |
| Embeddings | Google `text-embedding-004` (768-dim, pinned) |
| Vector store | ChromaDB (persistent mode) |
| Relational store | SQLite |
| Frontend | React + Vite |
| File storage | Local disk |

## 6. Remaining build order

All planned v1 work is complete. See §7 for the live-test bug log and the docs listed below for the rest of the documentation set.

Docs: [SRS.md](SRS.md) · [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) · [WIREFRAMES.md](WIREFRAMES.md) · [openapi.json](openapi.json) · root [README.md](../README.md)

## 7. Live end-to-end test (2026-08-04) — bugs found and fixed
Ran the full stack against a real `GOOGLE_API_KEY` for the first time. Three real bugs surfaced that no amount of mocking would have caught:
1. **`text-embedding-004` is retired.** Google's API returned 404. Switched to `gemini-embedding-001` with `output_dimensionality=768` (via `output_dimensionality` param) to keep the existing 768-dim Chroma collection design intact. The hardcoded `768` literal duplicated across `vectorstore.py` was also consolidated into a new `EMBEDDING_DIMENSION` config value.
2. **`gemini-1.5-flash` is retired**, and even `gemini-2.5-flash` came back "no longer available to new users" for this API key. Switched to `gemini-flash-latest`, Google's alias that stays pointed at the current recommended flash model — more resilient to this happening again. This also surfaced that `response.content` is a list of content blocks (not a plain string) on the newer model, which would have crashed `chain.py`'s `.strip()` call — added a small `_extract_text()` helper to handle both shapes.
3. **Search was silently reusing chat's grounding threshold (0.72).** A real 0.6948-similarity chunk was hidden from search results entirely. These are different concerns — chat's threshold exists to stop the LLM hallucinating; search should show ranked results regardless of score. Added an `apply_threshold` flag to `retrieve_relevant_chunks`, `True` for chat (unchanged behavior) and `False` for search (now returns real scores).

All three chat/search paths (grounded answer, no-answer fallback, citations, document-scoped search, dashboard live stats) were then re-verified against the real API and the actual browser UI — confirmed working correctly.

## 7. Resume description (once v1 above is complete)
> KnowledgeHub AI – Enterprise Document Intelligence Platform
> Built a production-style Retrieval-Augmented Generation platform (FastAPI, LangChain, Gemini, ChromaDB) with multi-format document ingestion, semantic chunking, persistent vector storage, grounded conversational QA with source citation, semantic search, and a React frontend — with explicit hallucination guarding (similarity-thresholded retrieval, fixed no-answer fallback) and failure-mode handling across the ingestion, deletion, and re-indexing pipelines.
