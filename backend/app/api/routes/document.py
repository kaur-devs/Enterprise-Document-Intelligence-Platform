import os
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.document import DocumentResponse, DuplicateCheckResponse
from app.services.document_service import DocumentService
from app.core import config

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

service = DocumentService()
SUPPORTED_FORMATS = {".pdf", ".docx", ".doc", ".txt", ".md", ".markdown"}

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    override: bool = Form(False),
    db: Session = Depends(get_db)
):
    _, ext = os.path.splitext(file.filename or "")
    if ext.lower() not in SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail="Unsupported file format.")
    
    file_bytes = await file.read()
    max_bytes = config.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum size limit of {config.MAX_UPLOAD_SIZE_MB}MB.")
    
    status, msg, doc = service.upload_document(db, file.filename or "", file_bytes, override)
    
    if status == "exact_duplicate":
        raise HTTPException(status_code=409, detail={
            "status": "exact_duplicate",
            "message": msg,
            "existing_document": DocumentResponse.model_validate(doc) if doc else None
        })
    
    if status == "likely_duplicate":
        return {
            "status": "likely_duplicate",
            "message": msg,
            "existing_document": DocumentResponse.model_validate(doc) if doc else None
        }
    
    if doc:
        background_tasks.add_task(service.process_document_pipeline, doc.id)
        return {
            "status": "success",
            "message": msg,
            "document": DocumentResponse.model_validate(doc)
        }
    raise HTTPException(status_code=500, detail="Failed to upload document.")

@router.get("/", response_model=List[DocumentResponse])
def get_documents(db: Session = Depends(get_db)):
    docs = service.repository.get_documents(db)
    return docs

@router.delete("/{id}")
def delete_document(id: int, db: Session = Depends(get_db)):
    try:
        success = service.delete_document(db, id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found.")
        return {"status": "success", "message": "Document deleted successfully."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
