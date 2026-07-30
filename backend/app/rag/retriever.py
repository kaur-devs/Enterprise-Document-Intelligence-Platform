from typing import List, Tuple, Optional
from langchain_core.documents import Document
from app.rag.vectorstore import get_vector_store
from app.core import config

class DocumentRetriever:
    def __init__(self):
        self.store = get_vector_store()
        self.threshold = config.SIMILARITY_THRESHOLD

    def retrieve_relevant_chunks(
        self, query: str, document_ids: Optional[List[int]] = None, top_k: int = 5
    ) -> List[Tuple[Document, float]]:
        filter_dict = None
        if document_ids:
            if len(document_ids) == 1:
                filter_dict = {"document_id": str(document_ids[0])}
            else:
                filter_dict = {"document_id": {"$in": [str(d) for d in document_ids]}}
        results = self.store.similarity_search_with_score(query, k=top_k, filter=filter_dict)
        relevant_results = []
        for doc, distance in results:
            similarity = 1.0 - distance
            if similarity >= self.threshold:
                relevant_results.append((doc, similarity))
        return relevant_results
