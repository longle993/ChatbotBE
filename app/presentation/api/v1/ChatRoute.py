from fastapi import APIRouter, Depends, Request, HTTPException, status
from core.use_case.ChatWithGemini import ChatWithGemini
from infrastructure.LLM.GeminiService import GeminiLLMService
from infrastructure.LLM.ClaudeService import ClaudeLLMService
from infrastructure.VectorDB.GeminiFaiss import GeminiFaiss
from infrastructure.VectorDB.Qwen3Faiss import Qwen3Faiss
from presentation.schema.Chat import CreateChatRequest, CreateChatResponse
from security import decode_jwt, require_csrf

router = APIRouter()
llm_service = ClaudeLLMService()
vector_service = Qwen3Faiss()
@router.post("/")
async def chat_endpoint(
    req: CreateChatRequest,
    request: Request
):
    require_csrf(request)
    payload = decode_jwt(request)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token"
        )
 
    use_case = ChatWithGemini(llm_service, vector_service)

    history = []
    answer = use_case.execute(req.message, history)

    return CreateChatResponse(
        code=200,
        isSuccess=True,
        message="Success",
        data=answer
    )
