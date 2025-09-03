from abc import ABC, abstractmethod
from typing import List
from langchain_core.documents import Document

class IQwen3Faiss(ABC):
    @abstractmethod
    def save_vectorstore(self) -> bool:
        pass
    
    @abstractmethod
    def add_documents(self, documents: List[Document]) -> bool:
        pass
    
    @abstractmethod
    def add_documents_with_custom_instruction(self, documents: List[Document], instruction: str) -> bool:
        pass
    
    @abstractmethod
    def add_documents_optimized(self, documents: List[Document], chunk_size: int) -> bool:
        pass
    
    @abstractmethod
    def similarity_search(self, query: str, k: int) -> List[Document]:
        pass
