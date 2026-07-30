import os
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader

class DocumentLoader:
    @staticmethod
    def load_document(filepath: str, file_type: str) -> List[Document]:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        file_type = file_type.lower()
        if file_type == "pdf":
            return PyPDFLoader(filepath).load()
        elif file_type in ["docx", "doc"]:
            return Docx2txtLoader(filepath).load()
        elif file_type in ["md", "markdown", "txt"]:
            return TextLoader(filepath, encoding="utf-8").load()
        else:
            raise ValueError(f"Unsupported file format: {file_type}")
