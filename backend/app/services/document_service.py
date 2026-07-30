import os
import hashlib
from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.core import config
from app.database.database import SessionLocal
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentCreate
from app.rag.loader import DocumentLoader
from app.rag.splitter import DocumentSplitter
from app.rag.vectorstore import get_vector_store

class DocumentService:
    def __init__(self):
        self.repository = DocumentRepository()
        self.loader = DocumentLoader()
        self.splitter = DocumentSplitter()
        self.vector_store = get_vector_store()
        os.makedirs(config.UPLOAD_DIR, exist_ok=True)

    def check_duplicate(self, db: Session, filename: str, file_size: int, content_hash: str) -> Tuple[str, Optional[object]]:
        exact_duplicate = self.repository.get_document_by_hash(db, content_hash)
        if exact_duplicate:
            return "exact_duplicate", exact_duplicate
        likely_duplicate = self.repository.get_document_by_name_and_size(db, filename, file_size)
        if likely_duplicate:
            return "likely_duplicate", likely_duplicate
        return "clean", None

    def upload_document(self, db: Session, filename: str, file_bytes: bytes, override: bool = False) -> Tuple[str, str, Optional[object]]:
        content_hash = hashlib.sha256(file_bytes).hexdigest()
        file_size = len(file_bytes)
        status, existing_doc = self.check_duplicate(db, filename, file_size, content_hash)
        if status == "exact_duplicate":
            return "exact_duplicate", "Document with identical content already exists.", existing_doc
        if status == "likely_duplicate" and not override:
            return "likely_duplicate", "A file with the same name and size already exists.", existing_doc
        
        filepath = os.path.join(config.UPLOAD_DIR, f"{content_hash}_{filename}")
        with open(filepath, "wb") as f:
            f.write(file_bytes)
        
        _, ext = os.path.splitext(filename)
        doc_type = ext.lstrip(".").lower()
        
        doc_in = DocumentCreate(
            name=filename,
            filepath=filepath,
            type=doc_type,
            size=file_size,
            content_hash=content_hash
        )
        db_doc = self.repository.create_document(db, doc_in)
        return "success", "Document uploaded successfully.", db_doc

    def process_document_pipeline(self, doc_id: int):
        db = SessionLocal()
        try:
            db_doc = self.repository.get_document(db, doc_id)
            if not db_doc:
                return
            
            self.repository.update_document_status(db, doc_id, "loaded")
            raw_docs = self.loader.load_document(db_doc.filepath, db_doc.type)
            
            self.repository.update_document_status(db, doc_id, "split")
            chunks = self.splitter.split_documents(raw_docs, db_doc.type)
            
            self.repository.update_document_status(db, doc_id, "embedded")
            texts = [chunk.page_content for chunk in chunks]
            metadatas = []
            for i, chunk in enumerate(chunks):
                page_val = chunk.metadata.get("page", 0)
                metadatas.append({
                    "document_id": str(doc_id),
                    "document_name": db_doc.name,
                    "page": int(page_val),
                    "chunk_number": i,
                    "upload_time": db_doc.upload_time.isoformat(),
                    "file_type": db_doc.type
                })
            
            self.vector_store.add_texts(texts=texts, metadatas=metadatas)
            self.repository.update_document_status(db, doc_id, "indexed", chunk_count=len(chunks))
        except Exception as e:
            self.repository.update_document_status(db, doc_id, "failed")
        finally:
            db.close()

    def delete_document(self, db: Session, doc_id: int) -> bool:
        db_doc = self.repository.get_document(db, doc_id)
        if not db_doc:
            return False
        
        try:
            self.vector_store.delete(where={"document_id": str(doc_id)})
        except Exception as e:
            raise e
        
        db_success = False
        fs_success = False
        try:
            db_success = self.repository.delete_document(db, doc_id)
        except Exception as e:
            pass
            
        try:
            if os.path.exists(db_doc.filepath):
                os.remove(db_doc.filepath)
            fs_success = True
        except Exception as e:
            pass
            
        if not db_success or not fs_success:
            if not db_success:
                self.repository.update_document_status(db, doc_id, "failed_cleanup")
            raise RuntimeError("Cleanup failed for some components. Orphaned metadata remains.")
            
        return True