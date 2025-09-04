from fastapi import APIRouter, Depends, Request, HTTPException, status
from core.use_case.ChatWithGemini import ChatWithGemini
from infrastructure.LLM.GeminiService import GeminiLLMService
from infrastructure.LLM.ClaudeService import ClaudeLLMService
from infrastructure.VectorDB.GeminiFaiss import GeminiFaiss
from infrastructure.VectorDB.Qwen3Faiss import Qwen3Faiss
from presentation.schema.Chat import CreateChatRequest, CreateChatResponse
from security import decode_jwt, require_csrf
from core.entity.Chat import Message
from datetime import datetime

router = APIRouter()
llm_service = ClaudeLLMService()
vector_service = Qwen3Faiss()
chat_histories: dict[str, list[Message]] = {}

@router.post("/")
async def chat_endpoint(req: CreateChatRequest, request: Request):
    require_csrf(request)
    payload = decode_jwt(request)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    # Lấy history của user, nếu chưa có thì tạo list rỗng
    history = chat_histories.get(user_id, [])

    use_case = ChatWithGemini(llm_service, vector_service)
    answer = use_case.execute(req.message, history)

    # Cập nhật history với Message
    history.append(Message(role="user", content=req.message, timestamp=datetime.utcnow()))
    history.append(Message(role="assistant", content=answer, timestamp=datetime.utcnow()))

    chat_histories[user_id] = history

    return CreateChatResponse(
        code=200,
        isSuccess=True,
        message="Success",
        data=answer
    )
