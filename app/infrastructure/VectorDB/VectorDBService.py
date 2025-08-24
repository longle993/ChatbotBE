# VectorDBService.py
from core.interface.IVectorDBRepository import IVectorDBRepository
from langchain_core.documents import Document
from typing import List
from dotenv import load_dotenv
load_dotenv()
import os

class VectorDBService(IVectorDBRepository):
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.persist_path = os.getenv("PERSIST_PATH")
        
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        if not self.vector_store:
            return []
        return self.vector_store.similarity_search(query, k=k)

    def add_documents(self, documents: List[Document]):
        if self.vector_store and documents:
            self.vector_store.add_documents(documents)

    def save_vectorstore(self):
        print(f" vectorstore {self.vector_store}")
        print(f"💾 Đang lưu vectorstore vào: {self.persist_path}")
        if self.vector_store:
            self.vector_store.save_local(self.persist_path)
            print(f"💾 Đã lưu vectorstore vào: {self.persist_path}")
            return True
        return False

    def get_vectorstore(self):
        return self.vector_store
