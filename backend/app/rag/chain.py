from typing import List, Tuple
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core import config


class LLMGenerationError(Exception):
    """Raised when the underlying Gemini call fails (timeout, API error, etc.)."""


class QAChain:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            google_api_key=config.GOOGLE_API_KEY,
            temperature=0.0
        )
        self.fallback_message = "I couldn't find relevant information in your uploaded documents to answer this question."

    def generate_answer(self, question: str, chunks: List[Tuple[Document, float]]) -> Tuple[str, bool]:
        if not chunks:
            return self.fallback_message, False
        context_blocks = []
        for doc, score in chunks:
            name = doc.metadata.get("document_name", "Unknown Document")
            page = doc.metadata.get("page", 0) + 1
            context_blocks.append(f"Source: {name} (Page {page})\nContent: {doc.page_content}\n")
        context = "\n---\n".join(context_blocks)
        system_prompt = (
            "You are a strict QA assistant. Your task is to answer the user's question using ONLY the provided context blocks.\n"
            "Here are the rules you MUST follow:\n"
            "1. Answer the question comprehensively but strictly based on the context.\n"
            "2. If the context does not contain enough information to answer the question, or if you are unsure, you MUST reply exactly with: "
            f"'{self.fallback_message}'\n"
            "3. Do not use any external knowledge. Do not assume or extrapolate."
        )
        messages = [
            ("system", system_prompt),
            ("user", f"Context:\n{context}\n\nQuestion: {question}")
        ]
        try:
            response = self.llm.invoke(messages)
        except Exception as e:
            raise LLMGenerationError(str(e)) from e
        answer = response.content.strip()
        is_grounded = answer != self.fallback_message
        return answer, is_grounded
