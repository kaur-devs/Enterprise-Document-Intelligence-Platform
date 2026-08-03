import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse
from app.services.chat_service import ChatService
from app.rag.chain import LLMGenerationError

logger = logging.getLogger("chat_route")

router = APIRouter(
    tags=["Chat"]
)

service = ChatService()

@router.post("/chat", response_model=ChatResponse)
def ask_question(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        response = service.chat_with_docs(db, request.question, request.document_ids)
        return response
    except LLMGenerationError:
        raise HTTPException(
            status_code=503,
            detail="Gemini API is temporarily unavailable or timed out. Please try again."
        )
    except Exception as e:
        logger.exception(f"Unexpected error handling chat question '{request.question}': {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")

@router.get("/history", response_model=List[ChatHistoryResponse])
def get_history(db: Session = Depends(get_db)):
    return service.get_chat_history(db)
