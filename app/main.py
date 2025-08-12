from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from presentation.api.v1.UserRoute import router as user_router

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
