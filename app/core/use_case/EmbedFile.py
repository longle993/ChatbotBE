from langchain_core.documents import Document
from fastapi import UploadFile
from core.interface.IQwen3Faiss import IQwen3Faiss
from core.interface.IFileRepository import IFileRepository

class EmbedFilesUseCase:
    def __init__(self, file_repo: IFileRepository, embedder: IQwen3Faiss):
        """
        embedder: EmbeddingRepository
        vector_db: VectorDBRepository
        """
        self.file_repo = file_repo
        self.embedder = embedder

    def execute(self, files: list[UploadFile]) -> int:
        documents = self.file_repo.extract_file(files)
        self.embedder.add_documents_optimized(documents, chunk_size=512)

        return len(documents)
