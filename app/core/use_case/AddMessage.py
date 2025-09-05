from datetime import datetime
from email.message import Message
from core.entity.Conversation import Conversation
from core.interface.IConversationRepository import IConversationRepository

class CreateConversation:
    def __init__(self, conv_repo: IConversationRepository):
        self.conv_repo = conv_repo

    async def execute(self, conversation_id: str, message: Message) -> Conversation:
        return await self.conv_repo.add_message(conversation_id, message)

