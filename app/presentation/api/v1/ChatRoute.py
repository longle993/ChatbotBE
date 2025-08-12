from fastapi import APIRouter, Depends
from core.use_case.ChatWithGemini import ChatWithGemini
from core.entity.Chat import Message
from infrastructure.LLM.GeminiService import GeminiLLMService
from infrastructure.VectorDB.VectorDBService import VectorDBService
from presentation.schema.Chat import CreateChatRequest, CreateChatResponse 
    
router = APIRouter()

@router.post("/message")
def chat_endpoint(req: CreateChatRequest):
    llm_service = GeminiLLMService()
    vector_service = VectorDBService()
    use_case = ChatWithGemini(llm_service, vector_service)

    history = []
    answer = use_case.execute(req.message, history)

    return CreateChatResponse(
        code=200,
        isSuccess=True,
        message="Success",
        data=answer
    )