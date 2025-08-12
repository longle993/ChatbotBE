from fastapi import APIRouter, Depends
from core.use_case.ChatWithGemini import ChatWithGemini
from core.entity.Chat import ChatMessage
from infrastructure.LLM.GeminiService import GeminiLLMService
from infrastructure.VectorDB.VectorDBService import VectorDBService

router = APIRouter()

@router.post("/chat")
def chat_endpoint(question: str):
    llm_service = GeminiLLMService()
    vector_service = VectorDBService()
    use_case = ChatWithGemini(llm_service, vector_service)

    history = []
    answer = use_case.execute(question, history)

    return {
        "code": 200,
        "isSuccess": True,
        "message": "Success",
        "data": answer
    }
