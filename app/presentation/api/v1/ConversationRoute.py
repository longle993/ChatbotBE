from fastapi import APIRouter, Depends, Request, Query, HTTPException, status
from presentation.schema.Conversation import CreateConversationRequest, CreateConversationResponse, GetConversationResponse
from infrastructure.repository.ConversationRepositoryMongo import ConversationRepositoryMongo
from infrastructure.db.Mongo import get_conversation_collection
from core.use_case.CreateConversation import CreateConversation
from core.use_case.GetConversation import GetConversation
from core.entity.Response import ApiResponse
from security import (
    require_csrf,
    decode_jwt
)


router = APIRouter()
@router.get("/")
async def get_conversations(
    request: Request,
    id: str = Query(...),
    username: str = Query(None),
    collection=Depends(get_conversation_collection)
):
    require_csrf(request)
    decode_jwt(request)
    repo = ConversationRepositoryMongo(collection)
    use_case = GetConversation(repo)

    conversations = await use_case.execute(id)
    return GetConversationResponse.from_entity(
        ApiResponse.success(conversations)
    )

@router.post("/create", response_model=CreateConversationResponse)
async def create_conversation(
    req: CreateConversationRequest, 
    request: Request,
    collection=Depends(get_conversation_collection)
):
    try:
        require_csrf(request)
        payload = decode_jwt(request)
        user_id = payload.get("sub")
        

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or missing token")
        
        repo = ConversationRepositoryMongo(collection)
        use_case = CreateConversation(repo)

        conversation = await use_case.execute(
            user_id,
            req.title,
            req.messages
        )
        print(conversation)
        if not conversation:
            return CreateConversationResponse.from_entity(
                ApiResponse.error("Conversation creation failed")
            )

        return CreateConversationResponse.from_entity(
            ApiResponse.success(conversation)
        )

    except Exception as e:
        print(f"Error creating conversation: {e}")
        return CreateConversationResponse.from_entity(
            ApiResponse.error(f"Internal server error: {str(e)}")
        )


