from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from presentation.api.v1.UserRoute import router as user_router
from presentation.api.v1.EmbedRoute import router as embed_router
from presentation.api.v1.ChatRoute import router as chat_router

app = FastAPI()

#Enable All CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(embed_router, prefix="/embed", tags=["embed"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])
