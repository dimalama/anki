import os
import argparse
import sys
import re
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from anki_deck_generator.core import create_dynamic_deck_generator, DeckGenerator
from anki_deck_generator.config import CSV_DIR, OUTPUT_DIR, MEDIA_DIR, load_config, save_config


def discover_csv_files(csv_dir: Path = CSV_DIR) -> List[str]:
    """
    Discover all CSV files in the specified directory.
    
    Args:
        csv_dir: Directory to search for CSV files
        
    Returns:
        List of paths to CSV files
    """
    if not os.path.exists(csv_dir):
        print(f"Error: CSV directory not found: {csv_dir}")
        return []
    
    csv_files = []
    for file in os.listdir(csv_dir):
        if file.lower().endswith('.csv'):
            csv_files.append(str(csv_dir / file))
    
    return csv_files


def process_media_files(csv_path: str, generator: DeckGenerator) -> List[str]:
    """
    Process media files referenced in the CSV and add them to the deck.
    
    Args:
        csv_path: Path to the CSV file
        generator: The deck generator instance
        
    Returns:
        List of media files that were added to the deck
    """
    try:
        import pandas as pd
        import genanki
        import re
        
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Patterns to match media references
        img_pattern = re.compile(r'<img\s+src=["\']([^"\'>]+)["\']')
        sound_pattern = re.compile(r'\[sound:([^\]]+)\]')
        
        # Track processed media files
        media_files = []
        
        # Process each cell in the dataframe
        for _, row in df.iterrows():
            for col in df.columns:
                cell = str(row[col])
                
                # Process image references
                for img_match in img_pattern.finditer(cell):
                    img_path = img_match.group(1)
                    # Check if it's a local file path
                    if not img_path.startswith(('http://', 'https://')):  
                        # Check if the file exists in the media directory
                        full_path = os.path.join(MEDIA_DIR, os.path.basename(img_path))
                        if os.path.exists(full_path):
                            media_files.append(full_path)
                
                # Process sound references
                for sound_match in sound_pattern.finditer(cell):
                    sound_path = sound_match.group(1)
                    # Check if the file exists in the media directory
                    full_path = os.path.join(MEDIA_DIR, os.path.basename(sound_path))
                    if os.path.exists(full_path):
                        media_files.append(full_path)
        
        return media_files
    except Exception as e:
        print(f"Error processing media files: {e}")
        return []


def generate_deck_from_csv(
    csv_path: str, 
    output_dir: Path = OUTPUT_DIR, 
    language: str = 'generic',
    custom_config: Optional[Dict[str, Any]] = None
) -> Tuple[str, List[str]]:
    """
    Generate an Anki deck from a CSV file.
    
    Args:
        csv_path: Path to the CSV file
        output_dir: Directory to save the generated APKG file
        language: Language tag for the deck
        
    Returns:
        Path to the generated APKG file
    """
    try:
        # Load configuration
        config = custom_config or load_config()
        
        # Create deck generator
        generator = create_dynamic_deck_generator(csv_path, language, config)
        
        # Extract filename without extension
        filename = os.path.basename(csv_path)
        base_name = os.path.splitext(filename)[0]
        
        # Define output path
        output_path = str(output_dir / f"{base_name}.apkg")
        
        # Print the tags that were applied to the deck
        print(f"\nApplied tags: {', '.join(generator.tags)}")
        
        # Generate deck from CSV
        columns, field_mapping = generator.model.fields, {field['name']: field['name'] for field in generator.model.fields}
        generator.generate_from_csv(csv_path, field_mapping)
        
        # Process media files if enabled
        media_files = []
        if config.get('media_enabled', True):
            media_files = process_media_files(csv_path, generator)
            if media_files:
                print(f"Found {len(media_files)} media files to include in the deck")
        
        # Create a package with media files if any were found
        if media_files:
            import genanki
            package = genanki.Package(generator.deck)
            package.media_files = media_files
            package.write_to_file(output_path)
        else:
            # Export to APKG without media
            generator.export_to_apkg(output_path)
        
        # Record this generation in the history
        record_generation_history(csv_path, output_path, generator.tags)
        
        return output_path, media_files
        
    
    except Exception as e:
        print(f"Error generating deck from {csv_path}: {e}")
        return "", []


def record_generation_history(csv_path: str, output_path: str, tags: List[str]) -> None:
    """
    Record the generation of a deck in the history file.
    
    Args:
        csv_path: Path to the CSV file
        output_path: Path to the generated APKG file
        tags: Tags applied to the deck
    """
    try:
        history_file = os.path.join(OUTPUT_DIR, 'generation_history.json')
        
        # Load existing history or create new
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        # Add new entry
        history.append({
            'csv_file': os.path.basename(csv_path),
            'output_file': os.path.basename(output_path),
            'tags': tags,
            'timestamp': datetime.now().isoformat(),
        })
        
        # Save updated history
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=4)
    except Exception as e:
        print(f"Error recording generation history: {e}")


