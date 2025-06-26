"""
Simplified MCP tools tests for basic functionality validation.
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


class TestMCPToolsBasic:
    """Basic functionality tests for MCP tools."""
    
    def test_tool_instantiation(self):
        """Test that all tools can be instantiated."""
        extract_tool = ExtractFieldsTool()
        generate_tool = GenerateNamesTool()
        validate_tool = ValidateNamesTool()
        export_tool = ExportMappingTool()
        
        assert extract_tool is not None
        assert generate_tool is not None
        assert validate_tool is not None
        assert export_tool is not None
    
    @pytest.mark.asyncio
    async def test_extract_fields_file_not_found(self):
        """Test extract_fields with non-existent file."""
        extract_tool = ExtractFieldsTool()
        
        result = await extract_tool.execute(
            pdf_path="/nonexistent/file.pdf",
            context_radius=50,
            output_format="csv"
        )
        
        assert result["success"] is False
        assert "error" in result
        assert result["error_type"] == "FileNotFoundError"
    
    @pytest.mark.asyncio
    async def test_generate_names_invalid_input(self):
        """Test generate_names with invalid input."""
        generate_tool = GenerateNamesTool()
        
        invalid_data = {"success": False, "error": "Test error"}
        
        result = await generate_tool.execute(
            field_data=invalid_data,
            use_training_data=True
        )
        
        assert result["success"] is False
        assert result["error_type"] == "InvalidInputError"
    
    @pytest.mark.asyncio
    async def test_validate_names_invalid_input(self):
        """Test validate_names with invalid input."""
        validate_tool = ValidateNamesTool()
        
        invalid_data = {"success": False}
        
        result = await validate_tool.execute(name_data=invalid_data)
        
        assert result["success"] is False
        assert result["error_type"] == "InvalidInputError"
    
    @pytest.mark.asyncio
    async def test_export_mapping_invalid_input(self):
        """Test export_mapping with invalid input."""
        export_tool = ExportMappingTool()
        
        invalid_data = {"success": False}
        
        result = await export_tool.execute(validated_names=invalid_data)
        
        assert result["success"] is False
        assert result["error_type"] == "InvalidInputError"
    
    @pytest.mark.asyncio
    async def test_export_mapping_invalid_format(self):
        """Test export_mapping with invalid format."""
        export_tool = ExportMappingTool()
        
        valid_data = {
            "success": True,
            "field_validations": []
        }
        
        result = await export_tool.execute(
            validated_names=valid_data,
            output_format="xml"  # Unsupported format
        )
        
        assert result["success"] is False
        assert result["error_type"] == "UnsupportedFormatError"
    
    def test_generate_names_bem_patterns(self):
        """Test BEM pattern loading."""
        generate_tool = GenerateNamesTool()
        
        assert "blocks" in generate_tool.bem_patterns
        assert "modifiers" in generate_tool.bem_patterns
        assert "radio_group_suffix" in generate_tool.bem_patterns
        assert generate_tool.bem_patterns["radio_group_suffix"] == "--group"
    
    def test_validate_names_bem_compliance(self):
        """Test BEM compliance checking."""
        validate_tool = ValidateNamesTool()
        
        # Test valid BEM name
        issues = validate_tool._check_bem_compliance("personal-information_first-name", "TextField")
        assert len(issues["errors"]) == 0
        
        # Test RadioGroup with correct suffix
        issues = validate_tool._check_bem_compliance("personal-information_gender--group", "RadioGroup")
        assert len(issues["errors"]) == 0
        
        # Test RadioGroup missing suffix
        issues = validate_tool._check_bem_compliance("personal-information_gender", "RadioGroup")
        assert len(issues["errors"]) > 0
    
    def test_export_mapping_confidence_calculation(self):
        """Test confidence calculation."""
        export_tool = ExportMappingTool()
        
        # High confidence case
        validation = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        confidence = export_tool._calculate_mapping_confidence(validation)
        assert confidence >= 0.8
        
        # Low confidence case
        validation = {
            "is_valid": False,
            "errors": [{"type": "test_error"}],
            "warnings": [{"type": "test_warning"}]
        }
        confidence = export_tool._calculate_mapping_confidence(validation)
        assert confidence < 0.8


class TestMCPToolsWithMockData:
    """Test MCP tools with mock data to verify data flow."""
    
    @pytest.mark.asyncio
    async def test_generate_names_success(self):
        """Test successful name generation with mock data."""
        generate_tool = GenerateNamesTool()
        
        mock_field_data = {
            "success": True,
            "fields": [
                {
                    "UUID": "field-1",
                    "Api name": "firstName",
                    "Type": "TextField",
                    "Label": "First Name",
                    "Section ID": "personal-info"
                }
            ]
        }
        
        result = await generate_tool.execute(
            field_data=mock_field_data,
            use_training_data=True,
            confidence_threshold=0.5
        )
        
        assert result["success"] is True
        assert "generation_metadata" in result
        assert "generated_names" in result
        assert len(result["generated_names"]) == 1
        
        # Check first generated name structure
        first_name = result["generated_names"][0]
        assert "field_id" in first_name
        assert "suggested_name" in first_name
        assert "confidence" in first_name
        assert "reasoning" in first_name
    
    @pytest.mark.asyncio
    async def test_validate_names_success(self):
        """Test successful name validation with mock data."""
        validate_tool = ValidateNamesTool()
        
        mock_name_data = {
            "success": True,
            "generated_names": [
                {
                    "field_id": "field-1",
                    "original_name": "firstName",
                    "suggested_name": "personal-information_first-name",
                    "field_type": "TextField",
                    "label": "First Name",
                    "confidence": 0.9
                }
            ]
        }
        
        result = await validate_tool.execute(
            name_data=mock_name_data,
            check_duplicates=True,
            check_bem_compliance=True
        )
        
        assert result["success"] is True
        assert "validation_metadata" in result
        assert "field_validations" in result
        assert len(result["field_validations"]) == 1
        
        # Check validation structure
        first_validation = result["field_validations"][0]
        assert "field_id" in first_validation
        assert "is_valid" in first_validation
        assert "errors" in first_validation
        assert "warnings" in first_validation
    
    @pytest.mark.asyncio
    async def test_export_mapping_json_success(self):
        """Test successful JSON export with mock data."""
        export_tool = ExportMappingTool()
        
        mock_validated_names = {
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
                }
            ]
        }
        
        result = await export_tool.execute(
            validated_names=mock_validated_names,
            output_format="json",
            include_metadata=True,
            include_backup_plan=True
        )
        
        assert result["success"] is True
        assert "export_metadata" in result
        assert "mapping_data" in result
        assert result["mapping_data"]["export_format"] == "json"
        assert "field_mappings" in result["mapping_data"]
        assert len(result["mapping_data"]["field_mappings"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])