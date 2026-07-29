from fastapi import APIRouter , Depends 
from fastapi import UploadFile, File

from sqlalchemy.orm import Session
from app.database.database import get_db 
from app.schemas.document import DocumentCreate , DocumentResponse
from app.services.document_service import DocumentService

router = APIRouter(
    prefix = "/documents",
    tags = ["Documents"]
)

service = DocumentService()

@router.post("/",response_model=DocumentResponse)
def create_document(document:DocumentCreate,db:Session=Depends(get_db)):
    return service.create_document(db,document)

@router.post("/upload", response_model=UploadResponse)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return service.upload_document(db, file)

