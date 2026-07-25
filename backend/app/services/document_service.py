from sqlalchemy.orm import Session 
from app.schemas.document import DocumentCreate
from app.repositories.document_repository import DocumentRepository

class DocumentService:

    def __init__(self):
        self.repository = DocumentRepository()

    def create_document(self,db:Session,document:DocumentCreate):
        return self.repository.create_document(db,document)