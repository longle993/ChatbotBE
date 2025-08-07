import pandas as pd
import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from services.embed import Embedder
from services.vector_db import VectorDB
from services.chatbot import Gemini

# Load .env
load_dotenv()
model_name = os.getenv("EMMBEDDING_MODEL")  # đảm bảo trong .env có biến này

# Khởi tạo embedder, veector_db và chatbot
embedder = Embedder(model_name)
persist_path = os.getenv("PERSIST_PATH") 
vector_db = VectorDB(embedder.model, persist_path=persist_path)
gemini_chatbot = Gemini(vector_db.get_vectorstore())

# Đọc Excel
df = pd.read_excel("data/documents/data.xlsx")
header = df.columns.tolist()

# Chuyển Excel → Documents
documents = []
for index, row in df.iterrows():
    content = embedder.combine_text_columns(row, header)
    doc = Document(
        page_content=content,
        metadata={"index": index}
    )
    documents.append(doc)
    print(content)

# Nhúng & lưu vào FAISS
vector_db.add_documents(documents)
print("✅ Đã nhúng xong và lưu FAISS thành công.")

while True:
    user_input = input("\nBạn: ").strip()
    if user_input.lower() in ["exit", "quit", "thoát"]:
        break
    if user_input:
        response = gemini_chatbot.chat(user_input)
        print(f"AI: {response}")