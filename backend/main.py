from fastapi import FastAPI
from app.api.routes.root import router as root_router
from app.api.routes.health import router as health_router 
from app.api.routes.document import router as document_router
from app.database.database import Base, engine
from app.models.document import Document 

app = FastAPI(
    title = "RAG",
    version = "1.0.0"
)

Base.metadata.create_all(bind=engine)

app.include_router(root_router)
app.include_router(health_router)
app.include_router(document_router)

# @app.get("/")
# def root():
#     return {
#         "message" : "RAG API is working fine."
#     }

