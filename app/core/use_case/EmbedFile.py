from langchain_core.documents import Document

from core.interface import IVectorDBRepository
from core.interface.IEmbeddingRepository import IEmbeddingRepository

class EmbedFilesUseCase:
    def __init__(self, embedder: IEmbeddingRepository, vector_db: IVectorDBRepository):
        """
        embedder: EmbeddingRepository
        vector_db: VectorDBRepository
        """
        self.embedder = embedder
        self.vector_db = vector_db

    def execute(self, files: list[dict]):
              
        docs = self.embedder.embed_documents([Document(page_content=f.get("content", ""), metadata={"name": f.get("name", "")}) for f in files])
        self.vector_db.add_documents(docs)
        self.vector_db.save_vectorstore()
        return len(docs)
