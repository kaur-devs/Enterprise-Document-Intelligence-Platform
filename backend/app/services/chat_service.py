import json
import logging
import time
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core import config
from app.rag.retriever import DocumentRetriever
from app.rag.chain import QAChain
from app.repositories.chat_repository import ChatRepository
from app.schemas.chat import ChatResponse, SourceCitation, SearchResponse, SearchResultChunk

logger = logging.getLogger("chat_service")

class ChatService:
    def __init__(self):
        self.retriever = DocumentRetriever()
        self.chain = QAChain()
        self.repository = ChatRepository()

    def chat_with_docs(self, db: Session, question: str, document_ids: Optional[List[int]] = None) -> ChatResponse:
        request_start = time.perf_counter()
        chunks_with_scores, retrieval_timings = self.retriever.retrieve_relevant_chunks(question, document_ids)
        try:
            answer, grounded, chain_timings = self.chain.generate_answer(question, chunks_with_scores)
        except Exception as e:
            logger.error(f"Gemini API invocation failed: {e}. Question: {question}")
            raise e

        serialize_start = time.perf_counter()
        citations = []
        seen = set()
        for doc, score in chunks_with_scores:
            doc_id = int(doc.metadata.get("document_id", 0))
            page_val = int(doc.metadata.get("page", 0)) + 1
            chunk_num = int(doc.metadata.get("chunk_number", 0))
            doc_name = doc.metadata.get("document_name", "Unknown")
            citation_key = (doc_id, page_val, chunk_num)
            if citation_key not in seen:
                seen.add(citation_key)
                citations.append(SourceCitation(
                    document_id=doc_id,
                    document_name=doc_name,
                    page=page_val,
                    chunk_number=chunk_num
                ))
        if not grounded:
            citations = []
        sources_data = [c.model_dump() for c in citations]
        sources_str = json.dumps(sources_data)
        self.repository.create_chat(db, question, answer, grounded, sources_str)
        response = ChatResponse(answer=answer, grounded=grounded, sources=citations)
        serialize_ms = (time.perf_counter() - serialize_start) * 1000
        total_ms = (time.perf_counter() - request_start) * 1000

        logger.info(
            "chat latency (ms): embed=%.0f retrieval=%.0f prompt=%.0f generation=%.0f serialize=%.0f total=%.0f",
            retrieval_timings["embed_ms"], retrieval_timings["retrieval_ms"],
            chain_timings["prompt_ms"], chain_timings["generation_ms"], serialize_ms, total_ms,
        )
        if total_ms > config.CHAT_LATENCY_BUDGET_MS:
            logger.warning(
                "Chat request exceeded %dms latency budget: %.0fms (question=%r)",
                config.CHAT_LATENCY_BUDGET_MS, total_ms, question,
            )
        return response

    def search_semantic(self, query: str, document_ids: Optional[List[int]] = None) -> SearchResponse:
        request_start = time.perf_counter()
        chunks_with_scores, retrieval_timings = self.retriever.retrieve_relevant_chunks(
            query, document_ids, top_k=10, apply_threshold=False
        )
        results = []
        for doc, score in chunks_with_scores:
            doc_id = int(doc.metadata.get("document_id", 0))
            page_val = int(doc.metadata.get("page", 0)) + 1
            chunk_num = int(doc.metadata.get("chunk_number", 0))
            doc_name = doc.metadata.get("document_name", "Unknown")
            citation = SourceCitation(
                document_id=doc_id,
                document_name=doc_name,
                page=page_val,
                chunk_number=chunk_num
            )
            results.append(SearchResultChunk(
                content=doc.page_content,
                score=score,
                source=citation
            ))
        total_ms = (time.perf_counter() - request_start) * 1000

        logger.info(
            "search latency (ms): embed=%.0f retrieval=%.0f total=%.0f",
            retrieval_timings["embed_ms"], retrieval_timings["retrieval_ms"], total_ms,
        )
        if total_ms > config.SEARCH_LATENCY_BUDGET_MS:
            logger.warning(
                "Search request exceeded %dms latency budget: %.0fms (query=%r)",
                config.SEARCH_LATENCY_BUDGET_MS, total_ms, query,
            )
        return SearchResponse(results=results)

    def get_chat_history(self, db: Session):
        db_chats = self.repository.get_chats(db)
        history = []
        for c in db_chats:
            citations = []
            if c.retrieved_sources:
                try:
                    raw_sources = json.loads(c.retrieved_sources)
                    for item in raw_sources:
                        citations.append(SourceCitation(**item))
                except Exception:
                    pass
            history.append({
                "id": c.id,
                "question": c.question,
                "answer": c.answer,
                "timestamp": c.timestamp,
                "grounded": c.grounded,
                "sources": citations
            })
        return history
