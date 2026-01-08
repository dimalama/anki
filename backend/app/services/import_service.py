"""Import service - Business logic for importing data"""

import pandas as pd
import io
import re
from typing import Optional, List
from pathlib import Path

from app.models.deck import Deck
from app.services.deck_service import DeckService
from app.services.card_service import CardService
from app.models.card import CardCreate

# Column format presets: maps format name to column headers
# Uses "Target" as placeholder for the target language (Spanish, French, etc.)
COLUMN_FORMATS = {
    "2col": ["English", "{target}"],
    "3col": ["English", "{target}", "Example"],
    "4col": ["English", "{target}", "Example", "Notes"],
    "front_back": ["Front", "Back"],
    "cloze": ["Text", "Translation", "Explanation"],
    "cloze_notes": ["Text", "Translation", "Explanation", "Notes"],
}


def get_column_headers(column_format: str, language: str) -> List[str]:
    """Get column headers for a given format and target language."""
    # Capitalize language name for column header
    target_lang = language.capitalize()

    if column_format not in COLUMN_FORMATS:
        # Default to 2col if unknown format
        column_format = "2col"

    headers = COLUMN_FORMATS[column_format]
    # Replace {target} placeholder with actual language name
    return [h.replace("{target}", target_lang) for h in headers]


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
        card_type: str = "basic",
        column_format: Optional[str] = None
    ) -> Deck:
        """Import cards from CSV content

        Args:
            content: Raw CSV/TSV file content
            filename: Original filename
            deck_name: Optional custom deck name
            language: Target language (spanish, french, etc.)
            card_type: Card type (basic, cloze, reversed)
            column_format: Column format preset (2col, 3col, 4col, front_back, cloze, cloze_notes)
        """

        # Use filename as deck name if not provided
        if not deck_name:
            deck_name = Path(filename).stem

        # Parse CSV/TSV - auto-detect delimiter
        try:
            # Try to detect delimiter (tab or comma)
            text_content = content.decode('utf-8')
            if '\t' in text_content.split('\n')[0]:
                df = pd.read_csv(io.BytesIO(content), sep='\t')
            else:
                df = pd.read_csv(io.BytesIO(content))
        except Exception as e:
            raise ValueError(f"Invalid CSV/TSV format: {str(e)}")

        # Validate CSV has data
        if df.empty:
            raise ValueError("CSV file is empty")

        # If column_format specified and CSV has generic headers, rename them
        if column_format:
            expected_headers = get_column_headers(column_format, language)
            current_cols = df.columns.tolist()

            # Check if current headers are generic (Column0, Column1, etc. or numbered)
            generic_patterns = ['column', 'col', 'field', 'unnamed']
            is_generic = all(
                any(p in str(col).lower() for p in generic_patterns) or str(col).isdigit()
                for col in current_cols
            )

            # Rename columns if they're generic or if column count matches
            if is_generic or len(current_cols) == len(expected_headers):
                rename_map = {current_cols[i]: expected_headers[i]
                             for i in range(min(len(current_cols), len(expected_headers)))}
                df = df.rename(columns=rename_map)

        # Save CSV to csv directory - sanitize deck_id for filesystem
        deck_id = re.sub(r'[^\w\s-]', '', deck_name.lower())
        deck_id = re.sub(r'[-\s]+', '_', deck_id)
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
        card_type: str = "basic",
        column_format: Optional[str] = None
    ) -> Deck:
        """Import cards from plain text

        Args:
            text: Plain text with one card per line
            deck_name: Name for the deck
            language: Target language (spanish, french, etc.)
            separator: Column separator (default: tab)
            card_type: Card type (basic, cloze, reversed)
            column_format: Column format preset (2col, 3col, 4col, front_back, cloze, cloze_notes)
                          If not specified, auto-detects based on column count
        """

        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]

        if not lines:
            raise ValueError("No valid lines found in text")

        # Parse lines - check if first line looks like a header
        first_parts = lines[0].split(separator)
        known_headers = ['front', 'back', 'english', 'text', 'translation',
                         'example', 'notes', 'explanation']
        # Add language names as known headers
        known_headers.extend(['spanish', 'french', 'german', 'italian', 'portuguese',
                             'russian', 'japanese', 'chinese', 'korean'])

        has_header = any(
            p.strip().lower().rstrip('()').split('(')[0].strip() in known_headers
            for p in first_parts
        )

        cards_data = []
        if has_header:
            # Use first line as headers
            headers = [h.strip() for h in first_parts]
            for line in lines[1:]:
                parts = line.split(separator)
                card = {}
                for i, header in enumerate(headers):
                    card[header] = parts[i].strip() if i < len(parts) else ''
                if any(card.values()):  # Only add if card has some content
                    cards_data.append(card)
        else:
            # No header - determine column names
            num_cols = len(first_parts)

            # Use column_format if specified, otherwise auto-detect
            if column_format:
                default_headers = get_column_headers(column_format, language)
            else:
                # Auto-detect based on column count and card type
                if card_type == "cloze":
                    default_headers = get_column_headers("cloze" if num_cols <= 3 else "cloze_notes", language)
                elif num_cols == 2:
                    default_headers = get_column_headers("2col", language)
                elif num_cols == 3:
                    default_headers = get_column_headers("3col", language)
                elif num_cols >= 4:
                    default_headers = get_column_headers("4col", language)
                else:
                    default_headers = get_column_headers("2col", language)

            # Extend headers if we have more columns than defaults
            while len(default_headers) < num_cols:
                default_headers.append(f'Column{len(default_headers) + 1}')

            for line in lines:
                parts = line.split(separator)
                if len(parts) >= 2:
                    card = {}
                    for i, part in enumerate(parts):
                        header = default_headers[i] if i < len(default_headers) else f'Column{i + 1}'
                        card[header] = part.strip()
                    cards_data.append(card)

        if not cards_data:
            raise ValueError("No valid card data found in text")

        # Create deck - sanitize deck_id for filesystem
        deck_id = re.sub(r'[^\w\s-]', '', deck_name.lower())
        deck_id = re.sub(r'[-\s]+', '_', deck_id)
        csv_path = self.deck_service._get_csv_path(deck_id)

        # Create CSV from data
        df = pd.DataFrame(cards_data)
        df.to_csv(csv_path, index=False)

        # Load and return deck metadata
        deck = self.deck_service._load_deck_metadata(deck_id)
        if not deck:
            raise ValueError("Failed to create deck from text")

        return deck
