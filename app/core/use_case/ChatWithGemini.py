from typing import List
from core.entity.Chat import Message
from core.interface.ILLMRepository import ILLMRepository
from core.interface.IVectorDBRepository import IVectorDBRepository

class ChatWithGemini:
    def __init__(self, llm: ILLMRepository, vector_db: IVectorDBRepository):
        self.llm = llm
        self.vector_db = vector_db
        self.last_query = ""
        self.last_context = ""

    def execute(self, question: str, history: List[Message]) -> str:
        context_docs = self.vector_db.similarity_search(question, k=5)
        context = "\n\n".join([doc.page_content for doc in context_docs])

        response = self.llm.chat(context=context, history=history, question=question)

        self.last_query = question
        self.last_context = context
        return response
