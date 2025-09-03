import os
import time
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from langchain_core.documents import Document
from typing import List
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
load_dotenv()

class GeminiFaiss():
    def __init__(self):
        self.persist_path = os.getenv("PERSIST_PATH")
        self.model = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
        # Tăng timeout và retry cho Gemini API
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=self.model,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            # Thêm config để tối ưu
            task_type="RETRIEVAL_DOCUMENT",
            # Có thể thêm rate limiting nếu cần
        )
        vector_store = None

        # file FAISS index
        index_file = os.path.join(self.persist_path, "index.faiss")

        if os.path.exists(index_file):
            try:
                vector_store = FAISS.load_local(
                    self.persist_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                ) 
                print(f"✅ Đã load vectorstore từ: {self.persist_path}")
            except Exception as e:
                print(f"❌ Lỗi khi load vectorstore: {e}")
                vector_store = None
        else:
            print(f"⚠️ Chưa có vectorstore tại: {self.persist_path}. Sẽ tạo mới sau.")

        super().__init__(vector_store)

    def save_vectorstore(self):
        print(f"💾 Đang lưu vectorstore vào: {self.persist_path}")
        if self.vector_store:
            self.vector_store.save_local(self.persist_path)
            print(f"💾 Đã lưu vectorstore vào: {self.persist_path}")
            return True
        return False
    
    def add_documents_batch(self, documents: List[Document], batch_size: int = 3, delay: float = 5.0):
        """Thêm documents theo batch với exponential backoff để tránh rate limit"""
        if not documents:
            print("❗ Không có document nào để thêm.")
            return

        print(f"🚀 Bắt đầu embedding {len(documents)} documents với batch_size={batch_size}")
        
        # Chia documents thành batches nhỏ hơn
        batches = [documents[i:i + batch_size] for i in range(0, len(documents), batch_size)]
        
        all_embeddings = []
        total_time = 0
        
        for i, batch in enumerate(batches):
            start_time = time.time()
            print(f"📦 Xử lý batch {i+1}/{len(batches)} ({len(batch)} docs)...")
            
            retry_count = 0
            max_retries = 5
            base_delay = delay
            
            while retry_count <= max_retries:
                try:
                    # Embed từng document một để tránh rate limit
                    batch_embeddings = []
                    for j, doc in enumerate(batch):
                        print(f"  📄 Embedding doc {j+1}/{len(batch)} trong batch {i+1}...")
                        doc_embedding = self.embeddings.embed_documents([doc.page_content])
                        batch_embeddings.extend(doc_embedding)
                        
                        # Delay nhỏ giữa các document
                        if j < len(batch) - 1:
                            time.sleep(0.5)
                    
                    all_embeddings.extend(batch_embeddings)
                    batch_time = time.time() - start_time
                    total_time += batch_time
                    print(f"✅ Hoàn thành batch {i+1} trong {batch_time:.2f}s")
                    break
                    
                except Exception as e:
                    retry_count += 1
                    if "429" in str(e) or "exhausted" in str(e):
                        # Exponential backoff
                        wait_time = base_delay * (2 ** retry_count)
                        print(f"🚫 Rate limit hit! Retry {retry_count}/{max_retries} sau {wait_time:.1f}s...")
                        time.sleep(wait_time)
                    else:
                        print(f"❌ Lỗi khác: {e}")
                        raise
            
            if retry_count > max_retries:
                print(f"❌ Đã retry {max_retries} lần, bỏ qua batch này")
                continue
                
            # Delay dài giữa các batch
            if i < len(batches) - 1:
                print(f"⏳ Chờ {delay}s trước batch tiếp theo...")
                time.sleep(delay)

        print(f"⏰ Tổng thời gian embedding: {total_time:.2f}s")
        
        # Tạo hoặc cập nhật vectorstore
        if self.vector_store:
            self.vector_store.add_documents(documents)
            print(f"➕ Đã thêm {len(documents)} documents vào vectorstore.")
        else:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            print(f"🆕 Đã tạo vectorstore mới từ {len(documents)} documents.")

        # Lưu vectorstore
        os.makedirs(self.persist_path, exist_ok=True)
        self.vector_store.save_local(self.persist_path)
        print(f"💾 Đã lưu vectorstore tại: {self.persist_path}")

    def add_documents(self, documents: List[Document]):
        """Wrapper cho add_documents_batch với config mặc định"""
        self.add_documents_batch(documents, batch_size=5, delay=1.5)

    def add_documents_optimized(self, documents: List[Document], chunk_size: int = 512):
        """Version tối ưu với text chunking nếu documents quá dài"""
        if not documents:
            print("❗ Không có document nào để thêm.")
            return

        # Chunk documents dài thành pieces nhỏ hơn
        chunked_docs = []
        for doc in documents:
            if len(doc.page_content) > chunk_size:
                # Chia document dài thành chunks
                content = doc.page_content
                for i in range(0, len(content), chunk_size):
                    chunk_content = content[i:i + chunk_size]
                    # Tạo metadata mới cho chunk
                    chunk_metadata = doc.metadata.copy()
                    chunk_metadata['chunk_id'] = f"{doc.metadata.get('row_index', 0)}_chunk_{i//chunk_size}"
                    chunk_metadata['is_chunked'] = True
                    
                    chunked_docs.append(Document(
                        page_content=chunk_content,
                        metadata=chunk_metadata
                    ))
            else:
                chunked_docs.append(doc)
        
        print(f"🔄 Đã chunk {len(documents)} docs thành {len(chunked_docs)} pieces")
        
        # Sử dụng batching
        self.add_documents_batch(chunked_docs, batch_size=8, delay=1.0)