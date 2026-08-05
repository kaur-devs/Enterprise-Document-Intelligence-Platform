import time
from typing import List, Tuple, Optional
from langchain_core.documents import Document
from app.rag.vectorstore import get_vector_store
from app.core import config

class DocumentRetriever:
    def __init__(self):
        self.store = get_vector_store()
        self.threshold = config.SIMILARITY_THRESHOLD

    def retrieve_relevant_chunks(
        self,
        query: str,
        document_ids: Optional[List[int]] = None,
        top_k: int = 5,
        apply_threshold: bool = True,
    ) -> Tuple[List[Tuple[Document, float]], dict]:
        filter_dict = None
        if document_ids:
            if len(document_ids) == 1:
                filter_dict = {"document_id": str(document_ids[0])}
            else:
                filter_dict = {"document_id": {"$in": [str(d) for d in document_ids]}}

        embed_start = time.perf_counter()
        query_embedding = self.store._embedding_function.embed_query(query)
        embed_ms = (time.perf_counter() - embed_start) * 1000

        retrieval_start = time.perf_counter()
        results = self.store.similarity_search_by_vector_with_relevance_scores(
            query_embedding, k=top_k, filter=filter_dict
        )
        retrieval_ms = (time.perf_counter() - retrieval_start) * 1000

        relevant_results = []
        for doc, distance in results:
            similarity = 1.0 - distance
            if not apply_threshold or similarity >= self.threshold:
                relevant_results.append((doc, similarity))

        return relevant_results, {"embed_ms": embed_ms, "retrieval_ms": retrieval_ms}
