from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.document import Document
from app.schemas.document import DocumentCreate

class DocumentRepository:
    def create_document(self, db: Session, document: DocumentCreate):
        db_document = Document(
            name=document.name,
            filepath=document.filepath,
            type=document.type,
            size=document.size,
            content_hash=document.content_hash,
            status="uploaded",
            chunk_count=0
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document

    def get_document(self, db: Session, document_id: int):
        return db.query(Document).filter(Document.id == document_id).first()

    def get_documents(self, db: Session):
        return db.query(Document).all()

    def get_document_by_hash(self, db: Session, content_hash: str):
        return db.query(Document).filter(Document.content_hash == content_hash).first()

    def get_document_by_name_and_size(self, db: Session, name: str, size: int):
        return db.query(Document).filter(Document.name == name, Document.size == size).first()

    def update_document_status(self, db: Session, document_id: int, status: str, chunk_count: int = None):
        db_document = self.get_document(db, document_id)
        if db_document:
            db_document.status = status
            if chunk_count is not None:
                db_document.chunk_count = chunk_count
            db.commit()
            db.refresh(db_document)
        return db_document

    def delete_document(self, db: Session, document_id: int):
        db_document = self.get_document(db, document_id)
        if db_document:
            db.delete(db_document)
            db.commit()
            return True
        return False

    def get_document_stats(self, db: Session):
        total_documents = db.query(func.count(Document.id)).scalar() or 0
        total_chunks = db.query(func.sum(Document.chunk_count)).scalar() or 0
        total_storage_bytes = db.query(func.sum(Document.size)).scalar() or 0
        return {
            "total_documents": total_documents,
            "total_chunks": total_chunks,
            "total_storage_bytes": total_storage_bytes,
        }