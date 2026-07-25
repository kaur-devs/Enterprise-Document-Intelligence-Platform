from sqlalchemy.orm import Session
from app.models.document import Document 
from app.schemas.document import DocumentCreate

class DocumentRepository:

    def create_document(self,db:Session,document:DocumentCreate):
        db_document = Document(
            filename = document.filename,
            filepath = document.filepath
        )

        db.add(db_document)
        db.commit()
        db.refresh(db_document)

        return db_document