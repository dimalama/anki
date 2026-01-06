# Anki Deck Generator - Backend API

FastAPI backend for the Anki Deck Generator application.

## Setup

1. Install uv (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create a virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
```

3. Run the development server:
```bash
cd backend
python -m app.main
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## API Endpoints

### Decks
- `GET /api/v1/decks` - List all decks
- `GET /api/v1/decks/{deck_id}` - Get deck details
- `POST /api/v1/decks` - Create new deck
- `PUT /api/v1/decks/{deck_id}` - Update deck
- `DELETE /api/v1/decks/{deck_id}` - Delete deck
- `POST /api/v1/decks/{deck_id}/generate` - Generate .apkg file
- `GET /api/v1/decks/{deck_id}/download` - Download .apkg file

### Cards
- `GET /api/v1/cards/{deck_id}/cards` - List cards in deck
- `POST /api/v1/cards/{deck_id}/cards` - Add card to deck
- `POST /api/v1/cards/{deck_id}/cards/batch` - Add multiple cards
- `PUT /api/v1/cards/{deck_id}/cards/{card_id}` - Update card
- `DELETE /api/v1/cards/{deck_id}/cards/{card_id}` - Delete card

### Templates
- `GET /api/v1/templates` - List all templates
- `GET /api/v1/templates/{template_id}` - Get template
- `POST /api/v1/templates` - Create custom template

### Import
- `POST /api/v1/import/csv` - Import from CSV file
- `POST /api/v1/import/text` - Import from text

### Tags
- `GET /api/v1/tags` - Get all tags
- `GET /api/v1/tags/suggest` - Get tag suggestions

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── endpoints/      # API route handlers
│   ├── core/               # Configuration
│   ├── models/             # Pydantic models
│   ├── services/           # Business logic
│   └── main.py             # FastAPI app
├── tests/                  # Tests
└── requirements.txt        # Dependencies
```
