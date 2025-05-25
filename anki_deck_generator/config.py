import os
from pathlib import Path

# Project root directory
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Data directories
CSV_DIR = ROOT_DIR / 'csv'
OUTPUT_DIR = ROOT_DIR / 'apkg'

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Field mappings for different CSV formats
FIELD_MAPPINGS = {
    'standard_cloze': {
        'Text': 'Text',
        'Translation': 'Translation',
        'Explanation': 'Explanation'
    }
}

# CSV file paths for Spanish language
SPANISH_CSV_FILES = {
    'ser_estar_tener': str(CSV_DIR / 'spanish_ser_estar_tener_cloze.csv'),
    'present_tense_regular': str(CSV_DIR / 'spanish_present_tense_regular.csv'),
    'present_tense_irregular': str(CSV_DIR / 'spanish_present_tense_irregular.csv'),
    'present_tense_stem_changing': str(CSV_DIR / 'spanish_present_tense_stem_changing.csv'),
    'prepositions': str(CSV_DIR / 'spanish_preposition_cloze_cards.csv'),
    'present_tense_verbs_cloze': str(CSV_DIR / 'spanish_present_tense_verbs_cloze.csv')
}

# Output file paths for Spanish language
SPANISH_OUTPUT_FILES = {
    'ser_estar_tener': str(OUTPUT_DIR / 'spanish_ser_estar_tener_cloze.apkg'),
    'present_tense_regular': str(OUTPUT_DIR / 'spanish_present_tense_regular.apkg'),
    'present_tense_irregular': str(OUTPUT_DIR / 'spanish_present_tense_irregular.apkg'),
    'present_tense_stem_changing': str(OUTPUT_DIR / 'spanish_present_tense_stem_changing.apkg'),
    'prepositions': str(OUTPUT_DIR / 'spanish_prepositions.apkg'),
    'present_tense_verbs_cloze': str(OUTPUT_DIR / 'spanish_present_tense_verbs_cloze.apkg')
}
