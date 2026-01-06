# Anki Deck Generator

A flexible and dynamic tool for generating Anki decks from CSV files. Simply drop your CSV files into the `csv` folder and run the generator to create Anki decks automatically - no code changes required for new deck types! Designed specifically for language learning with intelligent tagging and customization options.

## Features

- **Zero-configuration deck generation**: Drop CSV files in the folder and generate decks instantly
- **Automatic CSV structure detection**: Automatically detects fields and creates appropriate card templates
- **Smart card type detection**: Identifies if a CSV should be a cloze deletion or basic card format
- **Multi-language support**: Tag decks with different language identifiers
- **Command-line interface**: Easy to use with flexible options
- **Intelligent tagging system**: Automatically generates relevant tags for language learning
- **Custom tag support**: Define your own tagging rules based on filename patterns
- **Template customization**: Create and use custom card templates and CSS styling
- **Media support**: Include images and audio files in your decks
- **Bulk operations**: Generate multiple decks at once and optionally merge them
- **Generation history**: Keep track of all generated decks with timestamps and tags

## Installation

1. Clone this repository:

```bash
git clone https://github.com/dimalama/anki.git
cd anki
```

2. Install uv (if not already installed):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Create a virtual environment and install dependencies:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

## Usage

### Quick Start

The simplest way to generate decks from all your CSV files:

```bash
python auto_generate_decks.py
```

This will:
1. Scan the `csv/` directory for all CSV files
2. Generate an Anki deck for each CSV file
3. Save the decks to the `apkg/` directory

### Command Line Options

The script now uses a command-based interface with several subcommands:

#### Generate Decks

```bash
python auto_generate_decks.py generate --language french
```

Generate decks for specific CSV files only:
```bash
python auto_generate_decks.py generate --files vocabulary.csv grammar.csv
```

Generate and merge multiple decks into one:

```bash
python auto_generate_decks.py generate --merge --merge-name "Complete Spanish Course"
```

Create cards with both directions (e.g., English→Spanish and Spanish→English):

```bash
python auto_generate_decks.py generate --files vocabulary.csv --reversed
```

#### Manage Tags

Show tags that would be applied to specific CSV files:
```bash
python auto_generate_decks.py tags --show vocabulary.csv grammar.csv
```

Add custom tags for files matching a pattern:

```bash
python auto_generate_decks.py tags --add --pattern "*_verb_*.csv" --tags verb grammar
```

#### Customize Templates

Configure a custom template for basic cards:

```bash
python auto_generate_decks.py template --type basic --file templates/basic_template.json
```

Update the CSS styling for all cards:

```bash
python auto_generate_decks.py template --css templates/custom_style.css
```

#### View Generation History

```bash
python auto_generate_decks.py history
```

### CSV File Structure

The generator works with any CSV structure. Here are some examples:

**Basic Cards (Front/Back)**:

```csv
English,Spanish
Hello,Hola
Goodbye,Adiós
```

**Cloze Deletion Cards**:

```csv
Text,Translation,Explanation
I {{c1::am}} a student,Yo soy un estudiante,Using ser for permanent states
```

## Supported Languages

You can tag your decks with any of these language identifiers:

- spanish
- english
- french
- german
- italian
- portuguese
- russian
- japanese
- chinese
- korean
- generic (default for unspecified languages)

## How It Works

The generator:

1. Analyzes the structure of your CSV files
2. Creates appropriate Anki card templates based on the columns
3. Generates unique model and deck IDs based on the filename
4. Creates intelligent tags based on the filename, columns, and content
5. Exports the deck as an APKG file ready to import into Anki

## Tagging System

The auto-generator includes an intelligent tagging system specifically designed for language learning:

### Automatic Tags

- **Language Tags**: `spanish`, `french`, `german`, etc.
- **Card Type Tags**: `basic` or `cloze` depending on the card format
- **Source Tags**: `auto-generated` to identify machine-generated decks

### Content-Based Tags

The system automatically detects and adds relevant tags based on the CSV filename and content:

- **Grammar Tags**: `verb`, `noun`, `adjective`, `adverb`, `preposition`, etc.
- **Content Tags**: `vocabulary`, `grammar`, `translation`, etc.
- **Language Construct Tags**: `ir-a`, `ser-estar`, `por-para`, etc.

### Examples

A CSV file named `spanish_ir_a_infinitive.csv` with columns for English and Spanish would get tags like:

- `spanish` (language)
- `basic` (card type)
- `ir-a` (language construct)
- `future` (tense)
- `verb` (part of speech)
- `translation` (content type)

These tags make it much easier to organize and find your decks in Anki.

## Project Structure

```text
anki/
├── anki_deck_generator/   # Core package
│   ├── __init__.py
│   ├── core.py            # Core functionality
│   ├── config.py          # Configuration
│   ├── cli.py             # Command-line interface
│   └── auto_generator.py  # Auto-generation functionality
├── csv/                   # CSV files go here
├── apkg/                  # Generated APKG files
├── media/                 # Media files (images, audio) go here
├── config/                # Configuration files
│   └── config.json        # Main configuration file
├── templates/             # Custom template files
│   ├── basic_template.json    # Template for basic cards
│   ├── cloze_template.json    # Template for cloze cards
│   └── custom_style.css       # Custom CSS styling
├── auto_generate_decks.py # Main script
├── README.md
└── requirements.txt       # Dependencies
```

## Adding New CSV Files

1. Create your CSV file with appropriate columns
2. Place the file in the `csv` directory
3. Add any referenced media files to the `media` directory
4. Run `python auto_generate_decks.py generate` to generate the deck

No code changes are required for new CSV files or deck types!

## Bulk Operations

### Generating Multiple Decks

You can generate multiple decks at once by placing multiple CSV files in the `csv` directory and running:

```bash
python auto_generate_decks.py generate
```

### Merging Decks

You can generate multiple decks and merge them into a single deck:

```bash
python auto_generate_decks.py generate --merge --merge-name "Complete Course"
```

### Generation History

The generator keeps track of all generated decks in a history file (`apkg/generation_history.json`). You can view this history with:

```bash
python auto_generate_decks.py history
```

## Configuration

The generator uses a configuration file (`config/config.json`) that can be modified directly or through the command-line interface.

### Custom Tags

You can define custom tags to be applied to files matching specific patterns:

```json
{
  "custom_tags": {
    "*_verb_*.csv": ["verb", "grammar"],
    "*_vocabulary_*.csv": ["vocabulary", "basic"]
  }
}
```

### Custom Templates

You can define custom templates for your cards:

```json
{
  "templates": {
    "basic": {
      "name": "Basic Card",
      "qfmt": "{{Front}}",
      "afmt": "{{FrontSide}}<hr><div class=\"back-content\"><b>{{Back}}</b></div>"
    },
    "cloze": {
      "name": "Cloze Card",
      "qfmt": "{{cloze:Text}}<br><div class=\"hint\">{{Hint}}</div>",
      "afmt": "{{cloze:Text}}<hr><div class=\"translation\"><b>Translation:</b> {{Translation}}</div>"
    }
  },
  "css": "/* Custom CSS styling */\n.card { font-family: Arial; }"
}
```

### Media Support

Place your media files in the `media/` directory and reference them in your CSV files:

- For images: `<img src="image.jpg">`
- For audio: `[sound:audio.mp3]`

## Dependencies

- genanki - For generating Anki decks
- pandas - For CSV processing
- pathlib - For path manipulation
- json - For configuration file handling

## License

MIT
