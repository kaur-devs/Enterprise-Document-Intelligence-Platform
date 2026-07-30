from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from app.database.database import Base

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    grounded = Column(Boolean, default=False)
    retrieved_sources = Column(String, nullable=True)
