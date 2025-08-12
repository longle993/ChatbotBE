from abc import ABC, abstractmethod
from typing import List
from core.entity.File import FileDocument
from langchain_core.documents import Document

class IEmbeddingRepository(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Nhúng một đoạn văn bản thành vector."""
        pass

    @abstractmethod
    def embed_documents(self, documents: list[Document]) -> list[list[float]]:
        """Nhúng danh sách Document thành vector."""
        pass

    @abstractmethod
    def combine_text_columns(self, row, headers) -> str:
        """Ghép nhiều cột từ file Excel thành một đoạn văn bản."""
        pass