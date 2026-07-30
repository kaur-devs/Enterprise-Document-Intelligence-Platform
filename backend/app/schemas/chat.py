from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class SourceCitation(BaseModel):
    document_id: int
    document_name: str
    page: int
    chunk_number: int

class ChatRequest(BaseModel):
    question: str
    document_ids: Optional[List[int]] = None

class ChatResponse(BaseModel):
    answer: str
    grounded: bool
    sources: List[SourceCitation]

class SearchRequest(BaseModel):
    query: str
    document_ids: Optional[List[int]] = None

class SearchResultChunk(BaseModel):
    content: str
    score: float
    source: SourceCitation

class SearchResponse(BaseModel):
    results: List[SearchResultChunk]

class ChatHistoryResponse(BaseModel):
    id: int
    question: str
    answer: str
    timestamp: datetime
    grounded: bool
    sources: List[SourceCitation]

    class Config:
        from_attributes = True
