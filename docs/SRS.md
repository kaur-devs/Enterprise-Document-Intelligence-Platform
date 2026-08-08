# Software Requirements Specification — KnowledgeHub AI

## 1. Purpose

This document specifies the functional and non-functional requirements for KnowledgeHub AI, a document intelligence platform combining document ingestion, semantic search, and Retrieval-Augmented Generation (RAG) chat. It reflects what is actually implemented, not an aspirational spec — see [PRD.md](PRD.md) for feature status tracking.

## 2. Scope

The system allows a single user to upload documents (PDF, DOCX, TXT, Markdown), have them chunked and embedded into a persistent vector store, and then query them through two interfaces: a grounded chat that cites sources and refuses to answer outside the retrieved context, and a semantic search that surfaces ranked results by meaning. Multi-user auth, hybrid search, and agentic workflows are explicitly out of scope for this version (see PRD §2.7).

## 3. Functional Requirements

| ID | Requirement | Implemented in |
|---|---|---|
| FR-1 | System shall accept PDF, DOCX, TXT, Markdown uploads and reject other formats before processing | `api/routes/document.py` |
| FR-2 | System shall reject uploads exceeding a configurable max size | `api/routes/document.py`, `core/config.py` |
| FR-3 | System shall detect exact duplicates via SHA-256 content hash and block them | `services/document_service.py` |
| FR-4 | System shall detect likely duplicates (same name + size) and require explicit override to proceed | `services/document_service.py` |
| FR-5 | System shall split PDF content without crossing page boundaries, preserving accurate page metadata per chunk | `rag/loader.py`, `rag/splitter.py` |
| FR-6 | System shall split DOCX content along heading structure (Heading 1–3) | `rag/loader.py`, `rag/splitter.py` |
| FR-7 | System shall split Markdown content along header structure | `rag/splitter.py` |
| FR-8 | System shall track per-document pipeline status (`uploaded → loaded → split → embedded → indexed`, or `failed`) | `repositories/document_repository.py` |
| FR-9 | System shall allow deleting a document, removing its vectors, database row, and file from disk | `services/document_service.py` |
| FR-10 | System shall allow re-indexing a document (clear + reprocess) without re-uploading | `services/document_service.py`, `api/routes/document.py` |
| FR-11 | System shall answer chat questions using only retrieved context, never general LLM knowledge | `rag/chain.py` |
| FR-12 | System shall return a fixed fallback response and `grounded: false` when no chunk clears the similarity threshold | `rag/chain.py`, `rag/retriever.py` |
| FR-13 | System shall cite document name, page, and chunk number for every grounded answer | `services/chat_service.py` |
| FR-14 | System shall allow scoping a chat query to a subset of documents | `api/routes/chat.py`, `rag/retriever.py` |
| FR-15 | System shall persist chat history and expose it for retrieval | `repositories/chat_repository.py` |
| FR-16 | System shall provide semantic search returning ranked results with similarity scores, independent of the chat grounding threshold | `services/chat_service.py`, `rag/retriever.py` |
| FR-17 | System shall report document count, chunk count, storage used, and recent chats on a dashboard | `services/dashboard_service.py` |
| FR-18 | System shall report the reachability of the database, vector store, and LLM provider | `api/routes/health.py` |

## 4. Non-Functional Requirements

| ID | Requirement | Status |
|---|---|---|
| NFR-1 | Chat responses should complete within 5s end-to-end under normal load | Instrumented and logged per-request (embed/retrieval/prompt/generation/serialize breakdown); not load-tested at scale |
| NFR-2 | Search responses should complete within 1s end-to-end | Instrumented and logged per-request; not load-tested at scale |
| NFR-3 | Vector embeddings must persist across application restarts | Chroma configured in persistent mode |
| NFR-4 | The system must never silently swallow a failure — errors are logged with enough context to diagnose | Enforced across ingestion, deletion, and chat pipelines |
| NFR-5 | Tunable parameters (thresholds, chunk size, model names, latency budgets) must be environment-configurable, not hardcoded | Enforced via `core/config.py` |
| NFR-6 | The embedding model in use must be pinned and checked against the existing vector store at startup, failing loudly on mismatch | `rag/vectorstore.py` |
| NFR-7 | The system should support 100+ documents | Untested at that scale |

## 5. Constraints

- Single-user system; no authentication in v1 (see PRD §2.7)
- Local filesystem storage for uploaded files; local SQLite for relational data; local persistent ChromaDB for vectors — no cloud storage or managed DB in v1
- Dependent on Google's Gemini API for both embeddings and generation — model availability is externally controlled and has already required two model-name migrations during development (see PRD §7, live-test log)

## 6. Assumptions

- The user has a valid Google AI Studio API key with access to Gemini embedding and generation models
- Uploaded documents are text-based (scanned/image-only PDFs are not OCR'd)
- `.doc` (legacy binary Word format) is accepted at the upload-validation layer but is not actually parseable by the current DOCX loader (`python-docx` only supports the `.docx` XML format) — a known, pre-existing gap, not fixed in v1
