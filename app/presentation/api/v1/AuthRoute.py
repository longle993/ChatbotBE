from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from secrets import token_urlsafe
from datetime import timedelta
from datetime import datetime, timezone

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

from presentation.schema.Login import LoginUserRequest, LoginUserResponse
from core.entity.Response import ApiResponse
from infrastructure.db.Mongo import get_user_collection
from infrastructure.repository.UserRepositoryMongo import UserRepositoryMongo
from core.use_case.LoginUser import LoginUser
from presentation.schema.Auth import AuthResponse


router = APIRouter()

@router.get("/csrf")
async def get_csrf_token(response: Response):
    csrf = token_urlsafe(32)
    set_csrf_cookie(response, csrf, same_site="None", secure=True)
    return ApiResponse.success({"csrf": csrf})

# Endpoint refresh token cải thiện
@router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    payload = decode_jwt(refresh_token, token_type="refresh")
    
    sub = payload["sub"]
    access_exp = timedelta(minutes=ACCESS_EXPIRE_MIN)
    new_access = create_jwt(sub, access_exp, "access")
    
    set_jwt_cookies(response, new_access, None, same_site="None", secure=True)
    
    # Tính toán thời gian expire chính xác
    now = datetime.now(timezone.utc)
    exp_timestamp = int((now + access_exp).timestamp())
    
    return AuthResponse.from_entity(
        ApiResponse.success({
            "exp": exp_timestamp,
            "message": "Access token refreshed successfully"
        })
    )

@router.post("/login", response_model=LoginUserResponse)
async def login_user(
    req: LoginUserRequest,
    request: Request,
    response: Response,
    collection=Depends(get_user_collection)
):
    try:
        require_csrf(request)
        repo = UserRepositoryMongo(collection)
        use_case = LoginUser(repo)
        user = await use_case.execute(req.username, req.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Thời gian sống của token
        print(ACCESS_EXPIRE_MIN)
        access_exp = timedelta(minutes=ACCESS_EXPIRE_MIN)
        refresh_exp = timedelta(days=REFRESH_EXPIRE_DAYS)

        # Tạo JWT
        
        access = create_jwt(str(user.id), access_exp, "access")
        refresh = create_jwt(str(user.id), refresh_exp, "refresh")
        
        # Set cookie HttpOnly
        set_jwt_cookies(response, access, refresh, same_site="None", secure=True)

        # Trả thông tin user
        return LoginUserResponse.from_entity(
            ApiResponse.success(user)
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error logging in user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/logout")
async def logout(response: Response):
    clear_jwt_cookies(response, same_site="None", secure=True)
    return AuthResponse.success("Logged out successfully")