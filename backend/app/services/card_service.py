"""Card service - Business logic for card operations"""

import pandas as pd
from typing import List, Optional
from pathlib import Path

from app.models.card import Card, CardCreate, CardUpdate
from app.services.deck_service import DeckService


class CardService:
    """Service for managing cards within decks"""

    def __init__(self):
        self.deck_service = DeckService()

    def _load_csv(self, deck_id: str) -> pd.DataFrame:
        """Load CSV file for a deck"""
        csv_path = self.deck_service._get_csv_path(deck_id)
        if not csv_path.exists():
            raise ValueError(f"Deck '{deck_id}' not found")
        return pd.read_csv(csv_path)

    def _save_csv(self, deck_id: str, df: pd.DataFrame) -> None:
        """Save CSV file for a deck"""
        csv_path = self.deck_service._get_csv_path(deck_id)
        df.to_csv(csv_path, index=False)

    def list_cards(self, deck_id: str) -> List[Card]:
        """List all cards in a deck"""
        df = self._load_csv(deck_id)
        cards = []

        for idx, row in df.iterrows():
            fields = row.to_dict()
            # Convert NaN to empty string
            fields = {k: (v if pd.notna(v) else "") for k, v in fields.items()}

            cards.append(Card(
                id=int(idx),
                deck_id=deck_id,
                fields=fields,
                tags=[]
            ))

        return cards

    def get_card(self, deck_id: str, card_id: int) -> Optional[Card]:
        """Get a specific card from a deck"""
        df = self._load_csv(deck_id)

        if card_id < 0 or card_id >= len(df):
            return None

        row = df.iloc[card_id]
        fields = row.to_dict()
        fields = {k: (v if pd.notna(v) else "") for k, v in fields.items()}

        return Card(
            id=card_id,
            deck_id=deck_id,
            fields=fields,
            tags=[]
        )

    def create_card(self, deck_id: str, card_data: CardCreate) -> Card:
        """Add a new card to a deck"""
        df = self._load_csv(deck_id)

        # Validate that all required columns are present
        for col in df.columns:
            if col not in card_data.fields:
                # Fill missing columns with empty string
                card_data.fields[col] = ""

        # Add new row
        new_row = pd.DataFrame([card_data.fields])
        df = pd.concat([df, new_row], ignore_index=True)

        # Save CSV
        self._save_csv(deck_id, df)

        # Return the new card
        new_card_id = len(df) - 1
        return Card(
            id=new_card_id,
            deck_id=deck_id,
            fields=card_data.fields,
            tags=card_data.tags
        )

    def create_cards_batch(self, deck_id: str, cards_data: List[CardCreate]) -> List[Card]:
        """Add multiple cards to a deck at once"""
        df = self._load_csv(deck_id)

        new_cards = []
        for card_data in cards_data:
            # Validate and fill missing columns
            for col in df.columns:
                if col not in card_data.fields:
                    card_data.fields[col] = ""

            new_cards.append(card_data.fields)

        # Add all new rows
        new_df = pd.DataFrame(new_cards)
        df = pd.concat([df, new_df], ignore_index=True)

        # Save CSV
        self._save_csv(deck_id, df)

        # Return the new cards
        start_id = len(df) - len(new_cards)
        return [
            Card(
                id=start_id + i,
                deck_id=deck_id,
                fields=card_data.fields,
                tags=card_data.tags
            )
            for i, card_data in enumerate(cards_data)
        ]

    def update_card(self, deck_id: str, card_id: int, card_data: CardUpdate) -> Optional[Card]:
        """Update a card in a deck"""
        df = self._load_csv(deck_id)

        if card_id < 0 or card_id >= len(df):
            return None

        # Update fields if provided
        if card_data.fields:
            for col, value in card_data.fields.items():
                if col in df.columns:
                    df.at[card_id, col] = value

        # Save CSV
        self._save_csv(deck_id, df)

        # Return updated card
        return self.get_card(deck_id, card_id)

    def delete_card(self, deck_id: str, card_id: int) -> bool:
        """Delete a card from a deck"""
        df = self._load_csv(deck_id)

        if card_id < 0 or card_id >= len(df):
            return False

        # Drop the row
        df = df.drop(card_id).reset_index(drop=True)

        # Save CSV
        self._save_csv(deck_id, df)

        return True
