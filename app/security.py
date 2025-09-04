# app/security.py - Phiên bản cải thiện
from datetime import datetime, timedelta, timezone
from typing import Optional, Union
import jwt
from fastapi import Response, Request, HTTPException, status
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_EXPIRE_MIN = 15
REFRESH_EXPIRE_DAYS = 7

ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"

def create_jwt(sub: str, expires_delta: timedelta, token_type="access") -> str:
    now = datetime.now(timezone.utc)
    
    payload = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "type": token_type,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Cải thiện: Hàm decode linh hoạt hơn
def decode_jwt(token_or_request: Union[str, Request], token_type: str = "access") -> dict:
    """
    Decode JWT token từ string hoặc từ request cookies
    """
    if isinstance(token_or_request, str):
        # Trường hợp truyền vào là token string
        token = token_or_request
    else:
        # Trường hợp truyền vào là Request object
        cookie_name = ACCESS_COOKIE_NAME if token_type == "access" else REFRESH_COOKIE_NAME
        token = token_or_request.cookies.get(cookie_name)
        
        if not token:
            token_name = "access token" if token_type == "access" else "refresh token"
            raise HTTPException(status_code=401, detail=f"Missing {token_name}")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Kiểm tra token type nếu được chỉ định
        if token_type and payload.get("type") != token_type:
            raise HTTPException(status_code=401, detail="Invalid token type")
            
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Thêm hàm helper để decode refresh token
def decode_refresh_token(request: Request) -> dict:
    """Helper function để decode refresh token từ cookies"""
    return decode_jwt(request, token_type="refresh")

def set_jwt_cookies(
    resp: Response,
    access_token: str,
    refresh_token: Optional[str] = None,
    *,
    same_site="None",
    secure=True,
    domain: Optional[str] = None
):
    resp.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=secure,
        samesite=same_site,
        max_age=ACCESS_EXPIRE_MIN * 60,
        path="/",
        domain=domain
    )
    if refresh_token:
        resp.set_cookie(
            key=REFRESH_COOKIE_NAME,
            value=refresh_token,
            httponly=True,
            secure=secure,
            samesite=same_site,
            max_age=REFRESH_EXPIRE_DAYS * 24 * 3600,
            path="/",
            domain=domain
        )

def clear_jwt_cookies(resp: Response, *, same_site="None", secure=True, domain: Optional[str] = None):
    resp.delete_cookie(ACCESS_COOKIE_NAME, path="/", domain=domain, samesite=same_site)
    resp.delete_cookie(REFRESH_COOKIE_NAME, path="/", domain=domain, samesite=same_site)
    resp.delete_cookie(CSRF_COOKIE_NAME, path="/", domain=domain, samesite=same_site)

def set_csrf_cookie(resp: Response, token: str, *, same_site="None", secure=True, domain: Optional[str] = None):
    resp.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=token,
        httponly=False,
        secure=secure,
        samesite=same_site,
        max_age=REFRESH_EXPIRE_DAYS * 24 * 3600,
        path="/",
        domain=domain,
    )

def require_csrf(request: Request):
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
        header_token = request.headers.get(CSRF_HEADER_NAME)
        
        if not cookie_token or not header_token or cookie_token != header_token:
            raise HTTPException(status_code=403, detail="CSRF token invalid")