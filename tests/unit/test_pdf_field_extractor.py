"""Unit tests for PDFFieldExtractor."""

import os

# Add src to Python path
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from pdf_parser.field_extractor import PDFFieldExtractor


class TestPDFFieldExtractor:
    """Test suite for PDFFieldExtractor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = PDFFieldExtractor()
        self.test_data_dir = (
            Path(__file__).parent.parent.parent / "training_data" / "pdf_csv_pairs"
        )

    def test_init(self):
        """Test PDFFieldExtractor initialization."""
        extractor = PDFFieldExtractor()
        assert hasattr(extractor, "field_data")
        assert isinstance(extractor.field_data, list)
        assert len(extractor.field_data) == 0

    def test_extract_fields_file_not_found(self):
        """Test extraction with non-existent file."""
        result = self.extractor.extract_fields("nonexistent.pdf")

        assert result["success"] is False
        assert result["error_type"] == "FileNotFoundError"
        assert "not found" in result["error"].lower()
        assert result["data"] == []

    def test_extract_fields_empty_file(self):
        """Test extraction with empty file."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            empty_pdf = tmp.name

        try:
            result = self.extractor.extract_fields(empty_pdf)

            assert result["success"] is False
            assert result["error_type"] == "ValueError"
            assert "empty" in result["error"].lower()
        finally:
            os.unlink(empty_pdf)

    def test_extract_fields_non_pdf_file(self):
        """Test extraction with non-PDF file."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"This is not a PDF")
            txt_file = tmp.name

        try:
            result = self.extractor.extract_fields(txt_file)

            assert result["success"] is False
            assert result["error_type"] == "ValueError"
            assert "not a pdf" in result["error"].lower()
        finally:
            os.unlink(txt_file)

    def test_extract_fields_valid_pdf(self):
        """Test extraction with valid PDF."""
        pdf_path = self.test_data_dir / "W-4R_parsed.pdf"

        if not pdf_path.exists():
            pytest.skip(f"Test PDF not found: {pdf_path}")

        result = self.extractor.extract_fields(str(pdf_path))

        assert result["success"] is True
        assert result["field_count"] > 0
        assert result["pages_processed"] > 0
        assert isinstance(result["data"], list)
        assert len(result["data"]) == result["field_count"]

    def test_extract_fields_with_csv_output(self):
        """Test extraction with CSV output format."""
        pdf_path = self.test_data_dir / "W-4R_parsed.pdf"

        if not pdf_path.exists():
            pytest.skip(f"Test PDF not found: {pdf_path}")

        result = self.extractor.extract_fields(str(pdf_path), output_format="csv")

        assert result["success"] is True
        assert result["csv_export_success"] is True

        # Check if CSV file was created
        csv_path = str(pdf_path).replace(".pdf", "_extracted_fields.csv")
        assert Path(csv_path).exists()

        # Clean up
        try:
            os.unlink(csv_path)
        except:
            pass

    def test_csv_export_functionality(self):
        """Test CSV export with sample data."""
        test_data = [
            {
                "name": "test_field",
                "type": "TextField",
                "id": "test-id",
                "bem_category": "general-information",
                "x": 100,
                "y": 200,
                "width": 50,
                "height": 20,
                "page": 1,
            }
        ]

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            csv_path = tmp.name

        try:
            success = self.extractor.export_to_csv(test_data, csv_path)

            assert success is True
            assert Path(csv_path).exists()

            # Verify CSV content
            with open(csv_path, "r", encoding="utf-8") as f:
                content = f.read()
                assert "test_field" in content
                assert "TextField" in content
                assert "ID,Created at,Updated at" in content  # Header
        finally:
            try:
                os.unlink(csv_path)
            except:
                pass

    def test_field_type_detection(self):
        """Test field type detection methods."""
        # Test RadioGroup detection
        field_data = {"name": "test--group", "type": "RadioGroup"}
        assert (
            self.extractor._infer_bem_category("test--group", field_data)
            == "general-information"
        )

        # Test TextField detection
        assert (
            self.extractor._generate_field_label(
                {"name": "first_name", "type": "TextField"}
            )
            == "Name"
        )
        assert (
            self.extractor._generate_field_label(
                {"name": "last_name", "type": "TextField"}
            )
            == "Name"
        )

    def test_radiogroup_label_generation(self):
        """Test RadioGroup label generation."""
        test_cases = [
            (
                {"name": "address-change--group", "type": "RadioGroup"},
                "Address Change Options",
            ),
            (
                {"name": "dividend--group", "type": "RadioGroup"},
                "Future Dividend Application",
            ),
            ({"name": "frequency--group", "type": "RadioGroup"}, "Frequency"),
            ({"name": "custom--group", "type": "RadioGroup"}, "Custom"),
        ]

        for field_data, expected_label in test_cases:
            result = self.extractor._generate_field_label(field_data)
            assert result == expected_label

    def test_section_id_generation(self):
        """Test section ID generation for BEM categories."""
        test_fields = [
            {"bem_category": "general-information"},
            {"bem_category": "personal-information"},
            {"bem_category": "sign-here"},
        ]

        section_ids = self.extractor._generate_section_ids(test_fields)

        assert len(section_ids) == 3
        assert all(isinstance(id_val, int) for id_val in section_ids.values())
        assert all(id_val >= 8261 for id_val in section_ids.values())

    def test_get_page_count(self):
        """Test PDF page count functionality."""
        pdf_path = self.test_data_dir / "W-4R_parsed.pdf"

        if not pdf_path.exists():
            pytest.skip(f"Test PDF not found: {pdf_path}")

        page_count = self.extractor._get_page_count(str(pdf_path))
        assert page_count > 0
        assert isinstance(page_count, int)

    def test_get_page_count_invalid_file(self):
        """Test page count with invalid file."""
        page_count = self.extractor._get_page_count("nonexistent.pdf")
        assert page_count == 0

    def test_bem_category_inference(self):
        """Test BEM category inference from field names."""
        test_cases = [
            ("first_name", {"type": "TextField"}, "personal-information"),
            ("address", {"type": "TextField"}, "personal-information"),
            ("signature", {"type": "Signature"}, "sign-here"),
            ("test--group", {"type": "RadioGroup"}, "general-information"),
            ("unknown_field", {"type": "TextField"}, "general-information"),
        ]

        for field_name, field_data, expected_category in test_cases:
            result = self.extractor._infer_bem_category(field_name, field_data)
            assert result == expected_category

    @pytest.mark.integration
    def test_full_extraction_workflow(self):
        """Integration test for full extraction workflow."""
        pdf_path = self.test_data_dir / "LIFE-1528-Q__parsed.pdf"

        if not pdf_path.exists():
            pytest.skip(f"Test PDF not found: {pdf_path}")

        result = self.extractor.extract_fields(str(pdf_path))

        # Verify successful extraction
        assert result["success"] is True
        assert result["field_count"] > 50  # Should have many fields
        assert result["pages_processed"] >= 3

        # Verify field types are properly detected
        fields = result["data"]
        field_types = [field.get("Type") for field in fields]

        assert "RadioGroup" in field_types
        assert "RadioButton" in field_types
        assert "TextField" in field_types

        # Verify RadioGroup relationships
        radio_groups = [f for f in fields if f.get("Type") == "RadioGroup"]
        radio_buttons = [f for f in fields if f.get("Type") == "RadioButton"]

        assert len(radio_groups) >= 5
        assert len(radio_buttons) >= 15

        # Verify parent-child relationships
        for button in radio_buttons:
            parent_id = button.get("Parent ID")
            if parent_id:
                # Find corresponding RadioGroup
                parent_found = any(rg.get("ID") == parent_id for rg in radio_groups)
                assert (
                    parent_found
                ), f"RadioButton {button.get('Api name')} has invalid parent ID"

    def test_error_recovery(self):
        """Test error recovery mechanisms."""
        # Test with malformed data
        with patch.object(self.extractor, "_extract_acrofields") as mock_extract:
            mock_extract.side_effect = Exception("Test error")

            result = self.extractor.extract_fields("dummy.pdf")

            assert result["success"] is False
            assert "error" in result
            assert result["data"] == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
