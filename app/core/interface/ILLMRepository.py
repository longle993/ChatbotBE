from abc import ABC, abstractmethod
from typing import List
from core.entity.Chat import Message

class ILLMRepository(ABC):
    @abstractmethod
    def chat(self, context: str, history: List[Message], question: str) -> str:
        pass