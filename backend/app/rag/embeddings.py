from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core import config

def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        google_api_key=config.GOOGLE_API_KEY
    )
