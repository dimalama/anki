"""Import service - Business logic for importing data"""

import pandas as pd
import io
from typing import Optional
from pathlib import Path

from app.models.deck import Deck
from app.services.deck_service import DeckService
from app.services.card_service import CardService
from app.models.card import CardCreate


class ImportService:
    """Service for importing cards from various sources"""

    def __init__(self):
        self.deck_service = DeckService()
        self.card_service = CardService()

    def import_from_csv(
        self,
        content: bytes,
        filename: str,
        deck_name: Optional[str] = None,
        language: str = "spanish",
        card_type: str = "basic"
    ) -> Deck:
        """Import cards from CSV content"""

        # Use filename as deck name if not provided
        if not deck_name:
            deck_name = Path(filename).stem

        # Parse CSV
        try:
            df = pd.read_csv(io.BytesIO(content))
        except Exception as e:
            raise ValueError(f"Invalid CSV format: {str(e)}")

        # Validate CSV has data
        if df.empty:
            raise ValueError("CSV file is empty")

        # Save CSV to csv directory
        deck_id = deck_name.lower().replace(' ', '_')
        csv_path = self.deck_service._get_csv_path(deck_id)

        # Save the uploaded CSV
        df.to_csv(csv_path, index=False)

        # Load and return deck metadata
        deck = self.deck_service._load_deck_metadata(deck_id)
        if not deck:
            raise ValueError("Failed to create deck from CSV")

        return deck

    def import_from_text(
        self,
        text: str,
        deck_name: str,
        language: str = "spanish",
        separator: str = "\t",
        card_type: str = "basic"
    ) -> Deck:
        """Import cards from plain text"""

        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]

        if not lines:
            raise ValueError("No valid lines found in text")

        # Parse lines
        cards_data = []
        for line in lines:
            parts = line.split(separator)
            if len(parts) >= 2:
                if card_type == "cloze":
                    cards_data.append({
                        'Text': parts[0],
                        'Translation': parts[1] if len(parts) > 1 else '',
                        'Explanation': parts[2] if len(parts) > 2 else ''
                    })
                else:
                    cards_data.append({
                        'Front': parts[0],
                        'Back': parts[1]
                    })

        if not cards_data:
            raise ValueError("No valid card data found in text")

        # Create deck
        deck_id = deck_name.lower().replace(' ', '_')
        csv_path = self.deck_service._get_csv_path(deck_id)

        # Create CSV from data
        df = pd.DataFrame(cards_data)
        df.to_csv(csv_path, index=False)

        # Load and return deck metadata
        deck = self.deck_service._load_deck_metadata(deck_id)
        if not deck:
            raise ValueError("Failed to create deck from text")

        return deck
