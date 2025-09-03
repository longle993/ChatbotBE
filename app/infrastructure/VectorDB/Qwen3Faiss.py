import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from core.interface.IQwen3Faiss import IQwen3Faiss
from typing import List
from dotenv import load_dotenv
import time

load_dotenv()

class Qwen3Faiss(IQwen3Faiss):
    def __init__(self):
        self.persist_path = os.getenv("PERSIST_PATH")
        
        # Sử dụng Qwen3-Embedding-0.6B - SOTA model
        print("🔄 Đang load Qwen3-Embedding-0.6B model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="Qwen/Qwen3-Embedding-0.6B",
            model_kwargs={
                'device': 'cpu',  # Dùng 'cuda' nếu có GPU
                'trust_remote_code': True,  # Cần thiết cho Qwen models
            },
            encode_kwargs={
                'normalize_embeddings': True,
                'batch_size': 32,  # Tăng batch size vì model mạnh
                # Có thể thêm instruction để tăng 1-5% performance
                'instruction': 'Represent this document for retrieval: '
            }
        )
        print("✅ Đã load Qwen3-Embedding-0.6B model!")
        
        vector_store = None
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

        self.vector_store = vector_store

    def save_vectorstore(self) -> bool:
        """Lưu vectorstore vào persist_path"""
        print(f"💾 Đang lưu vectorstore vào: {self.persist_path}")
        try:
            if self.vector_store:
                os.makedirs(self.persist_path, exist_ok=True)
                self.vector_store.save_local(self.persist_path)
                print(f"💾 Đã lưu vectorstore vào: {self.persist_path}")
                return True
            else:
                print("❌ Không có vectorstore để lưu!")
                return False
        except Exception as e:
            print(f"❌ Lỗi khi lưu vectorstore: {e}")
            return False
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Thêm documents với Qwen3 - NHANH và CHẤT LƯỢNG CAO"""
        if not documents:
            print("❗ Không có document nào để thêm.")
            return False

        try:
            print(f"🚀 Bắt đầu embedding {len(documents)} documents với Qwen3-0.6B...")
            start_time = time.time()

            if self.vector_store:
                self.vector_store.add_documents(documents)
                print(f"➕ Đã thêm {len(documents)} documents vào vectorstore.")
            else:
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
                print(f"🆕 Đã tạo vectorstore mới từ {len(documents)} documents.")

            # Tự động lưu sau khi thêm
            save_success = self.save_vectorstore()
            
            total_time = time.time() - start_time
            print(f"⏰ Hoàn thành trong {total_time:.2f}s (trung bình {total_time/len(documents):.2f}s/doc)")
            
            return save_success
            
        except Exception as e:
            print(f"❌ Lỗi khi thêm documents: {e}")
            return False

    def add_documents_with_custom_instruction(self, documents: List[Document], instruction: str) -> bool:
        """Thêm documents với custom instruction để tăng performance"""
        if not documents:
            print("❗ Không có document nào để thêm.")
            return False

        if not instruction:
            print("⚠️ Không có instruction, sử dụng add_documents thông thường.")
            return self.add_documents(documents)

        try:
            print(f"🎯 Sử dụng custom instruction: '{instruction[:50]}...'")
            
            # Tạo embedding instance mới với instruction khác
            custom_embeddings = HuggingFaceEmbeddings(
                model_name="Qwen/Qwen3-Embedding-0.6B",
                model_kwargs={
                    'device': 'cpu',
                    'trust_remote_code': True,
                },
                encode_kwargs={
                    'normalize_embeddings': True,
                    'batch_size': 32,
                    'instruction': instruction
                }
            )
            
            # Backup embedding hiện tại
            original_embeddings = self.embeddings
            self.embeddings = custom_embeddings
            
            # Thêm documents
            success = self.add_documents(documents)
            
            # Restore embedding
            self.embeddings = original_embeddings
            
            return success
            
        except Exception as e:
            print(f"❌ Lỗi khi thêm documents với custom instruction: {e}")
            # Restore embedding trong trường hợp lỗi
            if 'original_embeddings' in locals():
                self.embeddings = original_embeddings
            return False

    def add_documents_optimized(self, documents: List[Document], chunk_size: int = 1000) -> bool:
        """Version tối ưu với chunking phù hợp cho Qwen3"""
        if not documents:
            print("❗ Không có document nào để thêm.")
            return False

        try:
            print(f"🔧 Tối ưu hóa documents với chunk_size={chunk_size}")
            
            # Chunk với size lớn hơn vì Qwen3 xử lý context dài tốt hơn
            chunked_docs = []
            for doc in documents:
                if len(doc.page_content) > chunk_size:
                    content = doc.page_content
                    for i in range(0, len(content), chunk_size):
                        chunk_content = content[i:i + chunk_size]
                        chunk_metadata = doc.metadata.copy()
                        chunk_metadata['chunk_id'] = f"{doc.metadata.get('row_index', 0)}_chunk_{i//chunk_size}"
                        chunk_metadata['is_chunked'] = True
                        
                        chunked_docs.append(Document(
                            page_content=chunk_content,
                            metadata=chunk_metadata
                        ))
                else:
                    chunked_docs.append(doc)
            
            if len(chunked_docs) != len(documents):
                print(f"🔄 Đã chunk {len(documents)} docs thành {len(chunked_docs)} pieces")
            
            # Sử dụng instruction phù hợp cho technical documents
            return self.add_documents_with_custom_instruction(
                chunked_docs, 
                instruction="Represent this technical document for semantic search and retrieval: "
            )
            
        except Exception as e:
            print(f"❌ Lỗi khi tối ưu hóa documents: {e}")
            return False
    
    def similarity_search(self, query: str, k: int = 5, score_threshold: float = 0.0):
        """Bonus method: Tìm kiếm documents tương tự"""
        if not self.vector_store:
            print("❌ Chưa có vectorstore để search!")
            return []
        
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            # Filter theo score threshold nếu cần
            filtered_results = [(doc, score) for doc, score in results if score >= score_threshold]
            return filtered_results
        except Exception as e:
            print(f"❌ Lỗi khi search: {e}")
            return []
    
    def get_vectorstore_info(self) -> dict:
        """Bonus method: Lấy thông tin về vectorstore"""
        if not self.vector_store:
            return {"status": "empty", "count": 0}
        
        try:
            # Thử lấy số lượng documents (có thể không work với tất cả FAISS versions)
            info = {
                "status": "loaded",
                "persist_path": self.persist_path,
                "embedding_model": "Qwen/Qwen3-Embedding-0.6B"
            }
            
            # Thử lấy số vectors nếu có thể
            if hasattr(self.vector_store, 'index') and hasattr(self.vector_store.index, 'ntotal'):
                info["vector_count"] = self.vector_store.index.ntotal
            
            return info
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Alternative: Sử dụng trực tiếp sentence-transformers cho flexibility cao hơn
class DirectQwen3EmbeddingService:
    def __init__(self):
        from sentence_transformers import SentenceTransformer
        print("🔄 Đang load Qwen3-Embedding-0.6B với SentenceTransformers...")
        
        self.model = SentenceTransformer(
            "Qwen/Qwen3-Embedding-0.6B",
            trust_remote_code=True,
            device='cpu'  # hoặc 'cuda'
        )
        print("✅ Đã load xong!")
    
    def embed_documents(self, texts: List[str], instruction: str = None) -> List[List[float]]:
        """Embed documents với optional instruction"""
        if instruction:
            texts = [f"{instruction}{text}" for text in texts]
        
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=True
        )
        return embeddings.tolist()
    
    def embed_query(self, query: str, instruction: str = "Represent this query for retrieving relevant documents: ") -> List[float]:
        """Embed query với instruction phù hợp"""
        if instruction:
            query = f"{instruction}{query}"
        
        embedding = self.model.encode(
            query,
            normalize_embeddings=True
        )
        return embedding.tolist()