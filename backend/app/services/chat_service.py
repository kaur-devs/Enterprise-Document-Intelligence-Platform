import json
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
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
        chunks_with_scores = self.retriever.retrieve_relevant_chunks(question, document_ids)
        try:
            answer, grounded = self.chain.generate_answer(question, chunks_with_scores)
        except Exception as e:
            logger.error(f"Gemini API invocation failed: {e}. Question: {question}")
            raise e
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
        return ChatResponse(
            answer=answer,
            grounded=grounded,
            sources=citations
        )

    def search_semantic(self, query: str, document_ids: Optional[List[int]] = None) -> SearchResponse:
        chunks_with_scores = self.retriever.retrieve_relevant_chunks(query, document_ids, top_k=10)
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
