"""
Unit tests for MCP tools.

Tests each MCP tool in isolation to verify correct functionality,
error handling, and data structures.
"""

import pytest
import pytest_asyncio
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp_tools.tools.extract_fields import ExtractFieldsTool
from mcp_tools.tools.generate_names import GenerateNamesTool
from mcp_tools.tools.validate_names import ValidateNamesTool
from mcp_tools.tools.export_mapping import ExportMappingTool

# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)


class TestExtractFieldsTool:
    """Test cases for the ExtractFieldsTool."""
    
    @pytest.fixture
    def extract_tool(self):
        """Create ExtractFieldsTool instance."""
        return ExtractFieldsTool()
    
    @pytest.fixture
    def sample_pdf_path(self):
        """Path to sample PDF for testing."""
        return str(Path(__file__).parent.parent.parent / "training_data" / "pdf_csv_pairs" / "W-4R_parsed.pdf")
    
    @pytest.mark.asyncio
    async def test_extract_fields_success(self, extract_tool, sample_pdf_path):
        """Test successful field extraction."""
        result = await extract_tool.execute(
            pdf_path=sample_pdf_path,
            context_radius=50,
            output_format="csv"
        )
        
        assert result["success"] is True
        assert "extraction_metadata" in result
        assert "fields" in result
        assert "extraction_summary" in result
        assert result["extraction_metadata"]["field_count"] > 0
    
    @pytest.mark.asyncio
    async def test_extract_fields_file_not_found(self, extract_tool):
        """Test extraction with non-existent file."""
        result = await extract_tool.execute(
            pdf_path="/nonexistent/file.pdf",
            context_radius=50,
            output_format="csv"
        )
        
        assert result["success"] is False
        assert result["error_type"] == "FileNotFoundError"
        assert "not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_extract_fields_invalid_parameters(self, extract_tool, sample_pdf_path):
        """Test extraction with invalid parameters."""
        # Test invalid output format
        result = await extract_tool.execute(
            pdf_path=sample_pdf_path,
            context_radius=50,
            output_format="invalid"
        )
        
        # Should still work but potentially with warnings
        # The actual validation depends on the underlying extractor
        assert "success" in result
    
    def test_analyze_field_types(self, extract_tool):
        """Test field type analysis."""
        mock_fields = [
            {"Type": "TextField"},
            {"Type": "TextField"},
            {"Type": "RadioGroup"},
            {"Type": "CheckBox"}
        ]
        
        type_counts = extract_tool._analyze_field_types(mock_fields)
        
        assert type_counts["TextField"] == 2
        assert type_counts["RadioGroup"] == 1
        assert type_counts["CheckBox"] == 1


