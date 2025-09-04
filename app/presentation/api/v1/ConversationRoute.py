from fastapi import APIRouter, Depends, Request, Query, HTTPException, status
from presentation.schema.User import CreateUserRequest, CreateUserResponse, GetUserRequest, GetUserResponse
from core.use_case.CreateUser import CreateUser
from core.use_case.GetUser import GetUser
from infrastructure.repository.UserRepositoryMongo import UserRepositoryMongo
from infrastructure.db.Mongo import get_user_collection
from core.entity.Response import ApiResponse
from security import (
    require_csrf,
    set_csrf_cookie,
    decode_jwt,
    create_jwt,
    set_jwt_cookies,
    clear_jwt_cookies,
    ACCESS_EXPIRE_MIN,
    REFRESH_EXPIRE_DAYS,
)


router = APIRouter()

@router.get("/")
async def get_users(
    request: Request,
    id: str = Query(...),
    role: str = Query(...),
    username: str = Query(None),
    collection=Depends(get_user_collection)
):
    require_csrf(request)
    decode_jwt(request)
    repo = UserRepositoryMongo(collection)
    use_case = GetUser(repo)

    users = await use_case.execute(role, id, username)
    return GetUserResponse.from_entity(
        ApiResponse.success(users)
    )

@router.post("/", response_model=CreateUserResponse)
async def create_user(
    req: CreateUserRequest, 
    request: Request,
    collection=Depends(get_user_collection)
):
    try:
        require_csrf(request)
        decode_jwt(request)
        
        repo = UserRepositoryMongo(collection)
        use_case = CreateUser(repo)
        
        user = await use_case.execute(
            req.username, 
            req.password, 
            req.full_name, 
            req.email
        )
        print(user)
        if not user:
            return CreateUserResponse.from_entity(
                ApiResponse.error("User creation failed")
            )

        return CreateUserResponse.from_entity(
            ApiResponse.success(user)
        )

    except Exception as e:
        print(f"Error creating user: {e}")
        return CreateUserResponse.from_entity(
            ApiResponse.error(f"Internal server error: {str(e)}")
        )


