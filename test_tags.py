#!/usr/bin/env python3
"""
Test script to verify the tagging system works correctly.
"""

from anki_deck_generator.core import create_dynamic_deck_generator
import sys

def test_tagging(csv_path, language='spanish'):
    """Test the tagging system on a CSV file."""
    try:
        # Create a deck generator for the CSV file
        generator = create_dynamic_deck_generator(csv_path, language)
        
        # Print the tags
        print(f"\nTags for {csv_path}:")
        print(f"  {', '.join(generator.tags)}")
        
        return True
    except Exception as e:
        print(f"Error testing tags: {e}")
        return False

if __name__ == '__main__':
    # Get CSV path from command line or use default
    csv_path = sys.argv[1] if len(sys.argv) > 1 else 'csv/ir_a_infinitive_deck_full.csv'
    
    # Test the tagging system
    success = test_tagging(csv_path)
    
    if success:
        print("\nTagging system test completed successfully.")
    else:
        print("\nTagging system test failed.")