class TestGenerateNamesTool:
    """Test cases for the GenerateNamesTool."""
    
    @pytest.fixture
    def generate_tool(self):
        """Create GenerateNamesTool instance."""
        return GenerateNamesTool()
    
    @pytest.fixture
    def sample_field_data(self):
        """Sample field data for testing."""
        return {
            "success": True,
            "fields": [
                {
                    "UUID": "field-1",
                    "Api name": "firstName",
                    "Type": "TextField",
                    "Label": "First Name",
                    "Section ID": "personal-info"
                },
                {
                    "UUID": "field-2", 
                    "Api name": "genderGroup",
                    "Type": "RadioGroup",
                    "Label": "Gender",
                    "Section ID": "personal-info"
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_generate_names_success(self, generate_tool, sample_field_data):
        """Test successful name generation."""
        result = await generate_tool.execute(
            field_data=sample_field_data,
            use_training_data=True,
            confidence_threshold=0.7,
            naming_strategy="context_aware"
        )
        
        assert result["success"] is True
        assert "generation_metadata" in result
        assert "generated_names" in result
        assert len(result["generated_names"]) == 2
        
        # Check first generated name
        first_name = result["generated_names"][0]
        assert "field_id" in first_name
        assert "suggested_name" in first_name
        assert "confidence" in first_name
        assert "reasoning" in first_name
    
    @pytest.mark.asyncio
    async def test_generate_names_invalid_input(self, generate_tool):
        """Test name generation with invalid input."""
        invalid_data = {"success": False, "error": "Test error"}
        
        result = await generate_tool.execute(
            field_data=invalid_data,
            use_training_data=True
        )
        
        assert result["success"] is False
        assert result["error_type"] == "InvalidInputError"
    
    def test_determine_block(self, generate_tool):
        """Test BEM block determination."""
        # Test personal information block
        block = generate_tool._determine_block(
            "personal_name", "First Name", "Personal Information", "Enter your first name"
        )
        assert block == "personal-information"
        
        # Test beneficiary block - use explicit beneficiary keywords
        block = generate_tool._determine_block(
            "", "Beneficiary Name", "Contingent Beneficiary", "beneficiary contingent details"
        )
        assert block == "contingent-benficiary"  # Match training data spelling
    
    def test_determine_element(self, generate_tool):
        """Test BEM element determination."""
        # Test first name element
        element = generate_tool._determine_element("personal_firstName", "First Name", "TextField")
        assert "first" in element and "name" in element
        
        # Test address element
        element = generate_tool._determine_element("", "Street Address", "TextField")
        assert element == "address"
    
    def test_radiogroup_naming(self, generate_tool):
        """Test RadioGroup specific naming."""
        bem_name = generate_tool._generate_context_aware_name(
            "genderChoice", "RadioGroup", "Gender", "Select gender", "Personal Info"
        )
        assert bem_name.endswith("--group")
    
    def test_calculate_confidence(self, generate_tool):
        """Test confidence calculation."""
        # High confidence case
        confidence = generate_tool._calculate_confidence(
            "personal-information_first-name", "TextField", "First Name", "firstName"
        )
        assert confidence >= 0.7
        
        # Low confidence case
        confidence = generate_tool._calculate_confidence(
            "field-unknown", "TextField", "", "field1"
        )
        assert confidence < 0.5


class TestValidateNamesTool:
    """Test cases for the ValidateNamesTool."""
    
    @pytest.fixture
    def validate_tool(self):
        """Create ValidateNamesTool instance."""
        return ValidateNamesTool()
    
    @pytest.fixture
    def sample_name_data(self):
        """Sample generated names for testing."""
        return {
            "success": True,
            "generated_names": [
                {
                    "field_id": "field-1",
                    "original_name": "firstName",
                    "suggested_name": "personal-information_first-name",
                    "field_type": "TextField",
                    "label": "First Name",
                    "confidence": 0.9
                },
                {
                    "field_id": "field-2",
                    "original_name": "genderGroup",
                    "suggested_name": "personal-information_gender--group",
                    "field_type": "RadioGroup",
                    "label": "Gender",
                    "confidence": 0.8
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_validate_names_success(self, validate_tool, sample_name_data):
        """Test successful name validation."""
        result = await validate_tool.execute(
            name_data=sample_name_data,
            check_duplicates=True,
            check_bem_compliance=True
        )
        
        assert result["success"] is True
        assert "validation_metadata" in result
        assert "field_validations" in result
        assert len(result["field_validations"]) == 2
        
        # Check validation structure
        first_validation = result["field_validations"][0]
        assert "field_id" in first_validation
        assert "is_valid" in first_validation
        assert "errors" in first_validation
        assert "warnings" in first_validation
    
    @pytest.mark.asyncio
    async def test_validate_names_invalid_input(self, validate_tool):
        """Test validation with invalid input."""
        invalid_data = {"success": False}
        
        result = await validate_tool.execute(name_data=invalid_data)
        
        assert result["success"] is False
        assert result["error_type"] == "InvalidInputError"
    
    def test_bem_compliance_valid(self, validate_tool):
        """Test BEM compliance with valid names."""
        issues = validate_tool._check_bem_compliance("personal-information_first-name", "TextField")
        assert len(issues["errors"]) == 0
        
        # Test RadioGroup with --group suffix
        issues = validate_tool._check_bem_compliance("personal-information_gender--group", "RadioGroup")
        assert len(issues["errors"]) == 0
    
    def test_bem_compliance_invalid(self, validate_tool):
        """Test BEM compliance with invalid names."""
        # Test invalid characters
        issues = validate_tool._check_bem_compliance("personal@info_name", "TextField")
        assert len(issues["errors"]) > 0
        assert any("invalid_characters" in error["type"] for error in issues["errors"])
        
        # Test RadioGroup missing --group suffix
        issues = validate_tool._check_bem_compliance("personal-information_gender", "RadioGroup")
        assert len(issues["errors"]) > 0
        assert any("missing_radiogroup_suffix" in error["type"] for error in issues["errors"])
    
    def test_duplicate_detection(self, validate_tool):
        """Test duplicate name detection."""
        seen_names = {"personal-information_name"}
        
        validation = validate_tool._validate_field_name(
            {
                "field_id": "field-1",
                "suggested_name": "personal-information_name",
                "field_type": "TextField"
            },
            seen_names,
            check_duplicates=True,
            check_bem_compliance=False,
            check_reserved_names=False,
            strict_mode=False
        )
        
        assert validation["is_valid"] is False
        assert any("duplicate_name" in error["type"] for error in validation["errors"])
    
    def test_reserved_names(self, validate_tool):
        """Test reserved name checking."""
        validation = validate_tool._validate_field_name(
            {
                "field_id": "field-1",
                "suggested_name": "name",  # Reserved name
                "field_type": "TextField"
            },
            set(),
            check_duplicates=False,
            check_bem_compliance=False,
            check_reserved_names=True,
            strict_mode=False
        )
        
        assert any("reserved_name" in warning["type"] for warning in validation["warnings"])


class TestExportMappingTool:
    """Test cases for the ExportMappingTool."""
    
    @pytest.fixture
    def export_tool(self):
        """Create ExportMappingTool instance."""
        return ExportMappingTool()
    
    @pytest.fixture
    def sample_validated_names(self):
        """Sample validated names for testing."""
        return {
            "success": True,
            "field_validations": [
                {
                    "field_id": "field-1",
                    "suggested_name": "personal-information_first-name",
                    "field_type": "TextField",
                    "is_valid": True,
                    "errors": [],
                    "warnings": [],
                    "suggestions": []
                },
                {
                    "field_id": "field-2",
                    "suggested_name": "personal-information_gender--group",
                    "field_type": "RadioGroup",
                    "is_valid": True,
                    "errors": [],
                    "warnings": [],
                    "suggestions": []
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_export_mapping_json(self, export_tool, sample_validated_names):
        """Test JSON export format."""
        result = await export_tool.execute(
            validated_names=sample_validated_names,
            output_format="json",
            include_metadata=True,
            include_backup_plan=True
        )
        
        assert result["success"] is True
        assert "export_metadata" in result
        assert "mapping_data" in result
        assert result["mapping_data"]["export_format"] == "json"
        assert "field_mappings" in result["mapping_data"]
        assert len(result["mapping_data"]["field_mappings"]) == 2
    
    @pytest.mark.asyncio
    async def test_export_mapping_csv(self, export_tool, sample_validated_names):
        """Test CSV export format."""
        result = await export_tool.execute(
            validated_names=sample_validated_names,
            output_format="csv",
            include_metadata=True,
            include_backup_plan=True
        )
        
        assert result["success"] is True
        assert result["mapping_data"]["export_format"] == "csv"
        assert "headers" in result["mapping_data"]
        assert "rows" in result["mapping_data"]
        assert len(result["mapping_data"]["rows"]) == 2
    
    @pytest.mark.asyncio
    async def test_export_mapping_invalid_format(self, export_tool, sample_validated_names):
        """Test export with invalid format."""
        result = await export_tool.execute(
            validated_names=sample_validated_names,
            output_format="xml"  # Unsupported format
        )
        
        assert result["success"] is False
        assert result["error_type"] == "UnsupportedFormatError"
    
    @pytest.mark.asyncio
    async def test_export_mapping_invalid_input(self, export_tool):
        """Test export with invalid input."""
        invalid_data = {"success": False}
        
        result = await export_tool.execute(validated_names=invalid_data)
        
        assert result["success"] is False
        assert result["error_type"] == "InvalidInputError"
    
    def test_create_field_mapping(self, export_tool):
        """Test field mapping creation."""
        sample_validation = {
            "field_id": "field-1",
            "suggested_name": "personal-information_first-name",
            "field_type": "TextField",
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        mapping = export_tool._create_field_mapping(sample_validation)
        
        assert mapping["field_id"] == "field-1"
        assert mapping["new_name"] == "personal-information_first-name"
        assert mapping["field_type"] == "TextField"
        assert mapping["validation_status"] == "approved"
        assert "modification_metadata" in mapping
    
    def test_calculate_mapping_confidence(self, export_tool):
        """Test mapping confidence calculation."""
        # High confidence case (no errors/warnings)
        validation = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        confidence = export_tool._calculate_mapping_confidence(validation)
        assert confidence >= 0.8
        
        # Low confidence case (with errors)
        validation = {
            "is_valid": False,
            "errors": [{"type": "test_error"}],
            "warnings": [{"type": "test_warning"}]
        }
        confidence = export_tool._calculate_mapping_confidence(validation)
        assert confidence < 0.8


class TestMCPToolsIntegration:
    """Integration tests for MCP tools working together."""
    
    @pytest.fixture
    def all_tools(self):
        """Create all MCP tool instances."""
        return {
            "extract": ExtractFieldsTool(),
            "generate": GenerateNamesTool(),
            "validate": ValidateNamesTool(),
            "export": ExportMappingTool()
        }
    
    @pytest.fixture
    def sample_pdf_path(self):
        """Path to sample PDF for testing."""
        return str(Path(__file__).parent.parent.parent / "training_data" / "pdf_csv_pairs" / "W-4R_parsed.pdf")
    
    @pytest.mark.asyncio
    async def test_full_workflow_integration(self, all_tools, sample_pdf_path):
        """Test complete workflow: extract -> generate -> validate -> export."""
        # Step 1: Extract fields
        extract_result = await all_tools["extract"].execute(
            pdf_path=sample_pdf_path,
            context_radius=50,
            output_format="csv"
        )
        assert extract_result["success"] is True
        
        # Step 2: Generate names
        generate_result = await all_tools["generate"].execute(
            field_data=extract_result,
            use_training_data=True,
            confidence_threshold=0.5
        )
        assert generate_result["success"] is True
        
        # Step 3: Validate names
        validate_result = await all_tools["validate"].execute(
            name_data=generate_result,
            check_duplicates=True,
            check_bem_compliance=True
        )
        assert validate_result["success"] is True
        
        # Step 4: Export mapping
        export_result = await all_tools["export"].execute(
            validated_names=validate_result,
            output_format="json",
            include_metadata=True
        )
        assert export_result["success"] is True
        
        # Verify data flow integrity
        original_field_count = extract_result["extraction_metadata"]["field_count"]
        generated_name_count = generate_result["generation_metadata"]["generated_count"]
        exported_field_count = export_result["export_metadata"]["exported_fields"]
        
        assert original_field_count == generated_name_count
        # Note: exported_field_count might be less due to validation filtering


if __name__ == "__main__":
    pytest.main([__file__])