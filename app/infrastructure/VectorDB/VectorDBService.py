# VectorDBService.py
from core.interface.IQwen3Faiss import IQwen3Faiss
from langchain_core.documents import Document
from typing import List
from dotenv import load_dotenv
load_dotenv()
import os

class VectorDBService(IQwen3Faiss):
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.persist_path = os.getenv("PERSIST_PATH")
        
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        if not self.vector_store:
            return []
        return self.vector_store.search_similar_documents(query, k=k)

    def get_vectorstore(self):
        return self.vector_store
