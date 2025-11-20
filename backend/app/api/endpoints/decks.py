"""Deck API endpoints"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from typing import List, Optional
import os

from app.models.deck import (
    Deck,
    DeckCreate,
    DeckUpdate,
    DeckResponse,
    DeckListResponse
)
from app.services.deck_service import DeckService

router = APIRouter()
deck_service = DeckService()


@router.get("", response_model=DeckListResponse)
async def list_decks(
    language: Optional[str] = None,
    tag: Optional[str] = None
):
    """
    List all available decks.

    Optional filters:
    - language: Filter by language
    - tag: Filter by tag
    """
    try:
        decks = deck_service.list_decks(language=language, tag=tag)
        return DeckListResponse(
            success=True,
            count=len(decks),
            decks=decks
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing decks: {str(e)}"
        )


@router.get("/{deck_id}", response_model=DeckResponse)
async def get_deck(deck_id: str):
    """Get a specific deck by ID"""
    try:
        deck = deck_service.get_deck(deck_id)
        if not deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deck '{deck_id}' not found"
            )
        return DeckResponse(
            success=True,
            message="Deck retrieved successfully",
            deck=deck
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving deck: {str(e)}"
        )


@router.post("", response_model=DeckResponse, status_code=status.HTTP_201_CREATED)
async def create_deck(deck_data: DeckCreate):
    """Create a new deck"""
    try:
        deck = deck_service.create_deck(deck_data)
        return DeckResponse(
            success=True,
            message="Deck created successfully",
            deck=deck
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating deck: {str(e)}"
        )


@router.put("/{deck_id}", response_model=DeckResponse)
async def update_deck(deck_id: str, deck_data: DeckUpdate):
    """Update an existing deck"""
    try:
        deck = deck_service.update_deck(deck_id, deck_data)
        if not deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deck '{deck_id}' not found"
            )
        return DeckResponse(
            success=True,
            message="Deck updated successfully",
            deck=deck
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating deck: {str(e)}"
        )


@router.delete("/{deck_id}", response_model=DeckResponse)
async def delete_deck(deck_id: str):
    """Delete a deck"""
    try:
        success = deck_service.delete_deck(deck_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deck '{deck_id}' not found"
            )
        return DeckResponse(
            success=True,
            message="Deck deleted successfully",
            deck=None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting deck: {str(e)}"
        )


@router.post("/{deck_id}/generate", response_model=DeckResponse)
async def generate_deck(deck_id: str):
    """Generate .apkg file for a deck"""
    try:
        deck = deck_service.generate_apkg(deck_id)
        if not deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deck '{deck_id}' not found"
            )
        return DeckResponse(
            success=True,
            message="Deck generated successfully",
            deck=deck
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating deck: {str(e)}"
        )


@router.get("/{deck_id}/download")
async def download_deck(deck_id: str):
    """Download .apkg file for a deck"""
    try:
        apkg_path = deck_service.get_apkg_path(deck_id)
        if not apkg_path or not os.path.exists(apkg_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"APKG file for deck '{deck_id}' not found. Generate it first."
            )

        return FileResponse(
            path=apkg_path,
            filename=os.path.basename(apkg_path),
            media_type="application/octet-stream"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading deck: {str(e)}"
        )
