from fastapi import APIRouter, Depends, Request, HTTPException, status
from infrastructure.repository.FileRepository import FileRepository
from core.use_case.ChatWithGemini import ChatWithGemini
from infrastructure.LLM.GeminiService import GeminiLLMService
from infrastructure.LLM.ClaudeService import ClaudeLLMService
from infrastructure.VectorDB.GeminiFaiss import GeminiFaiss
from infrastructure.VectorDB.Qwen3Faiss import Qwen3Faiss
from presentation.schema.Chat import CreateChatRequest, CreateChatResponse
from security import decode_jwt, require_csrf
from core.entity.Chat import Message
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import UploadFile, Form, File

router = APIRouter()
llm_service = ClaudeLLMService()
vector_service = Qwen3Faiss()
chat_histories: dict[str, list[Message]] = {}

async def parse_chat_request(
    message: str = Form(...),
    files: List[UploadFile] = File(default=[])
) -> CreateChatRequest:
    """
    Dependency để parse multipart/form-data thành CreateChatRequest
    """
    return CreateChatRequest(message=message, files=files if files else [])

@router.post("/") 
async def chat_endpoint(
    request: Request,
    req: CreateChatRequest = Depends(parse_chat_request)
):
    require_csrf(request)
    payload = decode_jwt(request)
    user_id = payload.get("sub")
    

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    
    history = chat_histories.get(user_id, [])
    
    file_repo = FileRepository()
    use_case = ChatWithGemini(llm_service, vector_service, file_repo)

    answer = use_case.execute(req.message, history, req.files)

    history.append(Message(role="user", content=req.message, timestamp=datetime.now(timezone.utc)))
    history.append(Message(role="assistant", content=answer, timestamp=datetime.now(timezone.utc)))

    chat_histories[user_id] = history
    
    return CreateChatResponse(
        code=200,
        isSuccess=True,
        message="Success",
        data=answer
    )