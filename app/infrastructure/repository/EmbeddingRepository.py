from core.interface.IEmbeddingRepository import IEmbeddingRepository
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

class GoogleEmbeddingService(IEmbeddingRepository):
    def __init__(self):
        self.embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    def embed_text(self, text: str) -> list[float]:
        return self.embedding_model.embed_query(text)

    def embed_documents(self, documents: list[Document]):
        return self.embedding_model.embed_documents([doc.page_content for doc in documents])

    def combine_text_columns(self, row, headers) -> str:
        """Ghép nội dung các cột Excel thành một đoạn văn bản duy nhất"""
        return " ".join(f"{header}: {row[header]}" for header in headers if header in row and row[header] is not None)
    
    def embed_excel(self, df, header):
        documents = []
        ids = []
        for index, row in df.iterrows():
            content = self.combine_text_columns(row, header)
            doc = Document(
                page_content=content,
                metadata={
                    "product": row[header[0]],
                }
            )
            documents.append(doc)
            ids.append(str(index))
        return documents, ids
