#!/usr/bin/env python3
"""
Test script to demonstrate the Anki deck generator functionality.
"""

import os
import sys
from pathlib import Path

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from anki_deck_generator.core import create_dynamic_deck_generator
from anki_deck_generator.config import load_config, CSV_DIR, OUTPUT_DIR

def main():
    # Load configuration
    config = load_config()
    
    # CSV file to process
    csv_filename = "ir_a_infinitive_deck_full.csv"
    csv_path = os.path.join(CSV_DIR, csv_filename)
    
    print(f"Processing CSV file: {csv_path}")
    print(f"File exists: {os.path.exists(csv_path)}")
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found: {csv_path}")
        return
    
    try:
        # Create a deck generator for the CSV file
        generator = create_dynamic_deck_generator(csv_path, language="spanish", custom_config=config)
        
        # Print the tags
        print(f"\nTags for {csv_filename}:")
        print(f"  {', '.join(generator.tags)}")
        
        # Generate the deck
        print(f"\nGenerating deck...")
        columns, field_mapping = generator.model.fields, {field['name']: field['name'] for field in generator.model.fields}
        generator.generate_from_csv(csv_path, field_mapping)
        
        # Export to APKG
        output_path = os.path.join(OUTPUT_DIR, f"{os.path.splitext(csv_filename)[0]}.apkg")
        generator.export_to_apkg(output_path)
        
        print(f"\nSuccessfully generated deck: {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
