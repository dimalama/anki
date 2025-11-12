"""Deck models"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class DeckBase(BaseModel):
    """Base deck model"""
    name: str = Field(..., min_length=1, max_length=200, description="Deck name")
    language: str = Field(default="spanish", description="Primary language for the deck")
    description: Optional[str] = Field(None, description="Deck description")
    tags: List[str] = Field(default_factory=list, description="Tags for the deck")


class DeckCreate(DeckBase):
    """Model for creating a new deck"""
    card_type: str = Field(default="basic", description="Card type: basic, cloze, or reversed")


class DeckUpdate(BaseModel):
    """Model for updating a deck"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    language: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class Deck(DeckBase):
    """Complete deck model with metadata"""
    id: str = Field(..., description="Unique deck identifier (filename without extension)")
    card_type: str = Field(..., description="Card type: basic, cloze, or reversed")
    card_count: int = Field(default=0, description="Number of cards in deck")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    csv_path: str = Field(..., description="Path to CSV file")
    apkg_path: Optional[str] = Field(None, description="Path to generated APKG file")

    class Config:
        from_attributes = True


class DeckResponse(BaseModel):
    """API response model for deck operations"""
    success: bool
    message: str
    deck: Optional[Deck] = None


class DeckListResponse(BaseModel):
    """API response model for listing decks"""
    success: bool
    count: int
    decks: List[Deck]
