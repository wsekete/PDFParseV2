"""
Export Mapping MCP Tool

Exports validated field mappings in structured format for PDF modification.
Creates the final output that the PDF modifier will use to safely rename fields.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ExportMappingTool:
    """MCP tool for exporting field mappings for PDF modification."""
    
    def __init__(self):
        """Initialize the export mapping tool."""
        self.supported_formats = ["json", "csv"]
        
    async def execute(
        self,
        validated_names: Dict[str, Any],
        output_format: str = "json",
        include_metadata: bool = True,
        include_backup_plan: bool = True,
        validation_threshold: float = 0.0
    ) -> Dict[str, Any]:
        """
        Export final field mapping for PDF modification.
        
        Args:
            validated_names: Validated names data from validate_names tool
            output_format: Export format ('json' or 'csv')
            include_metadata: Whether to include modification metadata
            include_backup_plan: Whether to include backup strategy
            validation_threshold: Minimum validation score to include field
            
        Returns:
            Dictionary containing structured mapping ready for PDF modifier
        """
        try:
            logger.info("Exporting field mapping for PDF modification")
            
            if not validated_names.get("success"):
                return {
                    "success": False,
                    "error": "Invalid validation data provided",
                    "error_type": "InvalidInputError"
                }
            
            if output_format not in self.supported_formats:
                return {
                    "success": False,
                    "error": f"Unsupported format: {output_format}",
                    "error_type": "UnsupportedFormatError"
                }
            
            field_validations = validated_names.get("field_validations", [])
            
            # Filter fields based on validation threshold
            valid_fields = [
                field for field in field_validations
                if field.get("is_valid", False) or validation_threshold == 0.0
            ]
            
            # Create the mapping structure
            mapping = self._create_mapping_structure(
                valid_fields, include_metadata, include_backup_plan
            )
            
            # Export in requested format
            if output_format == "json":
                exported_data = self._export_json_format(mapping)
            else:  # csv
                exported_data = self._export_csv_format(mapping)
            
            result = {
                "success": True,
                "export_metadata": {
                    "total_fields": len(field_validations),
                    "exported_fields": len(valid_fields),
                    "filtered_fields": len(field_validations) - len(valid_fields),
                    "output_format": output_format,
                    "validation_threshold": validation_threshold,
                    "export_timestamp": datetime.now().isoformat()
                },
                "mapping_data": exported_data,
                "export_summary": {
                    "ready_for_modification": len([
                        f for f in valid_fields if f.get("is_valid", False)
                    ]),
                    "requires_review": len([
                        f for f in valid_fields if not f.get("is_valid", False)
                    ]),
                    "backup_recommended": include_backup_plan
                }
            }
            
            logger.info(f"Exported mapping for {len(valid_fields)} fields")
            return result
            
        except Exception as e:
            logger.error(f"Error in export_mapping: {str(e)}")
            return {
                "success": False,
                "error": f"Export error: {str(e)}",
                "error_type": type(e).__name__
            }
    
    def _create_mapping_structure(
        self,
        valid_fields: List[Dict[str, Any]],
        include_metadata: bool,
        include_backup_plan: bool
    ) -> Dict[str, Any]:
        """Create the core mapping structure."""
        
        mapping = {
            "format_version": "1.0",
            "field_mappings": []
        }
        
        # Add metadata if requested
        if include_metadata:
            mapping["pdf_metadata"] = {
                "extraction_timestamp": datetime.now().isoformat(),
                "field_count": len(valid_fields),
                "modification_tool": "PDFParseV2",
                "modification_version": "2.0.0"
            }
        
        # Add backup plan if requested
        if include_backup_plan:
            mapping["modification_plan"] = {
                "backup_required": True,
                "backup_suffix": "_backup",
                "modification_type": "acrofield_rename",
                "estimated_changes": len(valid_fields),
                "rollback_supported": True,
                "verification_required": True
            }
        
        # Process field mappings
        for field_validation in valid_fields:
            field_mapping = self._create_field_mapping(field_validation)
            mapping["field_mappings"].append(field_mapping)
        
        return mapping
    
    def _create_field_mapping(self, field_validation: Dict[str, Any]) -> Dict[str, Any]:
        """Create mapping entry for a single field."""
        
        return {
            "field_id": field_validation.get("field_id"),
            "original_name": self._extract_original_name(field_validation),
            "new_name": field_validation.get("suggested_name"),
            "field_type": field_validation.get("field_type"),
            "validation_status": "approved" if field_validation.get("is_valid") else "needs_review",
            "validation_issues": {
                "errors": field_validation.get("errors", []),
                "warnings": field_validation.get("warnings", []),
                "suggestions": field_validation.get("suggestions", [])
            },
            "modification_metadata": {
                "requires_manual_review": not field_validation.get("is_valid", False),
                "confidence_score": self._calculate_mapping_confidence(field_validation),
                "backup_original": True,
                "verify_after_change": True
            }
        }
    
    def _extract_original_name(self, field_validation: Dict[str, Any]) -> str:
        """Extract the original field name from validation data."""
        # This would need to be passed through from the original extraction
        # For now, we'll use a placeholder
        return field_validation.get("original_name", f"original_{field_validation.get('field_id', 'unknown')}")
    
    def _calculate_mapping_confidence(self, field_validation: Dict[str, Any]) -> float:
        """Calculate overall confidence for this field mapping."""
        
        base_confidence = 0.8  # Base confidence
        
        # Reduce confidence for validation issues
        error_count = len(field_validation.get("errors", []))
        warning_count = len(field_validation.get("warnings", []))
        
        confidence = base_confidence
        confidence -= (error_count * 0.3)  # Errors significantly reduce confidence
        confidence -= (warning_count * 0.1)  # Warnings slightly reduce confidence
        
        # Boost confidence if the field is marked as valid
        if field_validation.get("is_valid", False):
            confidence += 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _export_json_format(self, mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Export mapping in JSON format."""
        
        # Add JSON-specific metadata
        mapping["export_format"] = "json"
        mapping["usage_instructions"] = {
            "description": "This mapping can be used by PDF modification tools",
            "required_fields": ["field_id", "original_name", "new_name"],
            "backup_recommended": True,
            "validation_required": True
        }
        
        return mapping
    
    def _export_csv_format(self, mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Export mapping in CSV-compatible format."""
        
        # Create CSV-style data structure
        csv_data = {
            "export_format": "csv",
            "headers": [
                "field_id", "original_name", "new_name", "field_type", 
                "validation_status", "confidence_score", "requires_review"
            ],
            "rows": []
        }
        
        # Convert mappings to CSV rows
        for field_mapping in mapping.get("field_mappings", []):
            row = [
                field_mapping.get("field_id", ""),
                field_mapping.get("original_name", ""),
                field_mapping.get("new_name", ""),
                field_mapping.get("field_type", ""),
                field_mapping.get("validation_status", ""),
                field_mapping.get("modification_metadata", {}).get("confidence_score", 0.0),
                field_mapping.get("modification_metadata", {}).get("requires_manual_review", False)
            ]
            csv_data["rows"].append(row)
        
        # Add metadata as separate section
        csv_data["metadata"] = mapping.get("pdf_metadata", {})
        csv_data["modification_plan"] = mapping.get("modification_plan", {})
        
        return csv_data
    
    def save_to_file(
        self, 
        mapping_data: Dict[str, Any], 
        output_path: str
    ) -> Dict[str, Any]:
        """Save mapping data to file."""
        
        try:
            output_file = Path(output_path)
            
            if mapping_data.get("export_format") == "json":
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(mapping_data, f, indent=2, ensure_ascii=False)
            
            elif mapping_data.get("export_format") == "csv":
                import csv
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(mapping_data["headers"])
                    writer.writerows(mapping_data["rows"])
            
            return {
                "success": True,
                "file_path": str(output_file),
                "file_size": output_file.stat().st_size
            }
            
        except Exception as e:
            logger.error(f"Error saving mapping to file: {str(e)}")
            return {
                "success": False,
                "error": f"File save error: {str(e)}"
            }