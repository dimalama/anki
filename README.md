# Anki Deck Generator

A modular and extensible tool for generating Anki decks from CSV files. Currently supports Spanish language decks, with a framework designed to easily add more languages and knowledge domains.

## Features

- Generate Anki decks from CSV files
- Modular architecture for easy extension to new languages and domains
- Command-line interface for easy use
- Supports cloze deletion cards

## Installation

1. Clone this repository:
```
git clone https://github.com/dimalama/anki.git
cd anki
```

2. Create a virtual environment and install dependencies:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Generate all Spanish decks:
```
python generate_decks.py spanish
```

Generate specific Spanish decks:
```
python generate_decks.py spanish --decks ser_estar_tener prepositions
```

### Available Spanish Decks

- `ser_estar_tener`: Spanish verbs ser, estar, and tener
- `present_tense_regular`: Regular verbs in present tense
- `present_tense_irregular`: Irregular verbs in present tense
- `present_tense_stem_changing`: Stem-changing verbs in present tense
- `prepositions`: Spanish prepositions

## Project Structure

```
anki/
├── anki_deck_generator/       # Main package
│   ├── __init__.py
│   ├── cli.py                 # Command-line interface
│   ├── config.py              # Configuration settings
│   ├── core.py                # Core functionality
│   └── languages/             # Language-specific modules
│       ├── __init__.py
│       └── spanish/           # Spanish language module
│           ├── __init__.py
│           └── models.py      # Spanish deck models
├── apkg/                      # Output directory for .apkg files
├── csv/                       # Input CSV files
├── generate_decks.py          # Main entry point
├── README.md
└── requirements.txt
```

## Adding New Languages or Knowledge Domains

1. Create a new module in the `languages` directory
2. Define deck models and generators in the new module
3. Update the CLI to support the new language or domain

## Dependencies

- genanki
- pandas
- numpy

## License

MIT
