from typing import List, Optional
from core.entity.Chat import Message
from core.interface.ILLMRepository import ILLMRepository
from core.interface.IVectorDBRepository import IVectorDBRepository
from core.interface.IFileRepository import IFileRepository
from fastapi import UploadFile

class ChatWithGemini:
    def __init__(self, llm: ILLMRepository, vector_db: IVectorDBRepository, file_repo: IFileRepository):
        self.llm = llm
        self.vector_db = vector_db
        self.file_repo = file_repo
        self.last_query = ""
        self.last_context = ""

    def execute(self, question: str, history: List[Message], 
                documents: Optional[List[UploadFile]] = None) -> str:
        
        # 1. Xử lý file nếu có
        file_context = ""
        if documents:
            try:
                # Extract content từ các file
                extracted_docs = self.file_repo.extract_file(documents)
                
                if extracted_docs:
                    # Lưu documents vào vector database để có thể search sau này
                    #self.vector_db.add_documents(extracted_docs)
                    #print(f"✅ Đã xử lý và lưu {len(extracted_docs)} documents từ {len(documents)} files")
                    
                    # Tạo context từ file content cho câu hỏi hiện tại
                    file_context = "\n\n".join([doc.page_content for doc in extracted_docs])
                    print(f"✅ Đã tạo file context với {len(file_context)} ký tự")
                else:
                    print("⚠️ Không thể extract content từ files")
                    
            except Exception as e:
                print(f"❌ Lỗi khi xử lý files: {e}")
                file_context = ""

        # 2. Tìm kiếm context từ vector database (bao gồm cả documents cũ)
        vector_context = ""
        try:
            context_docs = self.vector_db.similarity_search(question, k=5)
            if context_docs:
                vector_context = "\n\n".join([doc[0].page_content for doc in context_docs])
                print(f"✅ Đã tạo vector context từ {len(context_docs)} documents")
            else:
                print("⚠️ Không tìm thấy documents phù hợp trong vector DB")
        except (IndexError, AttributeError) as e:
            print(f"❌ Lỗi khi xử lý vector context: {e}")
            vector_context = ""

        # 3. Kết hợp context từ file mới và vector database
        combined_context = self.combine_contexts(file_context, vector_context)
        
        # 4. Gửi request đến LLM
        response = self.llm.chat(
            context=combined_context, 
            history=history, 
            question=question
        )

        # 5. Lưu lại query và context cuối cùng
        self.last_query = question
        self.last_context = combined_context
        
        return response
    
    def combine_contexts(self, file_context: str, vector_context: str) -> str:
        """
        Kết hợp context từ file mới và vector database
        
        Args:
            file_context: Context từ files vừa upload
            vector_context: Context từ vector database
            
        Returns:
            str: Combined context
        """
        contexts = []
        
        if file_context:
            contexts.append(f"=== THÔNG TIN TỪ FILES VỪA UPLOAD ===\n{file_context}")
            
        if vector_context:
            contexts.append(f"=== THÔNG TIN LIÊN QUAN TỪ CƠ SỞ DỮ LIỆU ===\n{vector_context}")
            
        if contexts:
            combined = "\n\n" + "\n\n".join(contexts) + "\n\n"
            print(f"✅ Đã kết hợp context với tổng cộng {len(combined)} ký tự")
            return combined
        else:
            print("⚠️ Không có context nào được tìm thấy")
            return ""

    def get_file_content_preview(self, documents: List[UploadFile]) -> str:
        """
        Phương thức để preview content từ files mà không lưu
        
        Args:
            documents: Danh sách files cần preview
            
        Returns:
            str: Preview content từ các files
        """
        try:
            extracted_docs = self.file_repo.extract_file(documents)
            if extracted_docs:
                preview = "\n\n".join([
                    f"File: {doc.metadata.get('source', 'unknown')}\n{doc.page_content[:500]}..." 
                    if len(doc.page_content) > 500 else doc.page_content
                    for doc in extracted_docs
                ])
                print(f"✅ Đã tạo preview từ {len(extracted_docs)} documents")
                return preview
            return "Không thể đọc nội dung từ files"
        except Exception as e:
            print(f"❌ Lỗi khi preview files: {e}")
            return f"Lỗi khi xử lý files: {str(e)}"