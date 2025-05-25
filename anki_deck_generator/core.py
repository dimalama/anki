import genanki
import pandas as pd
import os
from typing import Dict, List, Optional, Any


class DeckGenerator:
    """Base class for generating Anki decks from CSV files."""
    
    def __init__(
        self,
        model_id: int,
        model_name: str,
        deck_id: int,
        deck_name: str,
        fields: List[Dict[str, str]],
        templates: List[Dict[str, str]],
        css: str,
        model_type: Optional[int] = None,
        tags: Optional[List[str]] = None
    ):
        """
        Initialize the deck generator with model and deck information.
        
        Args:
            model_id: Unique identifier for the Anki model
            model_name: Name of the model
            deck_id: Unique identifier for the Anki deck
            deck_name: Name of the deck
            fields: List of field dictionaries for the model
            templates: List of template dictionaries for the model
            css: CSS styling for the cards
            model_type: Type of model (default is None, use genanki.Model.CLOZE for cloze deletions)
            tags: Default tags to apply to all notes
        """
        self.model_id = model_id
        self.model_name = model_name
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.fields = fields
        self.templates = templates
        self.css = css
        self.model_type = model_type
        self.tags = tags or []
        
        # Create model
        model_kwargs = {
            'model_id': model_id,
            'name': model_name,
            'fields': fields,
            'templates': templates,
            'css': css,
        }
        if model_type is not None:
            model_kwargs['model_type'] = model_type
        
        self.model = genanki.Model(**model_kwargs)
        
        # Create deck
        self.deck = genanki.Deck(deck_id, deck_name)
    
    def generate_from_csv(
        self, 
        csv_path: str, 
        field_mapping: Dict[str, str],
        tags: Optional[List[str]] = None
    ) -> None:
        """
        Generate notes from a CSV file and add them to the deck.
        
        Args:
            csv_path: Path to the CSV file
            field_mapping: Dictionary mapping model field names to CSV column names
            tags: Additional tags to apply to notes from this CSV
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        df = pd.read_csv(csv_path)
        
        # Combine default tags with specific tags for this CSV
        note_tags = self.tags.copy()
        if tags:
            note_tags.extend(tags)
        
        for _, row in df.iterrows():
            # Extract fields from CSV based on mapping
            fields = []
            for field_name in [field['name'] for field in self.fields]:
                if field_name in field_mapping:
                    csv_column = field_mapping[field_name]
                    fields.append(row[csv_column])
                else:
                    fields.append('')  # Empty string for unmapped fields
            
            # Create note
            note = genanki.Note(
                model=self.model,
                fields=fields,
                tags=note_tags
            )
            self.deck.add_note(note)
    
    def export_to_apkg(self, output_path: str) -> None:
        """
        Export the deck to an APKG file.
        
        Args:
            output_path: Path where the APKG file will be saved
        """
        package = genanki.Package(self.deck)
        package.write_to_file(output_path)
        print(f"✅ Deck exported as {output_path}")


def create_cloze_deck_generator(
    model_id: int,
    model_name: str,
    deck_id: int,
    deck_name: str,
    fields: List[Dict[str, str]],
    templates: Optional[List[Dict[str, str]]] = None,
    css: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> DeckGenerator:
    """
    Factory function to create a DeckGenerator configured for cloze deletion cards.
    
    Args:
        model_id: Unique identifier for the Anki model
        model_name: Name of the model
        deck_id: Unique identifier for the Anki deck
        deck_name: Name of the deck
        fields: List of field dictionaries for the model
        templates: Optional custom templates (defaults to standard cloze template)
        css: Optional custom CSS (defaults to standard styling)
        tags: Default tags to apply to all notes
        
    Returns:
        A configured DeckGenerator instance
    """
    # Default cloze template if none provided
    if templates is None:
        templates = [
            {
                'name': 'Cloze Card',
                'qfmt': '{{cloze:Text}}',
                'afmt': '{{cloze:Text}}<hr><b>Translation:</b> {{Translation}}<br><b>Explanation:</b> {{Explanation}}',
            }
        ]
    
    # Default CSS if none provided
    if css is None:
        css = """
            .card { font-family: arial; font-size: 20px; }
            .cloze { font-weight: bold; color: blue; }
        """
    
    return DeckGenerator(
        model_id=model_id,
        model_name=model_name,
        deck_id=deck_id,
        deck_name=deck_name,
        fields=fields,
        templates=templates,
        css=css,
        model_type=genanki.Model.CLOZE,
        tags=tags
    )
