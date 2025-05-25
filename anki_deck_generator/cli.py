import argparse
import sys
from typing import List, Optional

from anki_deck_generator.languages.spanish import models as spanish_models
from anki_deck_generator.config import (
    SPANISH_CSV_FILES,
    SPANISH_OUTPUT_FILES,
    FIELD_MAPPINGS
)


def generate_spanish_decks(deck_types: Optional[List[str]] = None) -> None:
    """
    Generate Spanish Anki decks.
    
    Args:
        deck_types: List of deck types to generate, or None for all decks
    """
    # Map of deck types to their generator functions and associated files
    deck_generators = {
        'ser_estar_tener': {
            'generator': spanish_models.create_ser_estar_tener_deck(),
            'csv_path': SPANISH_CSV_FILES['ser_estar_tener'],
            'output_path': SPANISH_OUTPUT_FILES['ser_estar_tener']
        },
        'present_tense_regular': {
            'generator': spanish_models.create_present_tense_regular_deck(),
            'csv_path': SPANISH_CSV_FILES['present_tense_regular'],
            'output_path': SPANISH_OUTPUT_FILES['present_tense_regular']
        },
        'present_tense_irregular': {
            'generator': spanish_models.create_present_tense_irregular_deck(),
            'csv_path': SPANISH_CSV_FILES['present_tense_irregular'],
            'output_path': SPANISH_OUTPUT_FILES['present_tense_irregular']
        },
        'present_tense_stem_changing': {
            'generator': spanish_models.create_present_tense_stem_changing_deck(),
            'csv_path': SPANISH_CSV_FILES['present_tense_stem_changing'],
            'output_path': SPANISH_OUTPUT_FILES['present_tense_stem_changing']
        },
        'prepositions': {
            'generator': spanish_models.create_preposition_deck(),
            'csv_path': SPANISH_CSV_FILES['prepositions'],
            'output_path': SPANISH_OUTPUT_FILES['prepositions']
        }
    }
    
    # If no specific deck types provided, generate all
    if deck_types is None:
        deck_types = list(deck_generators.keys())
    
    # Validate deck types
    for deck_type in deck_types:
        if deck_type not in deck_generators:
            print(f"Error: Unknown deck type '{deck_type}'")
            print(f"Available deck types: {', '.join(deck_generators.keys())}")
            sys.exit(1)
    
    # Generate decks
    for deck_type in deck_types:
        deck_info = deck_generators[deck_type]
        generator = deck_info['generator']
        csv_path = deck_info['csv_path']
        output_path = deck_info['output_path']
        
        print(f"Generating {deck_type} deck...")
        try:
            generator.generate_from_csv(
                csv_path=csv_path,
                field_mapping=FIELD_MAPPINGS['standard_cloze']
            )
            generator.export_to_apkg(output_path)
        except Exception as e:
            print(f"Error generating {deck_type} deck: {e}")


def main():
    parser = argparse.ArgumentParser(description='Generate Anki decks from CSV files')
    
    # Add subparsers for different languages
    subparsers = parser.add_subparsers(dest='language', help='Language to generate decks for')
    
    # Spanish subparser
    spanish_parser = subparsers.add_parser('spanish', help='Generate Spanish decks')
    spanish_parser.add_argument(
        '--decks',
        nargs='+',
        choices=[
            'ser_estar_tener',
            'present_tense_regular',
            'present_tense_irregular',
            'present_tense_stem_changing',
            'prepositions',
            'all'
        ],
        default=['all'],
        help='Specific decks to generate'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle language selection
    if args.language == 'spanish':
        deck_types = None
        if 'all' not in args.decks:
            deck_types = args.decks
        generate_spanish_decks(deck_types)
    elif args.language is None:
        parser.print_help()
    else:
        print(f"Error: Unsupported language '{args.language}'")
        sys.exit(1)


if __name__ == '__main__':
    main()
