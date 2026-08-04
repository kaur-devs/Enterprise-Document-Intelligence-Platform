from sqlalchemy.orm import Session
from app.repositories.document_repository import DocumentRepository
from app.repositories.chat_repository import ChatRepository
from app.schemas.dashboard import DashboardResponse, RecentChatItem

class DashboardService:
    def __init__(self):
        self.document_repository = DocumentRepository()
        self.chat_repository = ChatRepository()

    def get_dashboard_data(self, db: Session) -> DashboardResponse:
        stats = self.document_repository.get_document_stats(db)
        recent_chats = self.chat_repository.get_recent_chats(db, limit=5)
        return DashboardResponse(
            total_documents=stats["total_documents"],
            total_chunks=stats["total_chunks"],
            total_storage_bytes=stats["total_storage_bytes"],
            recent_chats=[RecentChatItem.model_validate(chat) for chat in recent_chats],
        )
