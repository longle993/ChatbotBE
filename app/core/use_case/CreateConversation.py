from datetime import datetime
from email.message import Message
from core.entity.Conversation import Conversation
from core.interface.IConversationRepository import IConversationRepository

class CreateConversation:
    def __init__(self, conv_repo: IConversationRepository):
        self.conv_repo = conv_repo

    async def execute(self, user_id: str, title: str, messages: list[Message]) -> Conversation:
        conversation = Conversation(
            user_id=user_id,
            title=title,
            messages=messages,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        return await self.conv_repo.create_conversation(conversation)

