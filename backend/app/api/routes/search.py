from fastapi import APIRouter, Depends
from app.schemas.chat import SearchRequest, SearchResponse
from app.services.chat_service import ChatService

router = APIRouter(
    tags=["Search"]
)

service = ChatService()

@router.post("/search", response_model=SearchResponse)
def search_documents(request: SearchRequest):
    return service.search_semantic(request.query, request.document_ids)
