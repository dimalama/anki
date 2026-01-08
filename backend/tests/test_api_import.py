"""Tests for import API endpoints"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.models.deck import Deck


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def mock_deck():
    """Create a mock deck response"""
    return Deck(
        id="test_deck",
        name="Test Deck",
        language="spanish",
        description=None,
        tags=["spanish", "basic"],
        card_type="basic",
        card_count=2,
        csv_path="/tmp/test.csv",
        apkg_path=None
    )


class TestCSVImportEndpoint:
    """Tests for CSV/TSV file import endpoint"""

    def test_import_csv_accepts_csv_file(self, client, mock_deck):
        """Test that CSV files are accepted"""
        with patch('app.api.endpoints.import_export.import_service') as mock_service:
            mock_service.import_from_csv.return_value = mock_deck

            response = client.post(
                "/api/v1/import/csv",
                files={"file": ("test.csv", b"Front,Back\nhello,hola", "text/csv")},
                data={"language": "spanish", "card_type": "basic"}
            )

            assert response.status_code == 200
            assert response.json()["success"] is True

    def test_import_csv_accepts_tsv_file(self, client, mock_deck):
        """Test that TSV files are accepted"""
        with patch('app.api.endpoints.import_export.import_service') as mock_service:
            mock_service.import_from_csv.return_value = mock_deck

            response = client.post(
                "/api/v1/import/csv",
                files={"file": ("test.tsv", b"English\tSpanish\nhello\thola", "text/tab-separated-values")},
                data={"language": "spanish", "card_type": "basic"}
            )

            assert response.status_code == 200
            assert response.json()["success"] is True

    def test_import_csv_rejects_invalid_extension(self, client):
        """Test that invalid file extensions are rejected"""
        response = client.post(
            "/api/v1/import/csv",
            files={"file": ("test.txt", b"hello\tworld", "text/plain")},
            data={"language": "spanish", "card_type": "basic"}
        )

        assert response.status_code == 400
        assert "CSV or TSV" in response.json()["detail"]


class TestTextImportEndpoint:
    """Tests for text import endpoint"""

    def test_import_text_with_tabs(self, client, mock_deck):
        """Test text import with tab separator"""
        with patch('app.api.endpoints.import_export.import_service') as mock_service:
            mock_service.import_from_text.return_value = mock_deck

            response = client.post(
                "/api/v1/import/text",
                data={
                    "text": "hello\thola\ngoodbye\tadios",
                    "deck_name": "Test Deck",
                    "language": "spanish",
                    "separator": "\t",
                    "card_type": "basic"
                }
            )

            assert response.status_code == 200
            assert response.json()["success"] is True

    def test_import_text_with_four_columns(self, client, mock_deck):
        """Test text import preserves all 4 columns"""
        with patch('app.api.endpoints.import_export.import_service') as mock_service:
            mock_service.import_from_text.return_value = mock_deck

            text = "this (m.)\teste\tEste es mi teléfono.\tNear me; masculine singular"

            response = client.post(
                "/api/v1/import/text",
                data={
                    "text": text,
                    "deck_name": "Spanish Vocab",
                    "language": "spanish",
                    "separator": "\t",
                    "card_type": "basic"
                }
            )

            assert response.status_code == 200
            # Verify the service was called with the text
            mock_service.import_from_text.assert_called_once()
            call_args = mock_service.import_from_text.call_args
            assert "this (m.)" in call_args.kwargs.get('text', call_args.args[0] if call_args.args else '')

    def test_import_text_empty_raises_error(self, client):
        """Test that empty text raises an error"""
        with patch('app.api.endpoints.import_export.import_service') as mock_service:
            mock_service.import_from_text.side_effect = ValueError("No valid lines found")

            response = client.post(
                "/api/v1/import/text",
                data={
                    "text": "",
                    "deck_name": "Empty",
                    "language": "spanish",
                    "separator": "\t",
                    "card_type": "basic"
                }
            )

            # 400 for ValueError, 422 for validation error (empty string rejected by FastAPI)
            assert response.status_code in [400, 422]


class TestCardsEndpoint:
    """Tests for cards API endpoints"""

    def test_update_card_endpoint(self, client):
        """Test card update endpoint"""
        from app.models.card import Card

        mock_card = Card(
            id=0,
            deck_id="test",
            fields={"English": "updated", "Spanish": "actualizado"},
            tags=[]
        )

        with patch('app.api.endpoints.cards.card_service') as mock_service:
            mock_service.update_card.return_value = mock_card

            response = client.put(
                "/api/v1/cards/test/cards/0",
                json={"fields": {"English": "updated"}}
            )

            assert response.status_code == 200
            mock_service.update_card.assert_called_once()

    def test_batch_create_cards_endpoint(self, client):
        """Test batch card creation endpoint"""
        from app.models.card import Card

        mock_cards = [
            Card(id=0, deck_id="test", fields={"Front": "a", "Back": "b"}, tags=[]),
            Card(id=1, deck_id="test", fields={"Front": "c", "Back": "d"}, tags=[]),
        ]

        with patch('app.api.endpoints.cards.card_service') as mock_service:
            mock_service.create_cards_batch.return_value = mock_cards

            response = client.post(
                "/api/v1/cards/test/cards/batch",
                json={
                    "cards": [
                        {"fields": {"Front": "a", "Back": "b"}, "tags": []},
                        {"fields": {"Front": "c", "Back": "d"}, "tags": []}
                    ]
                }
            )

            assert response.status_code == 201
            assert response.json()["count"] == 2
