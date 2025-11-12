"""Card API endpoints"""

from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models.card import (
    Card,
    CardCreate,
    CardUpdate,
    CardBatchCreate,
    CardResponse,
    CardListResponse
)
from app.services.card_service import CardService

router = APIRouter()
card_service = CardService()


@router.get("/{deck_id}/cards", response_model=CardListResponse)
async def list_cards(deck_id: str):
    """List all cards in a deck"""
    try:
        cards = card_service.list_cards(deck_id)
        return CardListResponse(
            success=True,
            count=len(cards),
            cards=cards
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing cards: {str(e)}"
        )


@router.post("/{deck_id}/cards", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
async def create_card(deck_id: str, card_data: CardCreate):
    """Add a new card to a deck"""
    try:
        card = card_service.create_card(deck_id, card_data)
        return CardResponse(
            success=True,
            message="Card created successfully",
            card=card
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating card: {str(e)}"
        )


@router.post("/{deck_id}/cards/batch", response_model=CardListResponse, status_code=status.HTTP_201_CREATED)
async def create_cards_batch(deck_id: str, batch_data: CardBatchCreate):
    """Add multiple cards to a deck at once"""
    try:
        cards = card_service.create_cards_batch(deck_id, batch_data.cards)
        return CardListResponse(
            success=True,
            count=len(cards),
            cards=cards
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating cards: {str(e)}"
        )


@router.put("/{deck_id}/cards/{card_id}", response_model=CardResponse)
async def update_card(deck_id: str, card_id: int, card_data: CardUpdate):
    """Update a card in a deck"""
    try:
        card = card_service.update_card(deck_id, card_id, card_data)
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Card {card_id} not found in deck '{deck_id}'"
            )
        return CardResponse(
            success=True,
            message="Card updated successfully",
            card=card
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating card: {str(e)}"
        )


@router.delete("/{deck_id}/cards/{card_id}", response_model=CardResponse)
async def delete_card(deck_id: str, card_id: int):
    """Delete a card from a deck"""
    try:
        success = card_service.delete_card(deck_id, card_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Card {card_id} not found in deck '{deck_id}'"
            )
        return CardResponse(
            success=True,
            message="Card deleted successfully",
            card=None
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting card: {str(e)}"
        )
