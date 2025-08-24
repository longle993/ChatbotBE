import base64
from fastapi import APIRouter, UploadFile, File, Request
import io
#from core.use_case.EmbedFile import EmbedFilesUseCase
#from infrastructure.repository.EmbeddingRepository import GoogleEmbeddingService
#from infrastructure.VectorDB.FaissVectorDB import FAISSVectorDB
#from presentation.schema.Embedder import EmbedderResponse
from core.entity.Response import ApiResponse
from security import (
    require_csrf,
    decode_jwt,
)
from langchain_core.documents import Document
import pandas as pd
from infrastructure.repository.FileRepository import FileRepository


router = APIRouter()

@router.post("/")
async def embed_files(
    request: Request,
    files: list[UploadFile] = File(...)
):
    require_csrf(request)
    user_id = decode_jwt(request)
     
    file_repo = FileRepository()
    documents = file_repo.extract_file(files)
    print(documents)
    return ApiResponse.success(len(documents))

"""    return EmbedderResponse.from_entity(
        ApiResponse.success(len(documents))
    )
"""
"""
    embedder = GoogleEmbeddingService()
    vector_db = FAISSVectorDB()


    file_dicts = []

    for f in files:
        file_bytes = await f.read()
        encoded_content = base64.b64encode(file_bytes).decode("utf-8")
 
        file_dicts.append({
            "name": f.filename,
            "content": encoded_content
        })

        # Nếu là Excel
        if f.filename.endswith(".xlsx"):
            df = pd.read_excel(io.BytesIO(file_bytes))
            header = df.columns.tolist()
            documents = []
            for index, row in df.iterrows():
                content = embedder.combine_text_columns(row, header)
                documents.append(
                    Document(
                        page_content=content,
                        metadata={"index": index, "filename": f.filename}
                    )
                )
            vector_db.add_documents(documents)

        else:
            # Nếu là file khác: tạo Document từ dict vừa thêm
            docs = [
                Document(
                    page_content=file_dicts[-1]["content"],  # chỉ lấy file hiện tại
                    metadata={"name": file_dicts[-1]["name"]}
                )
            ]
            vector_db.add_documents(docs)
"""


