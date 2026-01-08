"""Tests for the import service - TSV/CSV and text import functionality"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.services.import_service import ImportService


@pytest.fixture
def temp_csv_dir(tmp_path):
    """Create a temporary CSV directory for tests"""
    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()
    return csv_dir


@pytest.fixture
def import_service(temp_csv_dir):
    """Create an import service instance with mocked paths"""
    service = ImportService()
    # Mock the deck_service's csv_dir to use temp directory
    service.deck_service.csv_dir = temp_csv_dir
    return service


class TestCSVImport:
    """Tests for CSV/TSV file import"""

    def test_import_csv_basic_format(self, import_service, temp_csv_dir):
        """Test importing a basic CSV with Front/Back columns"""
        csv_content = b"Front,Back\nhello,hola\ngoodbye,adios"

        deck = import_service.import_from_csv(
            content=csv_content,
            filename="test_basic.csv",
            language="spanish",
            card_type="basic"
        )

        assert deck is not None
        assert deck.card_count == 2

    def test_import_tsv_with_tabs(self, import_service, temp_csv_dir):
        """Test importing a TSV file with tab separators"""
        tsv_content = b"English\tSpanish\tExample (ES)\tNotes\nthis (m.)\teste\tEste es mi telefono.\tNear me; masculine singular\nthat (m.)\tese\tEse libro es interesante.\tNear you; masculine singular"

        deck = import_service.import_from_csv(
            content=tsv_content,
            filename="test_vocab.tsv",
            language="spanish",
            card_type="basic"
        )

        assert deck is not None
        assert deck.card_count == 2

    def test_import_tsv_preserves_all_columns(self, import_service, temp_csv_dir):
        """Test that TSV import preserves all arbitrary columns"""
        tsv_content = b"English\tSpanish\tExample (ES)\tNotes\nthis (m.)\teste\tEste es mi telefono.\tNear me"

        deck = import_service.import_from_csv(
            content=tsv_content,
            filename="test_columns.tsv",
            language="spanish",
            card_type="basic"
        )

        # Load the saved CSV to verify columns
        csv_path = temp_csv_dir / "test_columns.csv"
        import pandas as pd
        df = pd.read_csv(csv_path)

        assert "English" in df.columns
        assert "Spanish" in df.columns
        assert "Example (ES)" in df.columns
        assert "Notes" in df.columns
        assert len(df) == 1

    def test_import_csv_empty_file_raises_error(self, import_service, temp_csv_dir):
        """Test that empty CSV raises an error"""
        csv_content = b"Front,Back\n"

        with pytest.raises(ValueError, match="empty"):
            import_service.import_from_csv(
                content=csv_content,
                filename="empty.csv",
                language="spanish",
                card_type="basic"
            )

    def test_import_csv_auto_detects_tab_delimiter(self, import_service, temp_csv_dir):
        """Test that tab delimiter is auto-detected even with .csv extension"""
        # Tab-separated content but with .csv extension
        tsv_content = b"Word\tTranslation\nhello\thola"

        deck = import_service.import_from_csv(
            content=tsv_content,
            filename="tabs.csv",  # .csv extension but tab-separated
            language="spanish",
            card_type="basic"
        )

        csv_path = temp_csv_dir / "tabs.csv"
        import pandas as pd
        df = pd.read_csv(csv_path)

        # Should have 2 columns, not be treated as single column
        assert len(df.columns) == 2
        assert "Word" in df.columns
        assert "Translation" in df.columns


class TestTextImport:
    """Tests for plain text import with header detection"""

    def test_text_import_with_headers(self, import_service, temp_csv_dir):
        """Test text import detects and uses headers"""
        text = "English\tSpanish\tExample\tNotes\nthis\teste\tEste es...\tmasculine\nthat\tese\tEse es...\tfeminine"

        deck = import_service.import_from_text(
            text=text,
            deck_name="test_headers",
            language="spanish",
            separator="\t",
            card_type="basic"
        )

        assert deck is not None
        assert deck.card_count == 2

        # Verify columns were preserved
        csv_path = temp_csv_dir / "test_headers.csv"
        import pandas as pd
        df = pd.read_csv(csv_path)

        assert "English" in df.columns
        assert "Spanish" in df.columns
        assert "Example" in df.columns
        assert "Notes" in df.columns

    def test_text_import_without_headers_basic(self, import_service, temp_csv_dir):
        """Test text import without headers uses Front/Back for basic cards"""
        text = "hello\thola\ngoodbye\tadios"

        deck = import_service.import_from_text(
            text=text,
            deck_name="test_no_headers",
            language="spanish",
            separator="\t",
            card_type="basic"
        )

        csv_path = temp_csv_dir / "test_no_headers.csv"
        import pandas as pd
        df = pd.read_csv(csv_path)

        assert "Front" in df.columns
        assert "Back" in df.columns
        assert df.iloc[0]["Front"] == "hello"
        assert df.iloc[0]["Back"] == "hola"

    def test_text_import_without_headers_cloze(self, import_service, temp_csv_dir):
        """Test text import without headers uses Text/Translation/Explanation for cloze"""
        text = "The {{c1::cat}} sat.\tEl gato se sentó.\tSimple sentence"

        deck = import_service.import_from_text(
            text=text,
            deck_name="test_cloze",
            language="spanish",
            separator="\t",
            card_type="cloze"
        )

        csv_path = temp_csv_dir / "test_cloze.csv"
        import pandas as pd
        df = pd.read_csv(csv_path)

        assert "Text" in df.columns
        assert "Translation" in df.columns
        assert "Explanation" in df.columns

    def test_text_import_detects_spanish_header(self, import_service, temp_csv_dir):
        """Test that 'Spanish' is recognized as a header"""
        text = "English\tSpanish\nhello\thola"

        deck = import_service.import_from_text(
            text=text,
            deck_name="test_spanish_header",
            language="spanish",
            separator="\t",
            card_type="basic"
        )

        csv_path = temp_csv_dir / "test_spanish_header.csv"
        import pandas as pd
        df = pd.read_csv(csv_path)

        # Should detect header and have 1 data row
        assert len(df) == 1
        assert "English" in df.columns
        assert "Spanish" in df.columns

    def test_text_import_detects_french_header(self, import_service, temp_csv_dir):
        """Test that 'French' is recognized as a header"""
        text = "English\tFrench\nhello\tbonjour"

        deck = import_service.import_from_text(
            text=text,
            deck_name="test_french_header",
            language="french",
            separator="\t",
            card_type="basic"
        )

        csv_path = temp_csv_dir / "test_french_header.csv"
        import pandas as pd
        df = pd.read_csv(csv_path)

        assert len(df) == 1
        assert "French" in df.columns

    def test_text_import_preserves_all_columns(self, import_service, temp_csv_dir):
        """Test that all columns from header line are preserved"""
        text = "English\tSpanish\tExample (ES)\tNotes\nthis (m.)\teste\tEste es mi teléfono.\tNear me; masculine singular"

        deck = import_service.import_from_text(
            text=text,
            deck_name="test_all_columns",
            language="spanish",
            separator="\t",
            card_type="basic"
        )

        csv_path = temp_csv_dir / "test_all_columns.csv"
        import pandas as pd
        df = pd.read_csv(csv_path)

        assert len(df.columns) == 4
        assert df.iloc[0]["English"] == "this (m.)"
        assert df.iloc[0]["Spanish"] == "este"
        assert df.iloc[0]["Example (ES)"] == "Este es mi teléfono."
        assert df.iloc[0]["Notes"] == "Near me; masculine singular"

    def test_text_import_empty_raises_error(self, import_service, temp_csv_dir):
        """Test that empty text raises an error"""
        with pytest.raises(ValueError, match="No valid lines"):
            import_service.import_from_text(
                text="",
                deck_name="empty",
                language="spanish",
                separator="\t",
                card_type="basic"
            )

    def test_text_import_four_columns_no_header(self, import_service, temp_csv_dir):
        """Test text import with 4 columns but no header row preserves all columns"""
        text = "this (m.)\teste\tEste es mi teléfono.\tNear me; masculine singular"

        deck = import_service.import_from_text(
            text=text,
            deck_name="test_four_cols",
            language="spanish",
            separator="\t",
            card_type="basic"
        )

        csv_path = temp_csv_dir / "test_four_cols.csv"
        import pandas as pd
        df = pd.read_csv(csv_path)

        # Should have 4 columns with default names
        assert len(df.columns) == 4
        assert "English" in df.columns
        assert "Spanish" in df.columns
        assert "Example" in df.columns
        assert "Notes" in df.columns

        # Verify data
        assert df.iloc[0]["English"] == "this (m.)"
        assert df.iloc[0]["Spanish"] == "este"
        assert df.iloc[0]["Example"] == "Este es mi teléfono."
        assert df.iloc[0]["Notes"] == "Near me; masculine singular"

    def test_text_import_handles_missing_columns(self, import_service, temp_csv_dir):
        """Test handling rows with fewer columns than header"""
        text = "English\tSpanish\tNotes\nhello\thola\nbye\tadios\tinformal"

        deck = import_service.import_from_text(
            text=text,
            deck_name="test_missing",
            language="spanish",
            separator="\t",
            card_type="basic"
        )

        csv_path = temp_csv_dir / "test_missing.csv"
        import pandas as pd
        df = pd.read_csv(csv_path)

        # First row should have empty/NaN Notes (empty string stored as NaN by pandas)
        assert pd.isna(df.iloc[0]["Notes"]) or df.iloc[0]["Notes"] == ""
        # Second row should have Notes
        assert df.iloc[1]["Notes"] == "informal"
