from fastapi import FastAPI
from app.api.routes.root import router as root_router
from app.api.routes.health import router as health_router 

app = FastAPI(
    title = "RAG",
    version = "1.0.0"
)

app.include_router(root_router)
app.include_router(health_router)

# @app.get("/")
# def root():
#     return {
#         "message" : "RAG API is working fine."
#     }