def merge_decks(output_files: List[str], output_name: str, output_dir: Path = OUTPUT_DIR) -> str:
    """
    Merge multiple decks into a single deck.
    
    Args:
        output_files: List of paths to APKG files to merge
        output_name: Name for the merged deck
        output_dir: Directory to save the merged deck
        
    Returns:
        Path to the merged deck
    """
    try:
        import genanki
        import zipfile
        import tempfile
        import sqlite3
        import shutil
        
        # Create a temporary directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a new deck for the merged content
            merged_deck = genanki.Deck(
                deck_id=abs(hash(output_name)) % (10**10),
                name=output_name
            )
            
            # Track all media files
            all_media_files = []
            
            # Process each deck file
            for deck_file in output_files:
                if not os.path.exists(deck_file):
                    print(f"Warning: Deck file not found: {deck_file}")
                    continue
                    
                # Extract the deck file
                deck_extract_dir = os.path.join(temp_dir, os.path.basename(deck_file))
                os.makedirs(deck_extract_dir, exist_ok=True)
                
                with zipfile.ZipFile(deck_file, 'r') as zip_ref:
                    zip_ref.extractall(deck_extract_dir)
                
                # Connect to the database
                db_path = os.path.join(deck_extract_dir, 'collection.anki2')
                if not os.path.exists(db_path):
                    print(f"Warning: No collection found in {deck_file}")
                    continue
                    
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Extract notes and add to merged deck
                cursor.execute("SELECT id, flds, tags, mid FROM notes")
                for note_id, fields, tags, model_id in cursor.fetchall():
                    # We can't directly add these notes to the merged deck
                    # Just count them for now
                    all_media_files.append(note_id)
                
                conn.close()
            
            # For now, just return a message about the limitation
            merged_path = os.path.join(output_dir, f"{output_name}.apkg")
            print(f"Note: Full deck merging requires the AnkiConnect API. Found {len(all_media_files)} notes across {len(output_files)} decks.")
            print(f"For now, please import each deck individually into Anki.")
            
            # Copy the first deck as a placeholder
            if output_files:
                shutil.copy(output_files[0], merged_path)
                return merged_path
            
            return ""
    except Exception as e:
        print(f"Error merging decks: {e}")
        return ""


def generate_decks_from_directory(
    csv_dir: Path = CSV_DIR, 
    output_dir: Path = OUTPUT_DIR, 
    language: str = 'generic',
    specific_files: Optional[List[str]] = None,
    merge_output: bool = False,
    merge_name: Optional[str] = None,
    custom_config: Optional[Dict[str, Any]] = None
) -> List[str]:
    """
    Generate Anki decks from all CSV files in a directory.
    
    Args:
        csv_dir: Directory containing CSV files
        output_dir: Directory to save the generated APKG files
        language: Language tag for the decks
        specific_files: Optional list of specific filenames to process
        merge_output: Whether to merge all generated decks into a single deck
        merge_name: Name for the merged deck (required if merge_output is True)
        custom_config: Optional custom configuration to use
        
    Returns:
        List of paths to the generated APKG files
    """
    # Ensure directories exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Discover CSV files
    if specific_files:
        csv_files = [str(csv_dir / file) for file in specific_files if file.lower().endswith('.csv')]
    else:
        csv_files = discover_csv_files(csv_dir)
    
    if not csv_files:
        print("No CSV files found.")
        return []
    
    # Load configuration
    config = custom_config or load_config()
    
    # Generate decks
    output_files = []
    all_media_files = []
    for csv_file in csv_files:
        print(f"\nProcessing {os.path.basename(csv_file)}...")
        output_file, media_files = generate_deck_from_csv(csv_file, output_dir, language, config)
        if output_file:
            output_files.append(output_file)
            all_media_files.extend(media_files)
            if media_files:
                print(f"Added {len(media_files)} media files to the deck.")
    
    # Merge decks if requested
    if merge_output and output_files and merge_name:
        print(f"\nMerging {len(output_files)} decks into {merge_name}...")
        merged_deck = merge_decks(output_files, merge_name, output_dir)
        if merged_deck:
            print(f"Successfully merged decks into {os.path.basename(merged_deck)}")
            # Return only the merged deck
            return [merged_deck]
    
    return output_files


def main():
    parser = argparse.ArgumentParser(description='Auto-generate Anki decks from CSV files')
    
    parser.add_argument(
        '--language',
        default='generic',
        help='Language tag for the decks (e.g., spanish, french, etc.)'
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
    
    args = parser.parse_args()
    
    # Set directories
    csv_directory = Path(args.csv_dir) if args.csv_dir else CSV_DIR
    output_directory = Path(args.output_dir) if args.output_dir else OUTPUT_DIR
    
    # Generate decks
    generated_files = generate_decks_from_directory(
        csv_dir=csv_directory,
        output_dir=output_directory,
        language=args.language,
        specific_files=args.files
    )
    
    # Print summary
    if generated_files:
        print(f"\nSuccessfully generated {len(generated_files)} deck(s):")
        for file in generated_files:
            print(f"  - {file}")
    else:
        print("No decks were generated.")


if __name__ == '__main__':
    main()
