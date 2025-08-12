from core.interface.IVectorDBRepository import IVectorDBRepository
from langchain_core.documents import Document

class VectorDBService(IVectorDBRepository):
    def __init__(self, vector_store):
        """
        vector_store: Một instance của FAISS, Pinecone, Weaviate, Chroma... 
        đã được khởi tạo sẵn bên ngoài và inject vào.
        """
        self.vector_store = vector_store

    def similarity_search(self, query: str, k: int = 5):
        if not self.vector_store:
            return []
        return self.vector_store.similarity_search(query, k=k)

    def add_documents(self, documents: list[Document]):
        if self.vector_store and documents:
            self.vector_store.add_documents(documents)

    def get_vectorstore(self):
        return self.vector_store
