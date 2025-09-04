from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.memory import ConversationBufferWindowMemory
from core.entity.Chat import Message
from core.interface.ILLMRepository import ILLMRepository
import os
from dotenv import load_dotenv
load_dotenv()


class GeminiLLMService(ILLMRepository):
    def __init__(self, model_name="gemini-2.0-flash", temperature=0.7, max_tokens=2000):
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature, api_key=os.getenv("GOOGLE_API_KEY"), max_tokens=max_tokens)
        self.memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True, k=10)
        
        # Prompt template được cải thiện cho RAG với context liên tục
        self.rag_prompt = ChatPromptTemplate.from_messages([
            ("system", """Bạn là một trợ lý AI thân thiện, thông minh và hữu ích. 

        HƯỚNG DẪN TRẢ LỜI:
        1. **Ưu tiên sử dụng thông tin trong Context** để trả lời câu hỏi
        2. **Kết hợp với lịch sử trò chuyện** để hiểu ngữ cảnh liên tục
        3. **Nếu câu hỏi hiện tại liên quan đến câu hỏi trước**, hãy:
           - Tham khảo thông tin đã thảo luận trước đó
           - Mở rộng hoặc làm rõ thêm dựa trên context mới
           - Duy trì tính liên kết trong cuộc trò chuyện
        4. **Nếu có từ như "đó", "này", "tiếp tục", "thêm nữa"**, hãy liên kết với nội dung trước đó
        5. Luôn trả lời bằng cùng ngôn ngữ với câu hỏi
        6. Nếu thiếu thông tin, yêu cầu làm rõ một cách thân thiện
        7. Kết hợp với kiến thức của bạn để cung cấp câu trả lời chính xác và đầy đủ nhất

        Context hiện tại:
        {context}

        Lịch sử trò chuyện (để hiểu ngữ cảnh liên tục):
        {chat_history}"""),
            ("human", "{question}")
        ])
        self.chain = self.rag_prompt | self.llm | StrOutputParser()

    def chat(self, context: str, history: list[Message], question: str) -> str:
        response = self.chain.invoke({
            "context": context,
            "chat_history": [m.content for m in history],
            "question": question
        })
        self.memory.chat_memory.add_user_message(question)
        self.memory.chat_memory.add_ai_message(response)
        return response
