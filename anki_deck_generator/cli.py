import argparse
import sys
from typing import List, Optional

from anki_deck_generator.auto_generator import generate_decks_from_directory
from anki_deck_generator.config import CSV_DIR, OUTPUT_DIR, SUPPORTED_LANGUAGES


def main():
    """
    Main entry point for the CLI application.
    """
    parser = argparse.ArgumentParser(description='Generate Anki decks from CSV files')
    
    parser.add_argument(
        '--language',
        choices=SUPPORTED_LANGUAGES,
        default='spanish',
        help='Language tag for the decks'
    )
    
    parser.add_argument(
        '--csv-dir',
        type=str,
        help='Directory containing CSV files (defaults to config.CSV_DIR)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Directory to save generated APKG files (defaults to config.OUTPUT_DIR)'
    )
    
    parser.add_argument(
        '--files',
        nargs='+',
        help='Specific CSV files to process (filenames only, not full paths)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set directories
    csv_directory = args.csv_dir or CSV_DIR
    output_directory = args.output_dir or OUTPUT_DIR
    
    print(f"🔍 Scanning for CSV files in {csv_directory}...")
    
    # Generate decks
    generated_files = generate_decks_from_directory(
        csv_dir=csv_directory,
        output_dir=output_directory,
        language=args.language,
        specific_files=args.files
    )
    
    # Print summary
    if generated_files:
        print(f"\n✅ Successfully generated {len(generated_files)} deck(s):")
        for file in generated_files:
            print(f"  - {file}")
    else:
        print("❌ No decks were generated.")


if __name__ == '__main__':
    main()
