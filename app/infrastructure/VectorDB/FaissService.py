from langchain.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from VectorDBService import VectorDBService

class FAISSVectorDB(VectorDBService):
    def __init__(self):
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = FAISS(embedding_function=embeddings, index=None)
        super().__init__(vector_store)
