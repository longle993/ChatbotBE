from abc import ABC, abstractmethod
from typing import List, Optional
from core.entity.Conversation import Conversation, Message

class IConversationRepository(ABC):
    @abstractmethod
    async def create_conversation(self, conversation: Conversation) -> Conversation:
        """Tạo conversation mới"""
        pass
    
    @abstractmethod
    async def get_conversation_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """Lấy conversation theo ID"""
        pass
    
    @abstractmethod
    async def get_conversations_by_user_id(self, user_id: str, limit: int = 20) -> List[Conversation]:
        """Lấy danh sách conversations của user"""
        pass
    
    @abstractmethod
    async def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """Cập nhật tiêu đề conversation"""
        pass
    
    @abstractmethod
    async def add_message(self, conversation_id: str, message: Message) -> bool:
        """Thêm message vào conversation"""
        pass
    
    @abstractmethod
    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Xóa conversation (chỉ owner mới được xóa)"""
        pass
    
    @abstractmethod
    async def get_messages(self, conversation_id: str, user_id: str, limit: int = 50) -> List[Message]:
        """Lấy messages của conversation (chỉ owner mới được xem)"""
        pass