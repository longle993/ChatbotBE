import os
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from infrastructure.VectorDB.VectorDBService import VectorDBService
from dotenv import load_dotenv
load_dotenv()

class FAISSVectorDB(VectorDBService):
    def __init__(self):
        self.persist_path = os.getenv("PERSIST_PATH")
        self.model = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
        embeddings = GoogleGenerativeAIEmbeddings(model=self.model)
        vector_store = None

        # file FAISS index
        index_file = os.path.join(self.persist_path, "index.faiss")

        if os.path.exists(index_file):
            try:
                vector_store = FAISS.load_local(
                    self.persist_path,
                    embeddings,
                    allow_dangerous_deserialization=True
                )
                print(f"✅ Đã load vectorstore từ: {self.persist_path}")
            except Exception as e:
                print(f"❌ Lỗi khi load vectorstore: {e}")
                vector_store = None
        else:
            print(f"⚠️ Chưa có vectorstore tại: {self.persist_path}. Sẽ tạo mới sau.")

        super().__init__(vector_store)

    def save(self):
        if self.vector_store:
            self.vector_store.save_local(self.persist_path)
            print(f"💾 Đã lưu vectorstore vào: {self.persist_path}")
