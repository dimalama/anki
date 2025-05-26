#!/usr/bin/env python3
"""
Simple script to show what tags would be applied to a CSV file.
"""

import os
import re
from pathlib import Path

# CSV file to analyze
csv_filename = "ir_a_infinitive_deck_full.csv"
csv_path = os.path.join("csv", csv_filename)

# Extract base name
base_name = os.path.splitext(os.path.basename(csv_path))[0]
print(f"Analyzing file: {csv_filename}")

# Generate tags
tags = []

# Add language tag
tags.append("spanish")

# Add source tag
tags.append("auto-generated")

# Add card type tag (assuming basic cards)
tags.append("basic")

# Extract meaningful tags from filename
common_words = {'deck', 'card', 'cards', 'anki', 'full', 'new', 'updated', 'final', 'draft', 'test'}
for word in re.split(r'[_\-\s]', base_name):
    if word and word.lower() not in common_words and len(word) > 1:
        tags.append(word.lower())

# Add language learning specific tags
if "ir_a" in base_name.lower() or "ir-a" in base_name.lower():
    tags.append("ir-a")
    tags.append("future")
    tags.append("verb")

if "infinitive" in base_name.lower():
    tags.append("infinitive")
    tags.append("verb")

# Add translation tag (since the CSV has English and Spanish)
tags.append("translation")

# Print the tags
print(f"\nTags that would be applied to {csv_filename}:")
print(f"  {', '.join(tags)}")

# Explain the tagging logic
print("\nTagging logic explanation:")
print("  - 'spanish': Language tag based on content")
print("  - 'auto-generated': Source tag for all generated decks")
print("  - 'basic': Card type tag (not cloze deletion)")
print("  - 'ir-a': Language construct tag from filename")
print("  - 'future': Tense tag based on 'ir a' construction")
print("  - 'infinitive': Grammar tag from filename")
print("  - 'verb': Part of speech tag from filename and content")
print("  - 'translation': Content tag based on having English and Spanish columns")
