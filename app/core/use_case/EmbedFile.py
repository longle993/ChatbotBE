from langchain_core.documents import Document

class EmbedFilesUseCase:
    def __init__(self, embedder, vector_db):
        """
        embedder: EmbeddingRepository
        vector_db: VectorDBRepository
        """
        self.embedder = embedder
        self.vector_db = vector_db

    def execute(self, files: list[dict]):
        documents = []
        for f in files:
            file_name = f.get("name", "").lower()
            file_bytes = f.get("bytes", b"")

            # Ví dụ chỉ xử lý text để demo
            try:
                text = file_bytes.decode("utf-8")
            except Exception:
                text = "[Không thể đọc file dạng text]"

            doc = Document(page_content=text, metadata={"name": file_name})
            documents.append(doc)

        if documents:
            self.vector_db.add_documents(documents)
        return len(documents)
