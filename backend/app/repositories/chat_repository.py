from sqlalchemy.orm import Session
from app.models.chat import Chat

class ChatRepository:
    def create_chat(self, db: Session, question: str, answer: str, grounded: bool, retrieved_sources: str):
        db_chat = Chat(
            question=question,
            answer=answer,
            grounded=grounded,
            retrieved_sources=retrieved_sources
        )
        db.add(db_chat)
        db.commit()
        db.refresh(db_chat)
        return db_chat

    def get_chats(self, db: Session):
        return db.query(Chat).order_by(Chat.timestamp.desc()).all()

    def get_recent_chats(self, db: Session, limit: int = 5):
        return db.query(Chat).order_by(Chat.timestamp.desc()).limit(limit).all()
