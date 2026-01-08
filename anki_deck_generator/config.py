import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

# Project root directory
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Data directories
CSV_DIR = ROOT_DIR / 'csv'
OUTPUT_DIR = ROOT_DIR / 'apkg'
MEDIA_DIR = ROOT_DIR / 'media'
TEMPLATES_DIR = ROOT_DIR / 'templates'
CONFIG_DIR = ROOT_DIR / 'config'

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# Default configuration file
DEFAULT_CONFIG_FILE = CONFIG_DIR / 'config.json'

# Supported languages
SUPPORTED_LANGUAGES = [
    'spanish',
    'english',
    'french',
    'german',
    'italian',
    'portuguese',
    'japanese',
    'chinese',
    'korean',
    'generic'
]

# Default card templates
DEFAULT_BASIC_TEMPLATE = {
    'name': 'Basic Card',
    'qfmt': '{{Front}}',
    'afmt': '{{FrontSide}}<hr>{{Back}}'
}

DEFAULT_CLOZE_TEMPLATE = {
    'name': 'Cloze Card',
    'qfmt': '{{cloze:Text}}',
    'afmt': '{{cloze:Text}}<hr><b>Translation:</b> {{Translation}}'
}

# Default CSS
DEFAULT_CSS = """
.card {
    font-family: Arial, sans-serif;
    font-size: 20px;
    text-align: center;
    color: #333;
    background-color: #f8f8f8;
    padding: 20px;
}
.cloze {
    font-weight: bold;
    color: #0066cc;
}
"""

# Default configuration
DEFAULT_CONFIG = {
    'custom_tags': {},  # Map of CSV filename patterns to additional tags
    'tag_filters': {    # Enable/disable different types of tags
        'language': True,
        'card_type': True,
        'source': True,
        'grammar': True,
        'content': True,
        'language_construct': True,
        'filename': True
    },
    'templates': {      # Custom templates for different card types
        'basic': DEFAULT_BASIC_TEMPLATE,
        'cloze': DEFAULT_CLOZE_TEMPLATE
    },
    'css': DEFAULT_CSS,  # Custom CSS for cards
    'media_enabled': True  # Enable/disable media support
}


def load_config() -> Dict[str, Any]:
    """Load configuration from file or create default if it doesn't exist."""
    if not os.path.exists(DEFAULT_CONFIG_FILE):
        # Create default configuration file
        with open(DEFAULT_CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG

    try:
        with open(DEFAULT_CONFIG_FILE, 'r') as f:
            config = json.load(f)

        # Ensure all required keys are present
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value

        return config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return DEFAULT_CONFIG


def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to file."""
    try:
        with open(DEFAULT_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False


def get_custom_tags(filename: str, config: Optional[Dict[str, Any]] = None) -> List[str]:
    """Get custom tags for a CSV file based on patterns in the configuration."""
    if config is None:
        config = load_config()

    custom_tags = []
    for pattern, tags in config.get('custom_tags', {}).items():
        if pattern in filename:
            custom_tags.extend(tags)

    return custom_tags
