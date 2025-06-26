"""
Integration tests for MCP tools with real PDF files.

Tests the complete workflow using actual PDF files from the training data
to verify end-to-end functionality.
"""

import pytest
import asyncio
import json
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp_tools.tools.extract_fields import ExtractFieldsTool
from mcp_tools.tools.generate_names import GenerateNamesTool
from mcp_tools.tools.validate_names import ValidateNamesTool
from mcp_tools.tools.export_mapping import ExportMappingTool


class TestMCPIntegrationWithRealPDFs:
    """Integration tests using real PDF files."""
    
    @pytest.fixture
    def training_data_dir(self):
        """Path to training data directory."""
        return Path(__file__).parent.parent.parent / "training_data" / "pdf_csv_pairs"
    
    @pytest.fixture
    def sample_pdfs(self, training_data_dir):
        """List of available sample PDFs for testing."""
        pdf_files = list(training_data_dir.glob("*.pdf"))
        return [str(pdf) for pdf in pdf_files if pdf.exists()]
    
    @pytest.fixture
    def all_tools(self):
        """Create all MCP tool instances."""
        return {
            "extract": ExtractFieldsTool(),
            "generate": GenerateNamesTool(),
            "validate": ValidateNamesTool(),
            "export": ExportMappingTool()
        }
    
    @pytest.mark.asyncio
    async def test_extract_fields_w4r_pdf(self, training_data_dir, all_tools):
        """Test field extraction with W-4R PDF file."""
        w4r_pdf = training_data_dir / "W-4R_parsed.pdf"
        
        if not w4r_pdf.exists():
            pytest.skip("W-4R_parsed.pdf not found in training data")
        
        result = await all_tools["extract"].execute(
            pdf_path=str(w4r_pdf),
            context_radius=50,
            output_format="csv"
        )
        
        assert result["success"] is True
        assert result["extraction_metadata"]["field_count"] > 0
        assert result["extraction_metadata"]["pages_processed"] > 0
        assert len(result["fields"]) > 0
        
        # Verify field structure
        first_field = result["fields"][0]
        expected_keys = ["UUID", "Type", "Label"]
        for key in expected_keys:
            assert key in first_field
    
    @pytest.mark.asyncio
    async def test_complete_workflow_small_pdf(self, training_data_dir, all_tools):
        """Test complete workflow with a small PDF file."""
        # Find the smallest PDF for faster testing
        pdf_files = list(training_data_dir.glob("*.pdf"))
        if not pdf_files:
            pytest.skip("No PDF files found in training data")
        
        # Use W-4R as it's typically small and reliable
        test_pdf = training_data_dir / "W-4R_parsed.pdf"
        if not test_pdf.exists():
            test_pdf = pdf_files[0]  # Use first available PDF
        
        # Step 1: Extract fields
        extract_result = await all_tools["extract"].execute(
            pdf_path=str(test_pdf),
            context_radius=50,
            output_format="csv"
        )
        
        assert extract_result["success"] is True
        original_field_count = extract_result["extraction_metadata"]["field_count"]
        assert original_field_count > 0
        
        # Step 2: Generate names
        generate_result = await all_tools["generate"].execute(
            field_data=extract_result,
            use_training_data=True,
            confidence_threshold=0.0,  # Accept all for testing
            naming_strategy="context_aware"
        )
        
        assert generate_result["success"] is True
        generated_count = generate_result["generation_metadata"]["generated_count"]
        assert generated_count == original_field_count
        assert len(generate_result["generated_names"]) == original_field_count
        
        # Step 3: Validate names
        validate_result = await all_tools["validate"].execute(
            name_data=generate_result,
            check_duplicates=True,
            check_bem_compliance=True,
            check_reserved_names=True,
            strict_mode=False
        )
        
        assert validate_result["success"] is True
        assert validate_result["validation_metadata"]["total_names"] == original_field_count
        
        # Step 4: Export mapping (JSON)
        export_result_json = await all_tools["export"].execute(
            validated_names=validate_result,
            output_format="json",
            include_metadata=True,
            include_backup_plan=True,
            validation_threshold=0.0
        )
        
        assert export_result_json["success"] is True
        assert export_result_json["mapping_data"]["export_format"] == "json"
        json_field_count = len(export_result_json["mapping_data"]["field_mappings"])
        assert json_field_count <= original_field_count  # May filter invalid names
        
        # Step 5: Export mapping (CSV)
        export_result_csv = await all_tools["export"].execute(
            validated_names=validate_result,
            output_format="csv",
            include_metadata=True,
            include_backup_plan=True,
            validation_threshold=0.0
        )
        
        assert export_result_csv["success"] is True
        assert export_result_csv["mapping_data"]["export_format"] == "csv"
        csv_field_count = len(export_result_csv["mapping_data"]["rows"])
        assert csv_field_count == json_field_count  # Should be same count
        
        # Verify data consistency
        assert export_result_json["export_metadata"]["exported_fields"] == \
               export_result_csv["export_metadata"]["exported_fields"]
    
    @pytest.mark.asyncio
    async def test_radiogroup_handling(self, training_data_dir, all_tools):
        """Test RadioGroup field handling with LIFE-1528-Q PDF."""
        life_pdf = training_data_dir / "LIFE-1528-Q__parsed.pdf"
        
        if not life_pdf.exists():
            pytest.skip("LIFE-1528-Q__parsed.pdf not found in training data")
        
        # Extract fields
        extract_result = await all_tools["extract"].execute(
            pdf_path=str(life_pdf),
            context_radius=50,
            output_format="csv"
        )
        
        assert extract_result["success"] is True
        
        # Check for RadioGroup fields
        has_radio_groups = any(
            field.get("Type") == "RadioGroup" 
            for field in extract_result["fields"]
        )
        
        if not has_radio_groups:
            pytest.skip("No RadioGroup fields found in PDF")
        
        # Generate names
        generate_result = await all_tools["generate"].execute(
            field_data=extract_result,
            use_training_data=True,
            confidence_threshold=0.0
        )
        
        assert generate_result["success"] is True
        
        # Check that RadioGroups get --group suffix
        radio_group_names = [
            name_entry for name_entry in generate_result["generated_names"]
            if name_entry.get("field_type") == "RadioGroup"
        ]
        
        for radio_name in radio_group_names:
            assert radio_name["suggested_name"].endswith("--group"), \
                f"RadioGroup {radio_name['suggested_name']} should end with --group"
        
        # Validate names
        validate_result = await all_tools["validate"].execute(
            name_data=generate_result,
            check_bem_compliance=True
        )
        
        assert validate_result["success"] is True
        
        # Check RadioGroup validation
        radio_validations = [
            validation for validation in validate_result["field_validations"]
            if validation.get("field_type") == "RadioGroup"
        ]
        
        for validation in radio_validations:
            # RadioGroups should pass BEM compliance
            bem_errors = [
                error for error in validation.get("errors", [])
                if "bem" in error.get("type", "").lower()
            ]
            assert len(bem_errors) == 0, \
                f"RadioGroup validation failed: {bem_errors}"
    
    @pytest.mark.asyncio 
    async def test_error_handling_with_corrupted_input(self, all_tools):
        """Test error handling with various corrupted inputs."""
        
        # Test extract with non-existent file
        extract_result = await all_tools["extract"].execute(
            pdf_path="/path/to/nonexistent.pdf"
        )
        assert extract_result["success"] is False
        assert extract_result["error_type"] == "FileNotFoundError"
        
        # Test generate with corrupted field data
        corrupted_data = {
            "success": False,
            "error": "Corrupted test data"
        }
        generate_result = await all_tools["generate"].execute(
            field_data=corrupted_data
        )
        assert generate_result["success"] is False
        
        # Test validate with corrupted name data
        validate_result = await all_tools["validate"].execute(
            name_data=corrupted_data
        )
        assert validate_result["success"] is False
        
        # Test export with corrupted validation data
        export_result = await all_tools["export"].execute(
            validated_names=corrupted_data
        )
        assert export_result["success"] is False
    
    @pytest.mark.asyncio
    async def test_bem_naming_conventions(self, training_data_dir, all_tools):
        """Test that generated names follow BEM conventions."""
        # Use any available PDF
        pdf_files = list(training_data_dir.glob("*.pdf"))
        if not pdf_files:
            pytest.skip("No PDF files found in training data")
        
        test_pdf = pdf_files[0]
        
        # Extract and generate names
        extract_result = await all_tools["extract"].execute(
            pdf_path=str(test_pdf),
            context_radius=50
        )
        
        if not extract_result["success"] or extract_result["extraction_metadata"]["field_count"] == 0:
            pytest.skip("Failed to extract fields from PDF or no fields found")
        
        generate_result = await all_tools["generate"].execute(
            field_data=extract_result,
            use_training_data=True
        )
        
        assert generate_result["success"] is True
        
        # Check BEM naming patterns
        for name_entry in generate_result["generated_names"]:
            suggested_name = name_entry["suggested_name"]
            field_type = name_entry["field_type"]
            
            # Basic BEM structure checks
            if field_type == "RadioGroup":
                assert suggested_name.endswith("--group"), \
                    f"RadioGroup {suggested_name} should end with --group"
            
            # Should contain at least one underscore (block_element)
            if not suggested_name.endswith("--group"):
                assert "_" in suggested_name, \
                    f"Name {suggested_name} should follow block_element pattern"
            
            # Should not contain invalid characters
            import re
            assert re.match(r'^[a-z0-9_-]+$', suggested_name), \
                f"Name {suggested_name} contains invalid characters"
            
            # Should not be empty
            assert len(suggested_name.strip()) > 0, "Name should not be empty"


