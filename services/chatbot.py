
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter



class Gemini:
    def __init__(self, vector_db):
        # Khởi tạo model và embeddings
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.7,
            max_tokens=1000
        )
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001"
        )
        
        # Memory cho conversation
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Vector store
        self.vector_store = vector_db

        # Prompt template cho RAG với labels
        self.rag_prompt = ChatPromptTemplate.from_messages([
            ("system", """Bạn là một trợ lý AI thân thiện, thông minh và hữu ích. 
        - Ưu tiên sử dụng thông tin trong `Context` để trả lời câu hỏi, bao gồm cả nội dung từ các file mà người dùng đính kèm (ví dụ: PDF, Word, Excel).
        - Nếu trong `Context` có phần liên quan đến file (bảng dữ liệu, văn bản, báo cáo...), hãy tóm tắt các ý chính hoặc trích xuất thông tin quan trọng từ file đó để trả lời câu hỏi của người dùng.
        - Nếu thông tin trong `Context` không đầy đủ hoặc không liên quan, hãy dựa vào kiến thức của bạn để trả lời.
        - Luôn trả lời bằng cùng ngôn ngữ với câu hỏi (tiếng Việt hoặc tiếng Anh).
        - Nếu câu hỏi không rõ ràng hoặc thiếu dữ kiện, hãy yêu cầu người dùng cung cấp thêm thông tin hoặc mô tả cụ thể về file.
        - Nếu `Context` quá dài hoặc chứa nhiều chi tiết, hãy tóm tắt ngắn gọn các điểm chính rồi trả lời rõ ràng.
        - Có thể sử dụng từ đồng nghĩa trong `Context` hoặc kiến thức để làm phong phú câu trả lời.

        Context (có thể bao gồm nội dung file):
        {context}

        Lịch sử trò chuyện:
        {chat_history}"""),
            ("human", "{question}")
        ])
        
        self.chain = self.rag_prompt | self.llm | StrOutputParser()

    
    def search_similar_documents(self, query, k=3):
        """Tìm kiếm documents tương tự"""
        if not self.vector_store:
            return []
        
        docs = self.vector_store.similarity_search(query, k=k)
        return docs
    
    def chat(self, user_input):
        context = ""
        
        if self.vector_store:
            relevant_docs = self.search_similar_documents(user_input, k=3)
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        # Lấy lịch sử chat
        chat_history = self.memory.chat_memory.messages
        
        # Generate response
        response = self.chain.invoke({
            "context": context,
            "chat_history": chat_history,
            "question": user_input
        })
        
        # Lưu vào memory
        self.memory.chat_memory.add_user_message(user_input)
        self.memory.chat_memory.add_ai_message(response)
        
        return response

