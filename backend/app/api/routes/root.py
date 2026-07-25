from fastapi import APIRouter 

router = APIRouter(
    tags = ["Root"]
)

@router.get("/")
def root():
    return {
        "message" : "RAG API is working fine"
    }