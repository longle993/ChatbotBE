from fastapi import APIRouter, Depends
from presentation.schema.User import CreateUserRequest, CreateUserResponse, LoginUserRequest, LoginUserResponse
from core.use_case.CreateUser import CreateUser
from core.use_case.LoginUser import LoginUser
from infrastructure.repository.UserRepositoryMongo import UserRepositoryMongo
from infrastructure.db.Mongo import get_user_collection
from core.entity.Response import ApiResponse

router = APIRouter()

@router.post("/", response_model=CreateUserResponse)
async def create_user(
    req: CreateUserRequest, 
    collection=Depends(get_user_collection)
):
    try:
        repo = UserRepositoryMongo(collection)
        use_case = CreateUser(repo)
        
        user = await use_case.execute(
            req.id,
            req.username, 
            req.password, 
            req.full_name, 
            req.email
        )

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


