import base64
from fastapi import APIRouter, UploadFile, File, Request
import io
from core.use_case.EmbedFile import EmbedFilesUseCase
#from infrastructure.repository.EmbeddingRepository import GoogleEmbeddingService
from infrastructure.VectorDB.GeminiFaiss import GeminiFaiss
from infrastructure.VectorDB.Qwen3Faiss import Qwen3Faiss
from presentation.schema.Embedder import EmbedderResponse
from core.entity.Response import ApiResponse
from security import (
    require_csrf,
    decode_jwt,
)
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
    embedder = Qwen3Faiss()
    use_case = EmbedFilesUseCase(file_repo, embedder)
    isSuccess = use_case.execute(files)
    if isSuccess:
        return EmbedderResponse.from_entity(ApiResponse.success(isSuccess))
    return EmbedderResponse.from_entity(ApiResponse.error("Embedding failed"))

