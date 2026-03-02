from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models  # noqa: F401 — ensures tables are created on startup
from routes import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sowvox.netlify.app",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
