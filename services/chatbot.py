
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
import io
import docx
import base64
import pandas as pd
from langchain_core.documents import Document

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
    
    def extract_file_contents(self, files, embedder=None, vector_db=None):
        file_contents = []
        for f in files:
            text = ""
            file_name = f.get("name", "").lower()
            encoded_content = f.get("content", "")

            try:
                file_bytes = base64.b64decode(encoded_content.split(',')[-1])
            except Exception:
                file_bytes = b""

            if file_name.endswith(".pdf"):
                try:
                    import io
                    from PyPDF2 import PdfReader
                    pdf_reader = PdfReader(io.BytesIO(file_bytes))
                    for page in pdf_reader.pages:
                        t = page.extract_text() or ""
                        text += t
                except Exception:
                    text += "[Không thể đọc file PDF]"
            elif file_name.endswith(".docx"):
                try:
                    doc = docx.Document(io.BytesIO(file_bytes))
                    for para in doc.paragraphs:
                        text += para.text + "\n"
                except Exception:
                    text += "[Không thể đọc file DOCX]"
            elif file_name.endswith(".xlsx") and embedder and vector_db:
                try:
                    df = pd.read_excel("data/documents/data.xlsx")
                    header = df.columns.tolist()
                    documents = []
                    for index, row in df.iterrows():
                        content = embedder.combine_text_columns(row, header)
                        doc = Document(
                            page_content=content,
                            metadata={"index": index}
                        )
                        documents.append(doc)
                    vector_db.add_documents(documents)
                except Exception:
                    text += "[Không thể đọc file Excel]"
            else:
                try:
                    text = file_bytes.decode("utf-8")
                except Exception:
                    text = "[Không thể đọc file dạng text]"

            if text:
                file_contents.append(f"{f['name']}:\n{text[:3000]}")
        return file_contents
    def embed_and_reload_files(self, files, embedder, vector_db):
        """
        Nhúng nội dung các file vào vector store và load lại vector store cho chatbot.
        """

        documents = []
        for f in files:
            file_name = f.get("name", "").lower()
            encoded_content = f.get("content", "")
            try:
                file_bytes = base64.b64decode(encoded_content.split(',')[-1])
            except Exception:
                file_bytes = b""

            if file_name.endswith(".pdf"):
                try:
                    from PyPDF2 import PdfReader
                    pdf_reader = PdfReader(io.BytesIO(file_bytes))
                    for page in pdf_reader.pages:
                        text = page.extract_text() or ""
                        doc = Document(page_content=text, metadata={"name": file_name})
                        documents.append(doc)
                except Exception:
                    pass
            elif file_name.endswith(".docx"):
                try:
                    docx_file = docx.Document(io.BytesIO(file_bytes))
                    text = "\n".join([para.text for para in docx_file.paragraphs])
                    doc = Document(page_content=text, metadata={"name": file_name})
                    documents.append(doc)
                except Exception:
                    pass
            elif file_name.endswith(".xlsx"):
                try:
                    df = pd.read_excel(io.BytesIO(file_bytes))
                    header = df.columns.tolist()
                    for index, row in df.iterrows():
                        content = embedder.combine_text_columns(row, header)
                        doc = Document(page_content=content, metadata={"name": file_name, "index": index})
                        documents.append(doc)
                except Exception:
                    pass
            else:
                try:
                    text = file_bytes.decode("utf-8")
                    doc = Document(page_content=text, metadata={"name": file_name})
                    documents.append(doc)
                except Exception:
                    pass

        if documents:
            vector_db.add_documents(documents)
            self.vector_store = vector_db.get_vectorstore()

