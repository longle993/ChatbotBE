from core.entity.Conversation import Conversation, Message
from core.interface.IConversationRepository import IConversationRepository
from bson import ObjectId
from pymongo.collection import Collection
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional

class ConversationRepositoryMongo(IConversationRepository):
    def __init__(self, collection: Collection):
        self.collection = collection

    async def create_conversation(self, conversation: Conversation) -> Conversation:
        """Tạo conversation mới"""
        doc = {
            "user_id": conversation.user_id,
            "title": conversation.title,
            "messages": [],
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "is_active": conversation.is_active
        }
        result = await self.collection.insert_one(doc)
        conversation.id = str(result.inserted_id)
        return conversation

    async def get_conversations_by_user_id(self, user_id: str, limit: int = 20) -> List[Conversation]:
        """Lấy danh sách conversations của user"""
        try:
            cursor = self.collection.find(
                {"user_id": user_id, "is_active": True}
            ).sort("updated_at", -1).limit(limit)
            
            docs = await cursor.to_list(length=None)
            conversations = []
            
            for doc in docs:
                # Chỉ lấy thông tin cơ bản, không load messages để tối ưu performance
                conversations.append(Conversation(
                    id=str(doc["_id"]),
                    user_id=doc["user_id"],
                    title=doc["title"],
                    messages=[],  # Không load messages ở đây
                    created_at=doc["created_at"],
                    updated_at=doc["updated_at"],
                    is_active=doc.get("is_active", True)
                ))
            
            return conversations
        except Exception as e:
            print(f"Error getting conversations by user id: {e}")
            return []

    async def get_conversation_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """Lấy conversation theo ID"""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(conversation_id)})
            if not doc:
                return None

            messages = []
            for msg_doc in doc.get("messages", []):
                messages.append(Message(
                    id=str(msg_doc.get("_id", "")),
                    role=msg_doc["role"],
                    content=msg_doc["content"],
                    timestamp=msg_doc["timestamp"]
                ))
            
            return Conversation(
                id=str(doc["_id"]),
                user_id=doc["user_id"],
                title=doc["title"],
                messages=messages,
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
                is_active=doc.get("is_active", True)
            )
        except Exception as e:
            print(f"Error getting conversation by id: {e}")
            return None

    async def get_conversations_by_user_id(self, user_id: str, limit: int = 20) -> List[Conversation]:
        """Lấy danh sách conversations của user"""
        try:
            cursor = self.collection.find(
                {"user_id": user_id, "is_active": True}
            ).sort("updated_at", -1).limit(limit)
            
            docs = await cursor.to_list(length=None)
            conversations = []
            
            for doc in docs:
                # Chỉ lấy thông tin cơ bản, không load messages để tối ưu performance
                conversations.append(Conversation(
                    id=str(doc["_id"]),
                    user_id=doc["user_id"],
                    title=doc["title"],
                    messages=[],  # Không load messages ở đây
                    created_at=doc["created_at"],
                    updated_at=doc["updated_at"],
                    is_active=doc.get("is_active", True)
                ))
            
            return conversations
        except Exception as e:
            print(f"Error getting conversations by user id: {e}")
            return []

    async def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """Cập nhật tiêu đề conversation"""
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(conversation_id)},
                {
                    "$set": {
                        "title": title,
                        "updated_at": datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating conversation title: {e}")
            return False

    async def add_message(self, conversation_id: str, message: Message) -> bool:
        """Thêm message vào conversation"""
        try:
            message_doc = {
                "_id": ObjectId(),
                "role": message.role,
                "content": message.content,
                "timestamp": message.timestamp
            }
            
            result = await self.collection.update_one(
                {"_id": ObjectId(conversation_id)},
                {
                    "$push": {"messages": message_doc},
                    "$set": {"updated_at": datetime.now()}
                }
            )
            
            # Set message ID từ ObjectId đã tạo
            message.id = str(message_doc["_id"])
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error adding message: {e}")
            return False

    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Xóa conversation (soft delete - chỉ owner mới được xóa)"""
        try:
            result = await self.collection.update_one(
                {
                    "_id": ObjectId(conversation_id),
                    "user_id": user_id  # Đảm bảo chỉ owner mới được xóa
                },
                {
                    "$set": {
                        "is_active": False,
                        "updated_at": datetime.now()
                    }
                }
            )
            
            if result.matched_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found or you don't have permission to delete it"
                )
            
            return result.modified_count > 0
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error deleting conversation: {e}")
            return False

    async def get_messages(self, conversation_id: str, user_id: str, limit: int = 50) -> List[Message]:
        """Lấy messages của conversation (chỉ owner mới được xem)"""
        try:
            # Kiểm tra quyền sở hữu
            doc = await self.collection.find_one({
                "_id": ObjectId(conversation_id),
                "user_id": user_id
            })
            
            if not doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found or you don't have permission to access it"
                )
            
            # Lấy messages (giới hạn số lượng để tối ưu performance)
            messages = []
            raw_messages = doc.get("messages", [])
            
            # Lấy messages mới nhất (reverse để lấy từ cuối)
            recent_messages = raw_messages[-limit:] if len(raw_messages) > limit else raw_messages
            
            for msg_doc in recent_messages:
                messages.append(Message(
                    id=str(msg_doc.get("_id", "")),
                    role=msg_doc["role"],
                    content=msg_doc["content"],
                    timestamp=msg_doc["timestamp"]
                ))
            
            return messages
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []

    async def get_conversation_with_permission_check(self, conversation_id: str, user_id: str) -> Optional[Conversation]:
        """Lấy conversation với kiểm tra quyền sở hữu"""
        try:
            doc = await self.collection.find_one({
                "_id": ObjectId(conversation_id),
                "user_id": user_id,
                "is_active": True
            })
            
            if not doc:
                return None
            
            # Convert messages
            messages = []
            for msg_doc in doc.get("messages", []):
                messages.append(Message(
                    id=str(msg_doc.get("_id", "")),
                    role=msg_doc["role"],
                    content=msg_doc["content"],
                    timestamp=msg_doc["timestamp"]
                ))
            
            return Conversation(
                id=str(doc["_id"]),
                user_id=doc["user_id"],
                title=doc["title"],
                messages=messages,
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
                is_active=doc.get("is_active", True)
            )
        except Exception as e:
            print(f"Error getting conversation with permission check: {e}")
            return None