import os
import chromadb
from langchain_chroma import Chroma
from app.core import config
from app.rag.embeddings import get_embeddings

class VectorStoreManager:
    def __init__(self):
        self.persist_dir = config.CHROMA_PERSIST_DIRECTORY
        os.makedirs(self.persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection_name = "knowledgehub"
        self._initialize_collection()

    def _initialize_collection(self):
        collections = self.client.list_collections()
        collection_names = [c.name for c in collections]
        if self.collection_name in collection_names:
            collection = self.client.get_collection(self.collection_name)
            meta = collection.metadata or {}
            existing_model = meta.get("embedding_model")
            existing_dimension = meta.get("dimension")
            if existing_model != config.EMBEDDING_MODEL or existing_dimension != config.EMBEDDING_DIMENSION:
                raise ValueError(
                    f"Embedding model mismatch! Configured: {config.EMBEDDING_MODEL} ({config.EMBEDDING_DIMENSION}), "
                    f"Found: {existing_model} ({existing_dimension}). "
                    "A full re-index is required to change embedding models."
                )
        else:
            self.client.create_collection(
                name=self.collection_name,
                metadata={
                    "embedding_model": config.EMBEDDING_MODEL,
                    "dimension": config.EMBEDDING_DIMENSION,
                    "hnsw:space": "cosine"
                }
            )

def get_vector_store():
    VectorStoreManager()
    return Chroma(
        collection_name="knowledgehub",
        persist_directory=config.CHROMA_PERSIST_DIRECTORY,
        embedding_function=get_embeddings()
    )
