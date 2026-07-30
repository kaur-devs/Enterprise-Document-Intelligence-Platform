from fastapi import APIRouter, Depends, Response
from sqlalchemy import text
from sqlalchemy.orm import Session
import google.generativeai as genai
from app.database.database import get_db
from app.rag.vectorstore import get_vector_store
from app.core import config

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)

@router.get("/")
def health_check(response: Response, db: Session = Depends(get_db)):
    sqlite_status = "Healthy"
    chroma_status = "Healthy"
    gemini_status = "Healthy"
    try:
        db.execute(text("SELECT 1")).scalar()
    except Exception as e:
        sqlite_status = f"Unhealthy: {str(e)}"
    try:
        store = get_vector_store()
        store._client.heartbeat()
    except Exception as e:
        chroma_status = f"Unhealthy: {str(e)}"
    try:
        if not config.GOOGLE_API_KEY:
            gemini_status = "Unhealthy: GOOGLE_API_KEY environment variable is not configured."
        else:
            genai.configure(api_key=config.GOOGLE_API_KEY)
            genai.list_models()
    except Exception as e:
        gemini_status = f"Unhealthy: {str(e)}"
    is_healthy = sqlite_status == "Healthy" and chroma_status == "Healthy" and gemini_status == "Healthy"
    if not is_healthy:
        response.status_code = 503
    return {
        "status": "Healthy" if is_healthy else "Unhealthy",
        "details": {
            "database": sqlite_status,
            "vector_store": chroma_status,
            "gemini": gemini_status
        }
    }
