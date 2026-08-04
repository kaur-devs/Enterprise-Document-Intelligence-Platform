from pydantic import BaseModel
from datetime import datetime
from typing import List

class RecentChatItem(BaseModel):
    id: int
    question: str
    timestamp: datetime
    grounded: bool

    class Config:
        from_attributes = True

class DashboardResponse(BaseModel):
    total_documents: int
    total_chunks: int
    total_storage_bytes: int
    recent_chats: List[RecentChatItem]
