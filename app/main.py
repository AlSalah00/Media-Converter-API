from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routes import convert
from app.services.security import ApiKeyDep

# Create FastAPI app with global API key security
app = FastAPI(
    title="Media Converter API",
    version="1.0.0",
    description="A simple REST API for media file conversion using FFmpeg",
    dependencies=[ApiKeyDep]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow requests from anywhere
    allow_credentials=True,
    allow_methods=["*"],      # allow GET, POST, etc.
    allow_headers=["Authorization", "Content-Type"],  # allow the API key and JSON headers
)

# Include routes
app.include_router(convert.router)

# Public health check (no API key)
@app.get("/health", include_in_schema=False)
def health_check():
    return {"status": "ok"}
