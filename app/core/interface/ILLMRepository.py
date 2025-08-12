from abc import ABC, abstractmethod
from typing import List
from core.entity.Chat import ChatMessage

class ILLMRepository(ABC):
    @abstractmethod
    def chat(self, context: str, history: List[ChatMessage], question: str) -> str:
        pass