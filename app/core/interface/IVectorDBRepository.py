from abc import ABC, abstractmethod
from typing import List

class IVectorDBRepository(ABC):
    @abstractmethod
    def similarity_search(self, query: str, k: int = 5) -> list:
        pass

    @abstractmethod
    def add_documents(self, documents: list):
        pass