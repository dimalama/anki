"""Deck service - Business logic for deck operations"""

import os
import pandas as pd
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import re

from app.models.deck import Deck, DeckCreate, DeckUpdate
from app.core.config import settings

# Import existing anki generator
import sys
sys.path.append(str(settings.BASE_DIR))
from anki_deck_generator.core import create_dynamic_deck_generator
from anki_deck_generator.config import load_config


class DeckService:
    """Service for managing decks"""

    def __init__(self):
        self.csv_dir = settings.CSV_DIR
        self.apkg_dir = settings.APKG_DIR
        self.config = load_config()

    def _filename_to_id(self, filename: str) -> str:
        """Convert filename to deck ID (without extension)"""
        return Path(filename).stem

    def _id_to_filename(self, deck_id: str) -> str:
        """Convert deck ID to CSV filename"""
        return f"{deck_id}.csv"

    def _get_csv_path(self, deck_id: str) -> Path:
        """Get full path to CSV file"""
        return self.csv_dir / self._id_to_filename(deck_id)

    def _get_apkg_path(self, deck_id: str) -> Optional[Path]:
        """Get full path to APKG file if it exists"""
        # Look for any .apkg file that starts with the deck_id
        for apkg_file in self.apkg_dir.glob(f"{deck_id}*.apkg"):
            return apkg_file
        return None

    def _load_deck_metadata(self, deck_id: str) -> Optional[Deck]:
        """Load deck metadata from CSV file"""
        csv_path = self._get_csv_path(deck_id)

        if not csv_path.exists():
            return None

        try:
            # Read CSV to get card count
            df = pd.read_csv(csv_path)
            card_count = len(df)

            # Get file stats
            stats = csv_path.stat()
            created_at = datetime.fromtimestamp(stats.st_ctime)
            updated_at = datetime.fromtimestamp(stats.st_mtime)

            # Detect card type from CSV content
            columns = df.columns.tolist()
            is_cloze = any('cloze' in col.lower() or 'text' in col.lower() for col in columns)
            card_type = 'cloze' if is_cloze else 'basic'

            # Get APKG path if it exists
            apkg_path = self._get_apkg_path(deck_id)

            # Generate deck name from filename
            deck_name = ' '.join(word.capitalize() for word in re.split(r'[_\-]', deck_id))

            # Detect language from filename
            language = 'generic'
            for lang in ['spanish', 'english', 'french', 'german', 'italian']:
                if lang in deck_id.lower():
                    language = lang
                    break

            # Extract tags from filename
            tags = [word.lower() for word in re.split(r'[_\-]', deck_id) if len(word) > 2]
            tags.append(language)
            tags.append(card_type)
            tags = list(set(tags))  # Remove duplicates

            return Deck(
                id=deck_id,
                name=deck_name,
                language=language,
                description=None,
                tags=tags,
                card_type=card_type,
                card_count=card_count,
                created_at=created_at,
                updated_at=updated_at,
                csv_path=str(csv_path),
                apkg_path=str(apkg_path) if apkg_path else None
            )

        except Exception as e:
            print(f"Error loading deck metadata for {deck_id}: {e}")
            return None

    def list_decks(self, language: Optional[str] = None, tag: Optional[str] = None) -> List[Deck]:
        """List all decks with optional filters"""
        decks = []

        # Scan CSV directory
        for csv_file in self.csv_dir.glob("*.csv"):
            deck_id = self._filename_to_id(csv_file.name)
            deck = self._load_deck_metadata(deck_id)

            if deck:
                # Apply filters
                if language and deck.language != language:
                    continue
                if tag and tag not in deck.tags:
                    continue

                decks.append(deck)

        # Sort by updated date (newest first)
        decks.sort(key=lambda d: d.updated_at or datetime.min, reverse=True)

        return decks

    def get_deck(self, deck_id: str) -> Optional[Deck]:
        """Get a single deck by ID"""
        return self._load_deck_metadata(deck_id)

    def create_deck(self, deck_data: DeckCreate) -> Deck:
        """Create a new deck"""
        # Generate deck ID from name
        deck_id = re.sub(r'[^\w\s-]', '', deck_data.name.lower())
        deck_id = re.sub(r'[-\s]+', '_', deck_id)

        csv_path = self._get_csv_path(deck_id)

        # Check if deck already exists
        if csv_path.exists():
            raise ValueError(f"Deck with name '{deck_data.name}' already exists")

        # Create empty CSV with appropriate columns based on card type
        if deck_data.card_type == 'cloze':
            columns = ['Text', 'Translation', 'Explanation']
        else:
            columns = ['Front', 'Back']

        df = pd.DataFrame(columns=columns)
        df.to_csv(csv_path, index=False)

        return self._load_deck_metadata(deck_id)

    def update_deck(self, deck_id: str, deck_data: DeckUpdate) -> Optional[Deck]:
        """Update an existing deck"""
        deck = self.get_deck(deck_id)
        if not deck:
            return None

        # If name is changing, rename the file
        if deck_data.name and deck_data.name != deck.name:
            new_id = re.sub(r'[^\w\s-]', '', deck_data.name.lower())
            new_id = re.sub(r'[-\s]+', '_', new_id)

            old_csv_path = self._get_csv_path(deck_id)
            new_csv_path = self._get_csv_path(new_id)

            if new_csv_path.exists():
                raise ValueError(f"Deck with name '{deck_data.name}' already exists")

            old_csv_path.rename(new_csv_path)
            deck_id = new_id

        return self._load_deck_metadata(deck_id)

    def delete_deck(self, deck_id: str) -> bool:
        """Delete a deck"""
        csv_path = self._get_csv_path(deck_id)

        if not csv_path.exists():
            return False

        # Delete CSV file
        csv_path.unlink()

        # Delete APKG file if it exists
        apkg_path = self._get_apkg_path(deck_id)
        if apkg_path and apkg_path.exists():
            apkg_path.unlink()

        return True

    def generate_apkg(self, deck_id: str) -> Optional[Deck]:
        """Generate .apkg file for a deck"""
        csv_path = self._get_csv_path(deck_id)

        if not csv_path.exists():
            return None

        try:
            # Get deck metadata
            deck = self._load_deck_metadata(deck_id)
            if not deck:
                return None

            # Use existing generator to create APKG
            generator = create_dynamic_deck_generator(
                str(csv_path),
                language=deck.language,
                custom_config=self.config
            )

            # Get columns for field mapping
            df = pd.read_csv(csv_path)
            columns = df.columns.tolist()
            field_mapping = {col: col for col in columns}

            # Generate from CSV
            generator.generate_from_csv(str(csv_path), field_mapping, tags=deck.tags)

            # Export to APKG
            output_filename = f"{deck_id}.apkg"
            output_path = self.apkg_dir / output_filename
            generator.export_to_apkg(str(output_path))

            # Return updated deck metadata
            return self._load_deck_metadata(deck_id)

        except Exception as e:
            print(f"Error generating APKG for {deck_id}: {e}")
            raise

    def get_apkg_path(self, deck_id: str) -> Optional[str]:
        """Get the path to the APKG file for a deck"""
        apkg_path = self._get_apkg_path(deck_id)
        return str(apkg_path) if apkg_path else None
