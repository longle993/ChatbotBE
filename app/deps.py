# app/deps.py
from fastapi import Depends, Request, HTTPException, status
from app.security import decode_jwt, ACCESS_COOKIE_NAME

def get_current_user_sub(request: Request) -> str:
    token = request.cookies.get(ACCESS_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing access token")
    payload = decode_jwt(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    return payload["sub"]