class TestMCPPerformance:
    """Performance tests for MCP tools."""
    
    @pytest.fixture
    def all_tools(self):
        """Create all MCP tool instances."""
        return {
            "extract": ExtractFieldsTool(),
            "generate": GenerateNamesTool(),
            "validate": ValidateNamesTool(),
            "export": ExportMappingTool()
        }
    
    @pytest.mark.asyncio
    async def test_processing_time_reasonable(self, all_tools):
        """Test that processing time is reasonable for typical PDFs."""
        import time
        
        # Create mock data for performance testing
        mock_field_data = {
            "success": True,
            "fields": [
                {
                    "UUID": f"field-{i}",
                    "Api name": f"field{i}",
                    "Type": "TextField",
                    "Label": f"Field {i}",
                    "Section ID": "test-section"
                }
                for i in range(50)  # 50 fields should be reasonable
            ]
        }
        
        # Test generate names performance
        start_time = time.time()
        generate_result = await all_tools["generate"].execute(
            field_data=mock_field_data,
            use_training_data=True
        )
        generate_time = time.time() - start_time
        
        assert generate_result["success"] is True
        assert generate_time < 10.0, f"Name generation took {generate_time:.2f}s (should be < 10s)"
        
        # Test validate names performance
        start_time = time.time()
        validate_result = await all_tools["validate"].execute(
            name_data=generate_result,
            check_duplicates=True,
            check_bem_compliance=True
        )
        validate_time = time.time() - start_time
        
        assert validate_result["success"] is True
        assert validate_time < 5.0, f"Name validation took {validate_time:.2f}s (should be < 5s)"
        
        # Test export performance
        start_time = time.time()
        export_result = await all_tools["export"].execute(
            validated_names=validate_result,
            output_format="json"
        )
        export_time = time.time() - start_time
        
        assert export_result["success"] is True
        assert export_time < 2.0, f"Export took {export_time:.2f}s (should be < 2s)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])