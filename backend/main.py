import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.root import router as root_router
from app.api.routes.health import router as health_router 
from app.api.routes.document import router as document_router
from app.api.routes.chat import router as chat_router
from app.api.routes.search import router as search_router
from app.database.database import Base, engine
from app.models.document import Document
from app.models.chat import Chat

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="KnowledgeHub AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(root_router)
app.include_router(health_router)
app.include_router(document_router)
app.include_router(chat_router)
app.include_router(search_router)


