from fastapi import FastAPI, Depends
from app.routes import convert
from app.services.security import ApiKeyDep

# Create FastAPI app with global API key security
app = FastAPI(
    title="Media Converter API",
    version="1.0.0",
    description="A simple REST API for media file conversion using FFmpeg",
    dependencies=[ApiKeyDep]
)

# Include routes
app.include_router(convert.router)

# Public health check (no API key)
@app.get("/health", include_in_schema=False)
def health_check():
    return {"status": "ok"}