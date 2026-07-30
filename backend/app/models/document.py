from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    chunk_count = Column(Integer, default=0)
    status = Column(String, default="uploaded")
    content_hash = Column(String, index=True, nullable=False)