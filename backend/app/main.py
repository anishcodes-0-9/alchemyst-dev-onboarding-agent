from __future__ import annotations
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.routers import chat, session, codegen

app = FastAPI(title="Alchemyst Dev Onboarding Agent")

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(session.router, prefix="/api")
app.include_router(codegen.router, prefix="/api")


@app.get("/")
def root():
    return {"status": "Backend running"}