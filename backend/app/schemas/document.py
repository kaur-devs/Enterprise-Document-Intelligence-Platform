from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentBase(BaseModel):
    name: str
    filepath: str
    type: str
    size: int
    content_hash: str

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(BaseModel):
    id: int
    name: str
    filepath: str
    type: str
    size: int
    upload_time: datetime
    chunk_count: int
    status: str
    content_hash: str

    class Config:
        from_attributes = True

class DuplicateCheckResponse(BaseModel):
    status: str
    message: str
    existing_document: Optional[DocumentResponse] = None