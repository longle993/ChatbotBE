from fastapi import APIRouter, UploadFile
from application.use_cases.embed_files import EmbedFilesUseCase
from infrastructure.embedding.google_embedding_service import GoogleEmbeddingService
from infrastructure.vector_db.faiss_service import FAISSVectorDB

router = APIRouter()

@router.post("/embed")
async def embed_files(files: list[UploadFile]):
    embedder = GoogleEmbeddingService()
    vector_db = FAISSVectorDB()

    file_dicts = []
    for f in files:
        file_dicts.append({
            "name": f.filename,
            "bytes": await f.read()
        })

    use_case = EmbedFilesUseCase(embedder, vector_db)
    count = use_case.execute(file_dicts)

    return {
        "code": 200,
        "isSuccess": True,
        "message": f"Embedded {count} file(s) successfully",
        "data": None
    }
