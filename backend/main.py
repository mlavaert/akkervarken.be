from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Akkervarken API", version="1.0.0")

# CORS setup - allow requests from your website
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://akkervarken.be").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Akkervarken API is running!",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
def health_check():
    """Health check endpoint for Railway"""
    return {"status": "ok"}
