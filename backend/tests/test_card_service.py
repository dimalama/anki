"""Tests for the card service - CRUD operations and batch handling"""

import pytest
import pandas as pd
from pathlib import Path

from app.services.card_service import CardService
from app.models.card import CardCreate, CardUpdate


@pytest.fixture
def temp_csv_dir(tmp_path):
    """Create a temporary CSV directory for tests"""
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()
    return csv_dir


@pytest.fixture
def card_service(temp_csv_dir, monkeypatch):
    """Create a card service instance with mocked paths"""
    from app.core.config import settings
    monkeypatch.setattr(settings, "CSV_DIR", temp_csv_dir)
    return CardService()


@pytest.fixture
def sample_deck(temp_csv_dir):
    """Create a sample deck CSV for testing"""
    deck_id = "test_deck"
    csv_path = temp_csv_dir / f"{deck_id}.csv"

    # Create CSV with sample data
    df = pd.DataFrame({
        'English': ['hello', 'goodbye', 'thanks'],
        'Spanish': ['hola', 'adiós', 'gracias'],
        'Example': ['Hola, amigo!', 'Adiós, hasta luego.', 'Muchas gracias.'],
        'Notes': ['greeting', 'farewell', 'polite']
    })
    df.to_csv(csv_path, index=False)

    return deck_id


class TestCardList:
    """Tests for listing cards"""

    def test_list_cards_returns_all_cards(self, card_service, sample_deck):
        """Test that list_cards returns all cards in deck"""
        cards = card_service.list_cards(sample_deck)

        assert len(cards) == 3
        assert cards[0].fields['English'] == 'hello'
        assert cards[1].fields['English'] == 'goodbye'
        assert cards[2].fields['English'] == 'thanks'

    def test_list_cards_preserves_all_fields(self, card_service, sample_deck):
        """Test that all fields are preserved when listing"""
        cards = card_service.list_cards(sample_deck)

        card = cards[0]
        assert 'English' in card.fields
        assert 'Spanish' in card.fields
        assert 'Example' in card.fields
        assert 'Notes' in card.fields

    def test_list_cards_empty_deck(self, card_service, temp_csv_dir):
        """Test listing cards from empty deck"""
        # Create empty CSV
        deck_id = "empty_deck"
        csv_path = temp_csv_dir / f"{deck_id}.csv"
        df = pd.DataFrame(columns=['Front', 'Back'])
        df.to_csv(csv_path, index=False)

        cards = card_service.list_cards(deck_id)
        assert len(cards) == 0


class TestCardCreate:
    """Tests for creating cards"""

    def test_create_single_card(self, card_service, sample_deck):
        """Test creating a single card"""
        card_data = CardCreate(
            fields={'English': 'please', 'Spanish': 'por favor', 'Example': 'Por favor, ayuda.', 'Notes': 'polite'},
            tags=['polite']
        )

        card = card_service.create_card(sample_deck, card_data)

        assert card is not None
        assert card.fields['English'] == 'please'
        assert card.fields['Spanish'] == 'por favor'
        assert card.id == 3  # 0-indexed, so 4th card has id 3

    def test_create_batch_cards(self, card_service, sample_deck):
        """Test creating multiple cards at once"""
        cards_data = [
            CardCreate(fields={'English': 'yes', 'Spanish': 'sí', 'Example': '', 'Notes': ''}, tags=[]),
            CardCreate(fields={'English': 'no', 'Spanish': 'no', 'Example': '', 'Notes': ''}, tags=[]),
        ]

        cards = card_service.create_cards_batch(sample_deck, cards_data)

        assert len(cards) == 2
        assert cards[0].fields['English'] == 'yes'
        assert cards[1].fields['English'] == 'no'

        # Verify total count
        all_cards = card_service.list_cards(sample_deck)
        assert len(all_cards) == 5  # 3 original + 2 new


class TestCardUpdate:
    """Tests for updating cards"""

    def test_update_card_fields(self, card_service, sample_deck):
        """Test updating card fields"""
        card_data = CardUpdate(
            fields={'English': 'hi', 'Spanish': 'hola (informal)'}
        )

        updated = card_service.update_card(sample_deck, 0, card_data)

        assert updated is not None
        assert updated.fields['English'] == 'hi'
        assert updated.fields['Spanish'] == 'hola (informal)'
        # Other fields should remain unchanged
        assert updated.fields['Example'] == 'Hola, amigo!'

    def test_update_preserves_other_cards(self, card_service, sample_deck):
        """Test that updating one card doesn't affect others"""
        card_data = CardUpdate(fields={'English': 'hi'})
        card_service.update_card(sample_deck, 0, card_data)

        # Check other cards are unchanged
        cards = card_service.list_cards(sample_deck)
        assert cards[1].fields['English'] == 'goodbye'
        assert cards[2].fields['English'] == 'thanks'

    def test_update_nonexistent_card_returns_none(self, card_service, sample_deck):
        """Test updating a card that doesn't exist"""
        card_data = CardUpdate(fields={'English': 'test'})
        result = card_service.update_card(sample_deck, 999, card_data)

        assert result is None


class TestCardDelete:
    """Tests for deleting cards"""

    def test_delete_card(self, card_service, sample_deck):
        """Test deleting a card"""
        result = card_service.delete_card(sample_deck, 0)

        assert result is True

        # Verify card was deleted
        cards = card_service.list_cards(sample_deck)
        assert len(cards) == 2
        # First card should now be 'goodbye'
        assert cards[0].fields['English'] == 'goodbye'

    def test_delete_nonexistent_card_returns_false(self, card_service, sample_deck):
        """Test deleting a card that doesn't exist"""
        result = card_service.delete_card(sample_deck, 999)

        assert result is False


class TestDuplicatePrevention:
    """Tests to verify duplicate entries are not created on update"""

    def test_update_does_not_create_duplicates(self, card_service, sample_deck):
        """Test that updating cards doesn't create duplicates"""
        initial_count = len(card_service.list_cards(sample_deck))

        # Update first card
        card_data = CardUpdate(fields={'English': 'hi there'})
        card_service.update_card(sample_deck, 0, card_data)

        # Count should remain the same
        final_count = len(card_service.list_cards(sample_deck))
        assert final_count == initial_count

    def test_multiple_updates_same_card(self, card_service, sample_deck):
        """Test multiple updates to same card don't create duplicates"""
        initial_count = len(card_service.list_cards(sample_deck))

        # Update same card multiple times
        for i in range(5):
            card_data = CardUpdate(fields={'English': f'update_{i}'})
            card_service.update_card(sample_deck, 0, card_data)

        # Count should remain the same
        final_count = len(card_service.list_cards(sample_deck))
        assert final_count == initial_count

        # Verify last update was applied
        cards = card_service.list_cards(sample_deck)
        assert cards[0].fields['English'] == 'update_4'
