from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from app.core import config

class DocumentSplitter:
    def __init__(self):
        self.chunk_size = config.CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP
        self.separators = ["\n\n", "\n", ". ", " ", ""]
        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators
        )
        self.markdown_headers = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3")
        ]
        self.markdown_header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.markdown_headers
        )

    def split_documents(self, documents: List[Document], file_type: str) -> List[Document]:
        file_type = file_type.lower()
        if file_type in ["md", "markdown", "docx", "doc"]:
            split_docs = []
            for doc in documents:
                header_splits = self.markdown_header_splitter.split_text(doc.page_content)
                for split in header_splits:
                    split.metadata.update(doc.metadata)
                    split_docs.extend(self.recursive_splitter.split_documents([split]))
            return split_docs
        else:
            return self.recursive_splitter.split_documents(documents)
