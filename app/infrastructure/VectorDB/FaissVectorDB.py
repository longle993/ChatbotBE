import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from infrastructure.VectorDB.VectorDBService import VectorDBService
from langchain_core.documents import Document
from typing import List
from dotenv import load_dotenv
load_dotenv()

class FAISSVectorDB(VectorDBService):
    def __init__(self):
        self.persist_path = os.getenv("PERSIST_PATH")
        self.model = os.getenv("EMBEDDING_MODEL", "")
        self.embeddings = GoogleGenerativeAIEmbeddings(model=self.model)
        vector_store = None

        # file FAISS index
        index_file = os.path.join(self.persist_path, "index.faiss")

        if os.path.exists(index_file):
            try:
                vector_store = FAISS.load_local(
                    self.persist_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                ) 
                print(f"✅ Đã load vectorstore từ: {self.persist_path}")
            except Exception as e:
                print(f"❌ Lỗi khi load vectorstore: {e}")
                vector_store = None
        else:
            print(f"⚠️ Chưa có vectorstore tại: {self.persist_path}. Sẽ tạo mới sau.")

        super().__init__(vector_store)

    def save_vectorstore(self):
        print(f" vectorstore {self.vector_store}")
        print(f"💾 Đang lưu vectorstore vào: {self.persist_path}")
        if self.vector_store:
            self.vector_store.save_local(self.persist_path)
            print(f"💾 Đã lưu vectorstore vào: {self.persist_path}")
            return True
        return False
    
    def add_documents(self, documents: List[Document]):
        """Thêm documents vào FAISS vectorstore (và tạo mới nếu cần)"""
        if not documents:
            print("❗ Không có document nào để thêm.")
            return

        if self.vector_store:
            self.vector_store.add_documents(documents)
            print(f"➕ Đã thêm {len(documents)} documents vào vectorstore.")
        else:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            print(f"🆕 Đã tạo vectorstore mới từ {len(documents)} documents.")

        # Đảm bảo thư mục tồn tại trước khi lưu
        os.makedirs(self.persist_path, exist_ok=True)
        self.vector_store.save_local(self.persist_path)
        print(f"💾 Đã lưu vectorstore tại: {self.persist_path}")
