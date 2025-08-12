import pandas as pd
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

class Embedder:
    def __init__(self, model_name):
        self.model = GoogleGenerativeAIEmbeddings(model=model_name)

    def embed_text(self, text):
        return self.model.embed_query(text)

    def embed_documents(self, documents):
        return self.model.embed_documents(documents)

    def combine_text_columns(self, row, header):
        return ". ".join([
            f"{col}: {row[col]}" for col in header if pd.notna(row[col])
        ])


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



