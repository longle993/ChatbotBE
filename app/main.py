from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from presentation.api.v1.UserRoute import router as user_router
from presentation.api.v1.EmbedRoute import router as embed_router
from presentation.api.v1.ChatRoute import router as chat_router
from presentation.api.v1.AuthRoute import router as auth_router
from presentation.api.v1.ConversationRoute import router as conversation_router

app = FastAPI()

#Exception Handler toàn cục
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "isSuccess": False,
            "message": str(exc.detail),
            "data": None
        }
    )
    
#Enable All CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=[    
        "http://localhost:5173",   
        "http://127.0.0.1:5173" 
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(embed_router, prefix="/embed", tags=["embed"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(conversation_router, prefix="/conversations", tags=["conversations"])
