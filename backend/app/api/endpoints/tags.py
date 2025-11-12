"""Tags API endpoints"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from pydantic import BaseModel

router = APIRouter()


class TagsResponse(BaseModel):
    """Response model for tags"""
    success: bool
    tags: List[str]


class TagSuggestion(BaseModel):
    """Tag suggestion model"""
    tag: str
    count: int


class TagSuggestionsResponse(BaseModel):
    """Response model for tag suggestions"""
    success: bool
    suggestions: List[TagSuggestion]


@router.get("", response_model=TagsResponse)
async def list_tags():
    """Get all available tags from existing decks"""
    try:
        # TODO: Implement tag extraction from all decks
        # For now, return common language learning tags
        common_tags = [
            "spanish", "english", "french", "german",
            "vocabulary", "grammar", "verb", "noun",
            "present", "past", "future", "cloze", "basic"
        ]
        return TagsResponse(success=True, tags=common_tags)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing tags: {str(e)}"
        )


@router.get("/suggest", response_model=TagSuggestionsResponse)
async def suggest_tags(filename: str = "", content: str = ""):
    """
    Get tag suggestions based on filename or content.

    This endpoint analyzes the filename and/or content to suggest relevant tags.
    """
    try:
        suggestions = []

        # Simple tag suggestion logic based on keywords
        keywords = {
            "verb": ["verb", "conjugation", "tense"],
            "noun": ["noun", "sustantivo"],
            "vocabulary": ["vocab", "word", "dictionary"],
            "grammar": ["grammar", "structure"],
            "present": ["present", "presente"],
            "past": ["past", "preterite", "imperfect", "pasado"],
            "future": ["future", "futuro"],
        }

        text = (filename + " " + content).lower()

        for tag, patterns in keywords.items():
            if any(pattern in text for pattern in patterns):
                suggestions.append(TagSuggestion(tag=tag, count=1))

        return TagSuggestionsResponse(success=True, suggestions=suggestions)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error suggesting tags: {str(e)}"
        )
