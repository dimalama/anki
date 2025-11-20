"""Template service - Business logic for template operations"""

import json
from pathlib import Path
from typing import List, Optional

from app.models.template import Template, TemplateCreate
from app.core.config import settings


class TemplateService:
    """Service for managing card templates"""

    def __init__(self):
        self.templates_dir = settings.TEMPLATES_DIR

    def _get_default_templates(self) -> List[Template]:
        """Get built-in default templates"""
        return [
            Template(
                id="basic",
                name="Basic Card",
                type="basic",
                qfmt="{{Front}}",
                afmt='{{FrontSide}}<hr id="answer"><div class="back">{{Back}}</div>',
                css=".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; }",
                is_default=True
            ),
            Template(
                id="basic_reversed",
                name="Basic Card (with Reversed)",
                type="basic",
                qfmt="{{Front}}",
                afmt='{{FrontSide}}<hr id="answer"><div class="back">{{Back}}</div>',
                css=".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; }",
                is_default=True
            ),
            Template(
                id="cloze",
                name="Cloze Deletion",
                type="cloze",
                qfmt="{{cloze:Text}}",
                afmt='{{cloze:Text}}<hr><div class="extra"><b>Translation:</b> {{Translation}}</div><div class="extra"><b>Explanation:</b> {{Explanation}}</div>',
                css=".card { font-family: arial; font-size: 20px; } .cloze { font-weight: bold; color: blue; } .extra { margin-top: 10px; }",
                is_default=True
            )
        ]

    def _load_custom_templates(self) -> List[Template]:
        """Load custom templates from JSON files"""
        templates = []

        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r') as f:
                    data = json.load(f)

                template = Template(
                    id=template_file.stem,
                    name=data.get('name', template_file.stem),
                    type=data.get('type', 'basic'),
                    qfmt=data.get('qfmt', ''),
                    afmt=data.get('afmt', ''),
                    css=data.get('css', ''),
                    is_default=False
                )
                templates.append(template)
            except Exception as e:
                print(f"Error loading template {template_file}: {e}")

        return templates

    def list_templates(self) -> List[Template]:
        """List all available templates (default + custom)"""
        templates = self._get_default_templates()
        templates.extend(self._load_custom_templates())
        return templates

    def get_template(self, template_id: str) -> Optional[Template]:
        """Get a specific template by ID"""
        templates = self.list_templates()
        for template in templates:
            if template.id == template_id:
                return template
        return None

    def create_template(self, template_data: TemplateCreate) -> Template:
        """Create a new custom template"""
        # Generate template ID from name
        template_id = template_data.name.lower().replace(' ', '_')
        template_path = self.templates_dir / f"{template_id}.json"

        # Check if template already exists
        if template_path.exists():
            raise ValueError(f"Template '{template_data.name}' already exists")

        # Save template as JSON
        template_dict = {
            'name': template_data.name,
            'type': template_data.type,
            'qfmt': template_data.qfmt,
            'afmt': template_data.afmt,
            'css': template_data.css or ''
        }

        with open(template_path, 'w') as f:
            json.dump(template_dict, f, indent=2)

        return Template(
            id=template_id,
            name=template_data.name,
            type=template_data.type,
            qfmt=template_data.qfmt,
            afmt=template_data.afmt,
            css=template_data.css,
            is_default=False
        )
