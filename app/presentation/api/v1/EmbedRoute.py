import base64
from fastapi import APIRouter, UploadFile, File, Request
from core.use_case.EmbedFile import EmbedFilesUseCase
from infrastructure.embedding.EmbeddingService import GoogleEmbeddingService
from infrastructure.VectorDB.FaissVectorDB import FAISSVectorDB
from security import (
    require_csrf,
    decode_jwt,
)
router = APIRouter()

@router.post("/")
async def embed_files(
    request: Request,
    files: list[UploadFile] = File(...)
):
    require_csrf(request)
    user_id = decode_jwt(request)
    print('loglog')
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
 
    use_case = EmbedFilesUseCase(embedder, vector_db)
    count = use_case.execute(file_dicts)
 
    return {
        "code": 200,
        "isSuccess": True,
        "message": f"Embedded {count} file(s) successfully",
        "data": None
    }
