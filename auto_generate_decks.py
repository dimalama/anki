#!/usr/bin/env python3
"""
Auto-generate Anki decks from CSV files.
This script automatically processes CSV files in the csv/ directory and generates Anki decks.
"""

from anki_deck_generator.auto_generator import generate_decks_from_directory, merge_decks
from anki_deck_generator.core import create_dynamic_deck_generator
from anki_deck_generator.config import CSV_DIR, OUTPUT_DIR, MEDIA_DIR, CONFIG_DIR, load_config, save_config
import sys
import os
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional


def show_tags(csv_path, language='spanish', config=None):
    """Show the tags that would be applied to a CSV file."""
    try:
        # Load configuration if not provided
        if config is None:
            config = load_config()

        # Create a deck generator for the CSV file
        generator = create_dynamic_deck_generator(csv_path, language, config)

        # Print the tags
        print(f"\nTags for {os.path.basename(csv_path)}:")
        print(f"  {', '.join(generator.tags)}")

        return True
    except Exception as e:
        print(f"Error analyzing tags: {e}")
        import traceback
        traceback.print_exc()
        return False


def add_custom_tags(pattern, tags):
    """Add custom tags to the configuration."""
    try:
        # Load configuration
        config = load_config()

        # Add or update custom tags
        if 'custom_tags' not in config:
            config['custom_tags'] = {}

        config['custom_tags'][pattern] = tags

        # Save configuration
        save_config(config)

        print(f"Added custom tags {tags} for pattern '{pattern}'")
        return True
    except Exception as e:
        print(f"Error adding custom tags: {e}")
        return False


def configure_templates(template_type, template_file):
    """Configure card templates from a JSON file."""
    try:
        # Load configuration
        config = load_config()

        # Load template from file
        with open(template_file, 'r') as f:
            template = json.load(f)

        # Validate template
        required_keys = ['name', 'qfmt', 'afmt']
        for key in required_keys:
            if key not in template:
                print(f"Error: Template is missing required key '{key}'")
                return False

        # Update configuration
        if 'templates' not in config:
            config['templates'] = {}

        config['templates'][template_type] = template

        # Save configuration
        save_config(config)

        print(f"Updated {template_type} template from {template_file}")
        return True
    except Exception as e:
        print(f"Error configuring template: {e}")
        return False


def configure_css(css_file):
    """Configure card CSS from a file."""
    try:
        # Load configuration
        config = load_config()

        # Load CSS from file
        with open(css_file, 'r') as f:
            css = f.read()

        # Update configuration
        config['css'] = css

        # Save configuration
        save_config(config)

        print(f"Updated CSS from {css_file}")
        return True
    except Exception as e:
        print(f"Error configuring CSS: {e}")
        return False


def show_history():
    """Show the history of generated decks."""
    try:
        history_file = os.path.join(OUTPUT_DIR, 'generation_history.json')

        if not os.path.exists(history_file):
            print("No generation history found.")
            return False

        with open(history_file, 'r') as f:
            history = json.load(f)

        if not history:
            print("No generation history found.")
            return False

        print(f"\nGeneration History ({len(history)} entries):")
        for i, entry in enumerate(history, 1):
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n{i}. {entry['csv_file']} → {entry['output_file']}")
            print(f"   Generated: {timestamp}")
            print(f"   Tags: {', '.join(entry['tags'])}")

        return True
    except Exception as e:
        print(f"Error showing history: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Auto-generate Anki decks from CSV files')

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate Anki decks from CSV files')
    generate_parser.add_argument(
        '--language',
        default='spanish',
        choices=[
            'spanish', 'english', 'french', 'german', 'italian',
            'portuguese', 'japanese', 'chinese', 'korean', 'generic'
        ],
        help='Language tag for the decks'
    )
    generate_parser.add_argument(
        '--files',
        nargs='+',
        help='Specific CSV files to process (filenames only, not full paths)'
    )
    generate_parser.add_argument(
        '--merge',
        action='store_true',
        help='Merge all generated decks into a single deck'
    )
    generate_parser.add_argument(
        '--merge-name',
        type=str,
        help='Name for the merged deck (required if --merge is specified)'
    )

    generate_parser.add_argument(
        '--reversed',
        action='store_true',
        help='Create reversed cards (e.g., both English→Spanish and Spanish→English)'
    )

    # Tags command
    tags_parser = subparsers.add_parser('tags', help='Manage tags for Anki decks')
    tags_parser.add_argument(
        '--show',
        nargs='+',
        metavar='FILE',
        help='Show tags that would be applied to specified CSV files'
    )
    tags_parser.add_argument(
        '--add',
        action='store_true',
        help='Add custom tags to the configuration'
    )
    tags_parser.add_argument(
        '--pattern',
        type=str,
        help='Filename pattern to match for custom tags'
    )
    tags_parser.add_argument(
        '--tags',
        nargs='+',
        metavar='TAG',
        help='Custom tags to add for the pattern'
    )
    tags_parser.add_argument(
        '--language',
        default='spanish',
        help='Language tag for showing tags'
    )

    # Template command
    template_parser = subparsers.add_parser('template', help='Configure card templates')
    template_parser.add_argument(
        '--type',
        choices=['basic', 'cloze'],
        help='Type of template to configure'
    )
    template_parser.add_argument(
        '--file',
        type=str,
        help='JSON file containing the template configuration'
    )
    template_parser.add_argument(
        '--css',
        type=str,
        help='CSS file containing the card styling'
    )

    # History command
    history_parser = subparsers.add_parser('history', help='Show generation history')

    # Parse arguments
    args = parser.parse_args()

    # If no command specified, default to generate
    if not args.command:
        args.command = 'generate'
        args.language = 'spanish'
        args.files = None
        args.merge = False
        args.merge_name = None
        args.reversed = False

    # Handle commands
    if args.command == 'generate':
        print(f"🔍 Scanning for CSV files in {CSV_DIR}...")

        # Load configuration and set reversed option
        config = load_config()
        config['create_reversed'] = args.reversed

        # Generate decks
        generated_files = generate_decks_from_directory(
            csv_dir=CSV_DIR,
            output_dir=OUTPUT_DIR,
            language=args.language,
            specific_files=args.files,
            merge_output=args.merge,
            merge_name=args.merge_name,
            custom_config=config
        )

        # Print reversed cards message if enabled
        if args.reversed:
            print("\nCreated reversed cards (both directions) for all decks.")

        # Print summary
        if generated_files:
            print(f"\n✅ Successfully generated {len(generated_files)} deck(s):")
            for file in generated_files:
                print(f"  - {file}")
        else:
            print("❌ No decks were generated.")

    elif args.command == 'tags':
        if args.show:
            # Show tags for specified files
            for filename in args.show:
                csv_path = os.path.join(CSV_DIR, filename)
                if os.path.exists(csv_path):
                    show_tags(csv_path, args.language)
                else:
                    print(f"File not found: {csv_path}")
        elif args.add and args.pattern and args.tags:
            # Add custom tags
            add_custom_tags(args.pattern, args.tags)
        else:
            tags_parser.print_help()

    elif args.command == 'template':
        if args.type and args.file:
            # Configure template
            configure_templates(args.type, args.file)
        elif args.css:
            # Configure CSS
            configure_css(args.css)
        else:
            template_parser.print_help()

    elif args.command == 'history':
        # Show generation history
        show_history()


if __name__ == '__main__':
    main()
