from sqlalchemy import Column,Integer,String,DateTime 
from datetime import datetime
from app.database.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer,primary_key=True,index=True)
    filename = Column(String,nullable=False)
    filepath = Column(String,nullable=False)
    status = Column(String,default="uploaded")
    created_at = Column(DateTime,default=datetime.utcnow)