"""
Validate Names MCP Tool

Validates generated field names for BEM compliance, conflicts, and best practices.
Provides suggestions for improvements and conflict resolution.
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional, Set

logger = logging.getLogger(__name__)

class ValidateNamesTool:
    """MCP tool for validating generated field names."""
    
    def __init__(self):
        """Initialize the validate names tool."""
        self.bem_pattern = re.compile(r'^[a-z][a-z0-9-]*(_[a-z][a-z0-9-]*)?(__[a-z][a-z0-9-]*)?(--group)?$')
        self.reserved_names = {
            'id', 'name', 'value', 'type', 'class', 'style', 'onclick',
            'onchange', 'onload', 'submit', 'reset', 'button', 'input'
        }
        
    async def execute(
        self,
        name_data: Dict[str, Any],
        check_duplicates: bool = True,
        check_bem_compliance: bool = True,
        check_reserved_names: bool = True,
        strict_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Validate generated field names for compliance and conflicts.
        
        Args:
            name_data: Generated names data from generate_names tool
            check_duplicates: Whether to check for duplicate names
            check_bem_compliance: Whether to validate BEM syntax
            check_reserved_names: Whether to check against reserved names
            strict_mode: Enable strict validation rules
            
        Returns:
            Dictionary containing validation results and suggestions
        """
        try:
            logger.info("Validating generated field names")
            
            if not name_data.get("success"):
                return {
                    "success": False,
                    "error": "Invalid name data provided",
                    "error_type": "InvalidInputError"
                }
            
            generated_names = name_data.get("generated_names", [])
            
            validation_results = {
                "success": True,
                "validation_metadata": {
                    "total_names": len(generated_names),
                    "validation_rules": {
                        "check_duplicates": check_duplicates,
                        "check_bem_compliance": check_bem_compliance,
                        "check_reserved_names": check_reserved_names,
                        "strict_mode": strict_mode
                    }
                },
                "validation_summary": {
                    "valid_names": 0,
                    "warnings": 0,
                    "errors": 0,
                    "suggestions": 0
                },
                "field_validations": [],
                "global_issues": []
            }
            
            # Track seen names for duplicate detection
            seen_names: Set[str] = set()
            
            # Validate each field name
            for name_entry in generated_names:
                field_validation = self._validate_field_name(
                    name_entry, seen_names, check_duplicates,
                    check_bem_compliance, check_reserved_names, strict_mode
                )
                
                validation_results["field_validations"].append(field_validation)
                
                # Update counters
                if field_validation["is_valid"]:
                    validation_results["validation_summary"]["valid_names"] += 1
                
                validation_results["validation_summary"]["warnings"] += len(field_validation["warnings"])
                validation_results["validation_summary"]["errors"] += len(field_validation["errors"])
                validation_results["validation_summary"]["suggestions"] += len(field_validation["suggestions"])
                
                # Track name for duplicate checking
                suggested_name = name_entry.get("suggested_name", "")
                if suggested_name:
                    seen_names.add(suggested_name)
            
            # Check for global issues
            global_issues = self._check_global_issues(generated_names, strict_mode)
            validation_results["global_issues"] = global_issues
            
            # Generate overall recommendations
            validation_results["recommendations"] = self._generate_recommendations(
                validation_results
            )
            
            logger.info(f"Validated {len(generated_names)} field names")
            return validation_results
            
        except Exception as e:
            logger.error(f"Error in validate_names: {str(e)}")
            return {
                "success": False,
                "error": f"Validation error: {str(e)}",
                "error_type": type(e).__name__
            }
    
    def _validate_field_name(
        self,
        name_entry: Dict[str, Any],
        seen_names: Set[str],
        check_duplicates: bool,
        check_bem_compliance: bool,
        check_reserved_names: bool,
        strict_mode: bool
    ) -> Dict[str, Any]:
        """Validate a single field name."""
        
        field_id = name_entry.get("field_id", "unknown")
        suggested_name = name_entry.get("suggested_name", "")
        field_type = name_entry.get("field_type", "TextField")
        original_name = name_entry.get("original_name", "")
        confidence = name_entry.get("confidence", 0.0)
        
        validation = {
            "field_id": field_id,
            "suggested_name": suggested_name,
            "field_type": field_type,
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Check for empty or invalid names
        if not suggested_name or not suggested_name.strip():
            validation["errors"].append({
                "type": "empty_name",
                "message": "Field name cannot be empty",
                "suggestion": f"Use pattern: {field_type.lower()}-field"
            })
            validation["is_valid"] = False
        
        # Check BEM compliance
        if check_bem_compliance and suggested_name:
            bem_issues = self._check_bem_compliance(suggested_name, field_type)
            validation["errors"].extend(bem_issues["errors"])
            validation["warnings"].extend(bem_issues["warnings"])
            validation["suggestions"].extend(bem_issues["suggestions"])
            if bem_issues["errors"]:
                validation["is_valid"] = False
        
        # Check for duplicates
        if check_duplicates and suggested_name in seen_names:
            validation["errors"].append({
                "type": "duplicate_name",
                "message": f"Duplicate name '{suggested_name}' found",
                "suggestion": f"{suggested_name}_alt"
            })
            validation["is_valid"] = False
        
        # Check reserved names
        if check_reserved_names and suggested_name.lower() in self.reserved_names:
            validation["warnings"].append({
                "type": "reserved_name",
                "message": f"'{suggested_name}' is a reserved name",
                "suggestion": f"custom_{suggested_name}"
            })
        
        # Strict mode additional checks
        if strict_mode:
            strict_issues = self._check_strict_mode(suggested_name, field_type, confidence)
            validation["warnings"].extend(strict_issues["warnings"])
            validation["suggestions"].extend(strict_issues["suggestions"])
        
        # Check field type consistency
        type_issues = self._check_field_type_consistency(suggested_name, field_type)
        validation["warnings"].extend(type_issues)
        
        return validation
    
    def _check_bem_compliance(self, name: str, field_type: str) -> Dict[str, List[Dict[str, str]]]:
        """Check BEM naming convention compliance."""
        
        issues = {
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Check basic BEM pattern
        if not self.bem_pattern.match(name):
            issues["errors"].append({
                "type": "invalid_bem_syntax",
                "message": f"'{name}' does not follow BEM convention",
                "suggestion": "Use format: block_element or block_element__modifier"
            })
            return issues
        
        # Check RadioGroup suffix
        if field_type == "RadioGroup":
            if not name.endswith("--group"):
                issues["errors"].append({
                    "type": "missing_radiogroup_suffix",
                    "message": "RadioGroup fields must end with --group",
                    "suggestion": f"{name}--group"
                })
        elif name.endswith("--group") and field_type != "RadioGroup":
            issues["warnings"].append({
                "type": "unnecessary_group_suffix",
                "message": "Only RadioGroup fields should have --group suffix",
                "suggestion": name.replace("--group", "")
            })
        
        # Check for proper block_element structure
        if "_" not in name and not name.endswith("--group"):
            issues["warnings"].append({
                "type": "missing_block_element_separator",
                "message": "BEM names should have block_element structure",
                "suggestion": f"general_{name}"
            })
        
        # Check for invalid characters
        if re.search(r'[^a-z0-9_-]', name):
            issues["errors"].append({
                "type": "invalid_characters",
                "message": "Name contains invalid characters",
                "suggestion": "Use only lowercase letters, numbers, hyphens, and underscores"
            })
        
        # Check length limits
        if len(name) > 100:
            issues["warnings"].append({
                "type": "name_too_long",
                "message": f"Name is {len(name)} characters (limit: 100)",
                "suggestion": name[:97] + "..."
            })
        elif len(name) < 3:
            issues["warnings"].append({
                "type": "name_too_short",
                "message": "Name is very short and may not be descriptive",
                "suggestion": f"descriptive_{name}"
            })
        
        return issues
    
    def _check_strict_mode(
        self, 
        name: str, 
        field_type: str, 
        confidence: float
    ) -> Dict[str, List[Dict[str, str]]]:
        """Additional checks for strict mode."""
        
        issues = {
            "warnings": [],
            "suggestions": []
        }
        
        # Check confidence threshold
        if confidence < 0.8:
            issues["warnings"].append({
                "type": "low_confidence",
                "message": f"Low confidence ({confidence:.2f}) for generated name",
                "suggestion": "Consider manual review"
            })
        
        # Check for generic names
        if any(generic in name.lower() for generic in ["field", "input", "control", "element"]):
            issues["warnings"].append({
                "type": "generic_name",
                "message": "Name appears to be generic",
                "suggestion": "Use more specific descriptive name"
            })
        
        # Check abbreviations
        if len([part for part in name.split("_") if len(part) <= 2]) > 0:
            issues["suggestions"].append({
                "type": "short_abbreviations",
                "message": "Consider spelling out abbreviations for clarity",
                "suggestion": "Use full words where possible"
            })
        
        return issues
    
    def _check_field_type_consistency(self, name: str, field_type: str) -> List[Dict[str, str]]:
        """Check consistency between name and field type."""
        
        warnings = []
        
        # Check signature fields
        if field_type == "Signature" and "signature" not in name.lower():
            warnings.append({
                "type": "type_name_mismatch",
                "message": "Signature field should contain 'signature' in name",
                "suggestion": f"{name}_signature"
            })
        
        # Check date fields
        if "date" in name.lower() and field_type not in ["TextField", "Signature"]:
            warnings.append({
                "type": "date_field_type_mismatch",
                "message": "Date fields are typically TextField or Signature types",
                "suggestion": "Verify field type is correct"
            })
        
        return warnings
    
    def _check_global_issues(
        self, 
        generated_names: List[Dict[str, Any]], 
        strict_mode: bool
    ) -> List[Dict[str, str]]:
        """Check for global naming issues across all fields."""
        
        global_issues = []
        
        # Check naming consistency across similar fields
        blocks = {}
        for name_entry in generated_names:
            suggested_name = name_entry.get("suggested_name", "")
            if "_" in suggested_name:
                block = suggested_name.split("_")[0]
                if block not in blocks:
                    blocks[block] = []
                blocks[block].append(suggested_name)
        
        # Check for block consistency
        for block, names in blocks.items():
            if len(names) == 1:
                global_issues.append({
                    "type": "orphaned_block",
                    "message": f"Block '{block}' has only one field",
                    "suggestion": f"Consider grouping related fields or using different block"
                })
        
        # Check for RadioGroup consistency
        radio_groups = [
            name_entry for name_entry in generated_names
            if name_entry.get("field_type") == "RadioGroup"
        ]
        
        radio_buttons = [
            name_entry for name_entry in generated_names
            if name_entry.get("field_type") == "RadioButton"
        ]
        
        if len(radio_groups) > 0 and len(radio_buttons) == 0:
            global_issues.append({
                "type": "radiogroup_without_buttons",
                "message": "Found RadioGroups but no RadioButtons",
                "suggestion": "Verify RadioButton extraction and naming"
            })
        
        return global_issues
    
    def _generate_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """Generate overall recommendations based on validation results."""
        
        recommendations = []
        
        summary = validation_results["validation_summary"]
        total_names = validation_results["validation_metadata"]["total_names"]
        
        # Overall health check
        valid_percentage = (summary["valid_names"] / total_names * 100) if total_names > 0 else 0
        
        if valid_percentage >= 90:
            recommendations.append("✅ Excellent: Most field names are valid and ready for use")
        elif valid_percentage >= 70:
            recommendations.append("⚠️ Good: Some field names need minor adjustments")
        else:
            recommendations.append("❌ Needs Work: Many field names require review and correction")
        
        # Specific recommendations
        if summary["errors"] > 0:
            recommendations.append(f"🔧 Fix {summary['errors']} critical errors before proceeding")
        
        if summary["warnings"] > 5:
            recommendations.append("⚠️ Consider addressing warnings for better naming consistency")
        
        if len(validation_results["global_issues"]) > 0:
            recommendations.append("🌐 Review global issues for overall naming strategy")
        
        return recommendations