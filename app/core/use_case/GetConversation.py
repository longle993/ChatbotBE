from core.entity.Conversation import Conversation
from core.interface.IConversationRepository import IConversationRepository

class GetConversation:
    def __init__(self, conversation_repo: IConversationRepository):
        self.conversation_repo = conversation_repo

    async def execute(self, id: str) -> list[Conversation]:
        return await self.conversation_repo.get_conversations_by_user_id(id)