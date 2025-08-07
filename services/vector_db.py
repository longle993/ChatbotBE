from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain.embeddings.base import Embeddings
import os
from typing import List

class VectorDB:
    def __init__(self, embedding_model: Embeddings, persist_path: str = "vector_store"):
        self.persist_path = persist_path
        self.embedding_model = embedding_model
        self.vectorstore = None

        # Đường dẫn đầy đủ đến file FAISS
        index_file = os.path.join(self.persist_path, "index.faiss")

        if os.path.exists(index_file):
            try:
                self.vectorstore = FAISS.load_local(
                    self.persist_path,
                    self.embedding_model,
                    allow_dangerous_deserialization=True
                )
                print(f"✅ Đã load vectorstore từ: {self.persist_path}")
            except Exception as e:
                print(f"❌ Lỗi khi load vectorstore: {e}")
                self.vectorstore = None
        else:
            print(f"⚠️ Chưa có vectorstore tại: {self.persist_path}. Sẽ tạo mới sau.")

    def add_documents(self, documents: List[Document]):
        """Thêm documents vào FAISS vectorstore (và tạo mới nếu cần)"""
        if not documents:
            print("❗ Không có document nào để thêm.")
            return

        if self.vectorstore:
            self.vectorstore.add_documents(documents)
            print(f"➕ Đã thêm {len(documents)} documents vào vectorstore.")
        else:
            self.vectorstore = FAISS.from_documents(documents, self.embedding_model)
            print(f"🆕 Đã tạo vectorstore mới từ {len(documents)} documents.")

        # Đảm bảo thư mục tồn tại trước khi lưu
        os.makedirs(self.persist_path, exist_ok=True)
        self.vectorstore.save_local(self.persist_path)
        print(f"💾 Đã lưu vectorstore tại: {self.persist_path}")

    def get_vectorstore(self):
        """Trả về đối tượng FAISS VectorStore"""
        return self.vectorstore
