"""Import/Export API endpoints"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Form
from typing import Optional
import csv
import io

from app.models.deck import DeckResponse
from app.services.import_service import ImportService

router = APIRouter()
import_service = ImportService()


@router.post("/csv", response_model=DeckResponse)
async def import_csv(
    file: UploadFile = File(...),
    deck_name: Optional[str] = Form(None),
    language: str = Form("spanish"),
    card_type: str = Form("basic"),
    column_format: Optional[str] = Form(None)
):
    """
    Import cards from a CSV file.

    The CSV should have headers that define the card fields.

    Column formats available:
    - 2col: English, [Language]
    - 3col: English, [Language], Example
    - 4col: English, [Language], Example, Notes
    - front_back: Front, Back (generic)
    - cloze: Text, Translation, Explanation
    - cloze_notes: Text, Translation, Explanation, Notes
    """
    try:
        # Validate file type
        if not (file.filename.endswith('.csv') or file.filename.endswith('.tsv')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a CSV or TSV file"
            )

        # Read file content
        content = await file.read()

        # Import and create deck
        deck = import_service.import_from_csv(
            content=content,
            filename=file.filename,
            deck_name=deck_name,
            language=language,
            card_type=card_type,
            column_format=column_format
        )

        return DeckResponse(
            success=True,
            message=f"Successfully imported {deck.card_count} cards",
            deck=deck
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing CSV: {str(e)}"
        )


@router.post("/text", response_model=DeckResponse)
async def import_text(
    text: str = Form(...),
    deck_name: str = Form(...),
    language: str = Form("spanish"),
    separator: str = Form("\t"),
    card_type: str = Form("basic"),
    column_format: Optional[str] = Form(None)
):
    """
    Import cards from plain text.

    Format: Each line should be columns separated by the separator.
    Default separator is tab.

    Column formats available:
    - 2col: English, [Language]
    - 3col: English, [Language], Example
    - 4col: English, [Language], Example, Notes
    - front_back: Front, Back (generic)
    - cloze: Text, Translation, Explanation
    - cloze_notes: Text, Translation, Explanation, Notes

    If not specified, auto-detects based on number of columns.
    """
    try:
        deck = import_service.import_from_text(
            text=text,
            deck_name=deck_name,
            language=language,
            separator=separator,
            card_type=card_type,
            column_format=column_format
        )

        return DeckResponse(
            success=True,
            message=f"Successfully imported {deck.card_count} cards",
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
            detail=f"Error importing text: {str(e)}"
        )
