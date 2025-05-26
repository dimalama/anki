import genanki
import pandas as pd
import os
import uuid
import re
from typing import Dict, List, Optional, Any, Tuple

# Import configuration functions
from anki_deck_generator.config import load_config, get_custom_tags, DEFAULT_CSS


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


def analyze_csv_structure(csv_path: str) -> Tuple[List[str], Dict[str, str]]:
    """
    Analyze the structure of a CSV file to determine its fields.
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        A tuple containing (list of field names, field mapping dictionary)
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Get column names
    columns = list(df.columns)
    
    # Create field list
    fields = [{'name': col} for col in columns]
    
    # Create field mapping (identity mapping)
    field_mapping = {col: col for col in columns}
    
    return columns, field_mapping


def create_dynamic_deck_generator(csv_path: str, language: str = 'generic', custom_config: Optional[Dict[str, Any]] = None) -> DeckGenerator:
    """
    Create a deck generator dynamically based on the CSV file structure.
    
    Args:
        csv_path: Path to the CSV file
        language: Language tag for the deck (default: 'generic')
        
    Returns:
        A configured DeckGenerator instance
    """
    # Extract filename without extension
    filename = os.path.basename(csv_path)
    base_name = os.path.splitext(filename)[0]
    
    # Create a readable deck name from the filename
    deck_name = ' '.join(word.capitalize() for word in re.split(r'[_\-]', base_name))
    if language != 'generic':
        deck_name = f"{language.capitalize()} {deck_name}"
    
    # Generate unique IDs based on the filename
    # Using hash of filename to create deterministic IDs
    filename_hash = hash(base_name)
    model_id = abs(filename_hash) % (10**10)  # Ensure it's positive and 10 digits
    deck_id = abs(filename_hash + 1) % (10**10)  # Different from model_id but related
    
    # Analyze CSV structure
    columns, field_mapping = analyze_csv_structure(csv_path)
    
    # Create fields list for the model
    fields = [{'name': col} for col in columns]
    
    # Determine if this is likely a cloze deletion deck
    is_cloze = any('cloze' in col.lower() for col in columns) or \
               any('text' in col.lower() for col in columns)
    
    # Load configuration
    config = custom_config or load_config()
    tag_filters = config.get('tag_filters', {})
    
    # Generate tags
    tags = []
    
    # Add language tag
    if tag_filters.get('language', True):
        tags.append(language.lower())
    
    # Add source tag
    if tag_filters.get('source', True):
        tags.append('auto-generated')
    
    # Add card type tag
    if tag_filters.get('card_type', True):
        if is_cloze:
            tags.append('cloze')
        else:
            tags.append('basic')
        
    # Extract meaningful tags from filename (skip common words)
    if tag_filters.get('filename', True):
        common_words = {'deck', 'card', 'cards', 'anki', 'full', 'new', 'updated', 'final', 'draft', 'test'}
        for word in re.split(r'[_\-\s]', base_name):
            if word and word.lower() not in common_words and len(word) > 1:  # Skip single letters and common words
                tags.append(word.lower())
                
    # Add custom tags from configuration
    custom_tags = get_custom_tags(base_name, config)
    tags.extend(custom_tags)
        
    # Define language learning tags to detect
    language_learning_tags = {
        # Basic categories
        'vocabulary': ['vocab', 'word', 'dictionary', 'lexicon', 'term'],
        'grammar': ['grammar', 'structure', 'syntax', 'rule'],
        'verb': ['verb', 'conjugation', 'tense', 'infinitive'],
        'noun': ['noun', 'substantive', 'object', 'thing'],
        'adjective': ['adjective', 'adj', 'descriptor'],
        'adverb': ['adverb', 'adv'],
        'preposition': ['preposition', 'prep'],
        'pronoun': ['pronoun', 'subject', 'object'],
        
        # Tenses and moods
        'present': ['present', 'presents', 'currently'],
        'past': ['past', 'preterite', 'imperfect', 'historical'],
        'future': ['future', 'will', 'going to'],
        'conditional': ['conditional', 'would'],
        'subjunctive': ['subjunctive', 'subjuntivo'],
        'imperative': ['imperative', 'command', 'order'],
        
        # Common constructs
        'ir-a': ['ir a', 'going to', 'future'],
        'ser-estar': ['ser estar', 'being', 'to be'],
        'por-para': ['por para', 'for']
    }
    
    # Only add grammar and content tags if enabled in config
    if tag_filters.get('grammar', True) or tag_filters.get('content', True) or tag_filters.get('language_construct', True):
        # Check filename for language learning category indicators
        lower_filename = base_name.lower()
        
        # Check for language learning tags in the filename
        for tag, indicators in language_learning_tags.items():
            category = 'grammar' if tag in ['verb', 'noun', 'adjective', 'adverb', 'preposition', 'pronoun'] else \
                      'language_construct' if tag in ['ir-a', 'ser-estar', 'por-para'] else 'content'
            
            # Skip if this category is disabled in config
            if not tag_filters.get(category, True):
                continue
                
            for indicator in indicators:
                if indicator in lower_filename:
                    if tag not in tags:  # Avoid duplicates
                        tags.append(tag)
        
        # Special checks for common constructs if language_construct tags are enabled
        if tag_filters.get('language_construct', True):
            if 'ir' in lower_filename and 'a' in lower_filename and ('infinitive' in lower_filename or 'future' in lower_filename):
                if 'ir-a' not in tags:
                    tags.append('ir-a')
                if 'future' not in tags and tag_filters.get('grammar', True):
                    tags.append('future')
        
        # Check column names for basic indicators
        lower_columns = [col.lower() for col in columns]
        if 'english' in lower_columns and any(lang in lower_columns for lang in ['spanish', 'french', 'german', 'italian']):
            tags.append('translation')
        
        # Add person tag if there's a Person column
        if 'person' in lower_columns and tag_filters.get('grammar', True):
            tags.append('person')
    
    # Scan for media references if media is enabled
    if config.get('media_enabled', True):
        try:
            df = pd.read_csv(csv_path, nrows=5)  # Read just a few rows to check for media
            has_media = False
            
            for col in df.columns:
                # Check for image or audio file references
                for cell in df[col].astype(str):
                    if '<img src=' in cell.lower() or '[sound:' in cell.lower():
                        has_media = True
                        break
            
            if has_media:
                tags.append('media')
        except Exception:
            # If there's any error reading the CSV, just continue without media check
            pass
    
    # Remove duplicate tags while preserving order
    seen = set()
    unique_tags = []
    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)
    tags = unique_tags
    
    # Get custom templates and options from config
    custom_templates = config.get('templates', {})
    custom_css = config.get('css', DEFAULT_CSS)
    
    # Check if we should create a reversed deck
    create_reversed = config.get('create_reversed', False)
    
    # Create appropriate templates based on CSV structure
    if is_cloze:
        # For cloze deletion cards
        if 'cloze' in custom_templates:
            # Use custom template from config
            template = custom_templates['cloze']
            templates = [{
                'name': template.get('name', 'Cloze Card'),
                'qfmt': template.get('qfmt', '{{cloze:' + columns[0] + '}}'),
                'afmt': template.get('afmt', '{{cloze:' + columns[0] + '}}<hr>' + \
                       ''.join([f'<b>{col}:</b> {{{{{col}}}}}<br>' for col in columns[1:]]))
            }]
        else:
            # Use default cloze template
            templates = [{
                'name': 'Cloze Card',
                'qfmt': '{{cloze:' + columns[0] + '}}',
                'afmt': '{{cloze:' + columns[0] + '}}<hr>' + \
                       ''.join([f'<b>{col}:</b> {{{{{col}}}}}<br>' for col in columns[1:]])
            }]
        model_type = genanki.Model.CLOZE
    else:
        # For basic cards (front/back)
        if 'basic' in custom_templates:
            # Use custom template from config
            template = custom_templates['basic']
            if len(columns) >= 2:
                # Create the standard template
                standard_template = {
                    'name': template.get('name', 'Basic Card'),
                    'qfmt': template.get('qfmt', '{{' + columns[0] + '}}'),
                    'afmt': template.get('afmt', '{{FrontSide}}<hr><b>' + columns[1] + ':</b> {{' + columns[1] + '}}' + \
                           ''.join([f'<br><b>{col}:</b> {{{{{col}}}}}<br>' for col in columns[2:]]))
                }
                
                # Initialize templates with the standard template
                templates = [standard_template]
                
                # Add reversed template if enabled
                if create_reversed:
                    reversed_template = {
                        'name': template.get('name', 'Basic Card') + ' (Reversed)',
                        'qfmt': template.get('qfmt', '{{' + columns[1] + '}}'),
                        'afmt': template.get('afmt', '{{FrontSide}}<hr><b>' + columns[0] + ':</b> {{' + columns[0] + '}}' + \
                               ''.join([f'<br><b>{col}:</b> {{{{{col}}}}}<br>' for col in columns[2:] if col != columns[1]]))
                    }
                    templates.append(reversed_template)
                    # Add a tag to indicate this deck has reversed cards
                    tags.append('reversed')
            else:
                templates = [{
                    'name': template.get('name', 'Basic Card'),
                    'qfmt': template.get('qfmt', '{{' + columns[0] + '}}'),
                    'afmt': template.get('afmt', '{{FrontSide}}')
                }]
        else:
            # Use default basic template
            if len(columns) >= 2:
                # Create the standard template
                standard_template = {
                    'name': 'Basic Card',
                    'qfmt': '{{' + columns[0] + '}}',
                    'afmt': '{{FrontSide}}<hr><b>' + columns[1] + ':</b> {{' + columns[1] + '}}' + \
                           ''.join([f'<br><b>{col}:</b> {{{{{col}}}}}<br>' for col in columns[2:]])
                }
                
                # Initialize templates with the standard template
                templates = [standard_template]
                
                # Add reversed template if enabled
                if create_reversed:
                    reversed_template = {
                        'name': 'Basic Card (Reversed)',
                        'qfmt': '{{' + columns[1] + '}}',
                        'afmt': '{{FrontSide}}<hr><b>' + columns[0] + ':</b> {{' + columns[0] + '}}' + \
                               ''.join([f'<br><b>{col}:</b> {{{{{col}}}}}<br>' for col in columns[2:] if col != columns[1]])
                    }
                    templates.append(reversed_template)
                    # Add a tag to indicate this deck has reversed cards
                    tags.append('reversed')
            else:
                templates = [{
                    'name': 'Basic Card',
                    'qfmt': '{{' + columns[0] + '}}',
                    'afmt': '{{FrontSide}}'
                }]
        model_type = 0  # Standard model
    
    # Use custom CSS from config
    css = custom_css
    
    # Create the deck generator
    return DeckGenerator(
        model_id=model_id,
        model_name=f"{deck_name} Model",
        deck_id=deck_id,
        deck_name=deck_name,
        fields=fields,
        templates=templates,
        css=css,
        model_type=model_type,
        tags=tags
    )
