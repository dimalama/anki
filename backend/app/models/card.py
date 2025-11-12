"""Card models"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


class CardBase(BaseModel):
    """Base card model"""
    fields: Dict[str, str] = Field(..., description="Card fields as key-value pairs")
    tags: List[str] = Field(default_factory=list, description="Card-specific tags")


class CardCreate(CardBase):
    """Model for creating a new card"""
    pass


class CardUpdate(BaseModel):
    """Model for updating a card"""
    fields: Optional[Dict[str, str]] = None
    tags: Optional[List[str]] = None


class Card(CardBase):
    """Complete card model with metadata"""
    id: int = Field(..., description="Card index in deck")
    deck_id: str = Field(..., description="Parent deck ID")

    class Config:
        from_attributes = True


class CardBatchCreate(BaseModel):
    """Model for batch creating cards"""
    cards: List[CardCreate] = Field(..., description="List of cards to create")


class CardResponse(BaseModel):
    """API response model for card operations"""
    success: bool
    message: str
    card: Optional[Card] = None


class CardListResponse(BaseModel):
    """API response model for listing cards"""
    success: bool
    count: int
    cards: List[Card]
