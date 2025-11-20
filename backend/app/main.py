"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from pathlib import Path

from app.api.endpoints import decks, cards, templates, import_export, tags
from app.core.config import settings

# Create FastAPI app
app = FastAPI(
    title="Anki Deck Generator API",
    description="API for creating and managing Anki flashcard decks",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(decks.router, prefix="/api/v1/decks", tags=["decks"])
app.include_router(cards.router, prefix="/api/v1/cards", tags=["cards"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["templates"])
app.include_router(import_export.router, prefix="/api/v1/import", tags=["import/export"])
app.include_router(tags.router, prefix="/api/v1/tags", tags=["tags"])

# Mount static files (for generated .apkg files)
apkg_dir = Path(__file__).parent.parent.parent / "apkg"
apkg_dir.mkdir(exist_ok=True)
app.mount("/static/apkg", StaticFiles(directory=str(apkg_dir)), name="apkg")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Anki Deck Generator API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
