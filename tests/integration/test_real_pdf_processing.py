"""Integration tests for real PDF processing."""

import sys
from pathlib import Path

import pytest

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from pdf_parser.field_extractor import PDFFieldExtractor


class TestRealPDFProcessing:
    """Integration tests with real PDF files from training data."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = PDFFieldExtractor()
        self.test_data_dir = (
            Path(__file__).parent.parent.parent / "training_data" / "pdf_csv_pairs"
        )

    @pytest.mark.parametrize(
        "pdf_name,expected_min_fields",
        [
            ("W-4R_parsed.pdf", 8),
            ("LIFE-1528-Q__parsed.pdf", 70),
            ("FAF-0485AO__parsed.pdf", 20),
        ],
    )
    def test_pdf_field_extraction(self, pdf_name, expected_min_fields):
        """Test field extraction from various PDF types."""
        pdf_path = self.test_data_dir / pdf_name

        if not pdf_path.exists():
            pytest.skip(f"Test PDF not found: {pdf_path}")

        result = self.extractor.extract_fields(str(pdf_path))

        assert result["success"] is True
        assert result["field_count"] >= expected_min_fields
        assert len(result["data"]) == result["field_count"]
        assert result["pages_processed"] > 0

    def test_life_1528q_radio_button_detection(self):
        """Test specific radio button detection for LIFE-1528-Q."""
        pdf_path = self.test_data_dir / "LIFE-1528-Q__parsed.pdf"

        if not pdf_path.exists():
            pytest.skip(f"Test PDF not found: {pdf_path}")

        result = self.extractor.extract_fields(str(pdf_path))

        assert result["success"] is True

        fields = result["data"]

        # Count field types
        field_types = {}
        for field in fields:
            field_type = field.get("Type", "Unknown")
            field_types[field_type] = field_types.get(field_type, 0) + 1

        # Verify expected field type distribution
        assert field_types.get("RadioGroup", 0) >= 5
        assert field_types.get("RadioButton", 0) >= 15
        assert field_types.get("TextField", 0) >= 40

        # Verify specific RadioGroups exist
        radio_groups = [f for f in fields if f.get("Type") == "RadioGroup"]
        group_names = [rg.get("Api name", "") for rg in radio_groups]

        expected_groups = [
            "dividend--group",
            "frequency--group",
            "name-change--group",
            "name-change_reason--group",
            "stop--group",
        ]

        for expected_group in expected_groups:
            assert (
                expected_group in group_names
            ), f"RadioGroup {expected_group} not found"

    def test_faf_0485ao_checkbox_detection(self):
        """Test CheckBox detection for FAF-0485AO (CheckBox-only form)."""
        pdf_path = self.test_data_dir / "FAF-0485AO__parsed.pdf"

        if not pdf_path.exists():
            pytest.skip(f"Test PDF not found: {pdf_path}")

        result = self.extractor.extract_fields(str(pdf_path))

        assert result["success"] is True

        fields = result["data"]

        # Count field types
        field_types = {}
        for field in fields:
            field_type = field.get("Type", "Unknown")
            field_types[field_type] = field_types.get(field_type, 0) + 1

        # Should be mostly CheckBox fields
        assert field_types.get("CheckBox", 0) >= 20
        # Should have no RadioButtons (this was the key fix)
        assert field_types.get("RadioButton", 0) == 0
        assert field_types.get("RadioGroup", 0) == 0

    def test_w4r_text_field_detection(self):
        """Test TextField detection for W-4R (simple text form)."""
        pdf_path = self.test_data_dir / "W-4R_parsed.pdf"

        if not pdf_path.exists():
            pytest.skip(f"Test PDF not found: {pdf_path}")

        result = self.extractor.extract_fields(str(pdf_path))

        assert result["success"] is True

        fields = result["data"]

        # Count field types
        field_types = {}
        for field in fields:
            field_type = field.get("Type", "Unknown")
            field_types[field_type] = field_types.get(field_type, 0) + 1

        # Should be mostly TextField with some Signature fields
        assert field_types.get("TextField", 0) >= 8
        # Should have no radio buttons or checkboxes
        assert field_types.get("RadioButton", 0) == 0
        assert field_types.get("RadioGroup", 0) == 0
        assert field_types.get("CheckBox", 0) == 0

    def test_csv_export_integration(self):
        """Test CSV export integration with real PDF."""
        pdf_path = self.test_data_dir / "W-4R_parsed.pdf"

        if not pdf_path.exists():
            pytest.skip(f"Test PDF not found: {pdf_path}")

        result = self.extractor.extract_fields(str(pdf_path), output_format="csv")

        assert result["success"] is True
        assert result["csv_export_success"] is True

        # Verify CSV file was created
        csv_path = str(pdf_path).replace(".pdf", "_extracted_fields.csv")
        csv_file = Path(csv_path)
        assert csv_file.exists()

        # Verify CSV content structure
        with open(csv_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

            # Should have header + data rows
            assert len(lines) >= result["field_count"] + 1

            # Check header format
            header = lines[0].strip()
            expected_columns = [
                "ID",
                "Created at",
                "Updated at",
                "Label",
                "Description",
                "Form ID",
                "Order",
                "Api name",
                "UUID",
                "Type",
            ]
            for col in expected_columns:
                assert col in header

        # Clean up
        try:
            csv_file.unlink()
        except:
            pass

    def test_field_name_consistency(self):
        """Test that field names match training data patterns."""
        pdf_path = self.test_data_dir / "LIFE-1528-Q__parsed.pdf"

        if not pdf_path.exists():
            pytest.skip(f"Test PDF not found: {pdf_path}")

        result = self.extractor.extract_fields(str(pdf_path))

        assert result["success"] is True

        fields = result["data"]

        # Check for expected BEM naming patterns
        field_names = [f.get("Api name", "") for f in fields]

        # Should have RadioGroup names with --group suffix
        radio_group_names = [name for name in field_names if name.endswith("--group")]
        assert len(radio_group_names) >= 5

        # Should have RadioButton names with proper hierarchy
        radio_button_names = [
            name
            for name in field_names
            if name
            and not name.endswith("--group")
            and any(rg.replace("--group", "") in name for rg in radio_group_names)
        ]
        assert len(radio_button_names) >= 15

        # Should have proper BEM structure (block_element format)
        bem_structured_names = [
            name for name in field_names if "_" in name and not name.endswith("--group")
        ]
        assert len(bem_structured_names) >= 40

    def test_coordinate_extraction(self):
        """Test that coordinates are properly extracted."""
        pdf_path = self.test_data_dir / "LIFE-1528-Q__parsed.pdf"

        if not pdf_path.exists():
            pytest.skip(f"Test PDF not found: {pdf_path}")

        result = self.extractor.extract_fields(str(pdf_path))

        assert result["success"] is True

        fields = result["data"]

        # Most fields should have coordinate data
        fields_with_coords = [
            f
            for f in fields
            if f.get("X") and f.get("Y") and f.get("Width") and f.get("Height")
        ]

        # At least 80% of fields should have coordinates
        assert len(fields_with_coords) >= len(fields) * 0.8

        # Coordinates should be reasonable values
        for field in fields_with_coords:
            x, y = float(field.get("X", 0)), float(field.get("Y", 0))
            width, height = float(field.get("Width", 0)), float(field.get("Height", 0))

            # Coordinates should be within reasonable PDF bounds
            assert 0 <= x <= 1000  # Typical PDF width
            assert 0 <= y <= 1000  # Typical PDF height
            assert width > 0
            assert height > 0

    def test_parent_child_relationships(self):
        """Test RadioGroup parent-child relationships."""
        pdf_path = self.test_data_dir / "LIFE-1528-Q__parsed.pdf"

        if not pdf_path.exists():
            pytest.skip(f"Test PDF not found: {pdf_path}")

        result = self.extractor.extract_fields(str(pdf_path))

        assert result["success"] is True

        fields = result["data"]

        radio_groups = [f for f in fields if f.get("Type") == "RadioGroup"]
        radio_buttons = [f for f in fields if f.get("Type") == "RadioButton"]

        # Every RadioButton should have a valid parent
        for button in radio_buttons:
            parent_id = button.get("Parent ID")
            assert parent_id, f"RadioButton {button.get('Api name')} has no parent ID"

            # Find corresponding RadioGroup
            parent_found = any(rg.get("ID") == parent_id for rg in radio_groups)
            assert (
                parent_found
            ), f"RadioButton {button.get('Api name')} has invalid parent ID {parent_id}"

        # Every RadioGroup should have at least one child
        for group in radio_groups:
            group_id = group.get("ID")
            children = [b for b in radio_buttons if b.get("Parent ID") == group_id]
            assert (
                len(children) > 0
            ), f"RadioGroup {group.get('Api name')} has no children"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
