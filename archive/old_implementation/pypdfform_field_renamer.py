"""
PyPDFForm-based PDF field renaming implementation.
Replaces PyPDF2 approach with improved field detection and renaming.

This module provides a high-performance PDF field renamer using PyPDFForm
with reliable field detection via sample_data property and robust error handling.
"""

from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import logging
from dataclasses import dataclass
import traceback

try:
    from PyPDFForm import PdfWrapper
except ImportError as e:
    raise ImportError(
        "PyPDFForm is required but not installed. "
        "Please install it with: pip install PyPDFForm==3.1.2"
    ) from e


@dataclass
class FieldRenameResult:
    """Result of a single field renaming operation."""
    success: bool
    old_name: str
    new_name: str
    error: Optional[str] = None


@dataclass
class ProgressUpdate:
    """Progress update information for long-running operations."""
    current: int
    total: int
    percentage: float
    operation: str
    elapsed_time: float


class PyPDFFormFieldRenamer:
    """
    High-performance PDF field renamer using PyPDFForm.
    
    This class provides a clean interface for renaming PDF form fields
    with reliable field detection and robust error handling.
    
    Features:
    - Reliable field detection using sample_data property
    - Progress tracking for bulk operations  
    - Field validation before processing
    - Enhanced error handling and reporting
    - Support for all PDF field types (text, checkbox, radio, etc.)
    - Automatic field type detection
    
    Example:
        >>> renamer = PyPDFFormFieldRenamer("document.pdf")
        >>> if renamer.load_pdf():
        ...     mappings = {"old_field": "new_field"}
        ...     results = renamer.rename_fields(mappings)
        ...     if renamer.save_pdf("output.pdf"):
        ...         print(f"Success rate: {renamer.get_success_rate(results):.1f}%")
    """
    
    def __init__(self, pdf_path: str, progress_callback: Optional[Callable] = None):
        """
        Initialize the PyPDFForm field renamer.
        
        Args:
            pdf_path: Path to the PDF file to process
            progress_callback: Optional callback for progress updates
        """
        self.pdf_path = Path(pdf_path)
        self.wrapper: Optional[PdfWrapper] = None
        self.progress_callback = progress_callback
        self.logger = logging.getLogger(__name__)
        
        # Validate PDF path
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    def load_pdf(self) -> bool:
        """
        Load PDF file with PyPDFForm.
        
        Returns:
            True if PDF loaded successfully, False otherwise
        """
        try:
            self.wrapper = PdfWrapper(str(self.pdf_path))
            self.logger.info(f"Successfully loaded PDF: {self.pdf_path.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load PDF {self.pdf_path}: {e}")
            return False
    
    def extract_fields(self) -> List[Dict[str, Any]]:
        """
        Extract all form fields from PDF using PyPDFForm's sample_data with enhanced metadata.
        
        This method uses the proven sample_data property which reliably
        detects all form fields in the PDF, and adds relationship detection
        for RadioGroups and nested field hierarchies.
        
        Returns:
            List of field information dictionaries with enhanced metadata
        """
        if not self.wrapper:
            self.logger.error("PDF not loaded. Call load_pdf() first.")
            return []
        
        try:
            fields = []
            
            # Use sample_data property - the reliable method for field detection
            try:
                sample_data = self.wrapper.sample_data
                if sample_data:
                    # First pass: create basic field info
                    for field_name, field_value in sample_data.items():
                        field_type = self._detect_field_type(field_name, field_value)
                        
                        # Extract field information with enhanced metadata
                        field_info = {
                            'name': field_name,
                            'value': field_value,
                            'type': field_type,
                            'properties': {
                                'sample_value': field_value,
                                'is_empty': not bool(str(field_value).strip()) if field_value else True,
                                'has_double_underscore': '__' in field_name,
                                'has_single_underscore': '_' in field_name,
                                'ends_with_group': field_name.endswith('--group')
                            }
                        }
                        
                        # Add relationship metadata
                        field_info.update(self._analyze_field_relationships(field_name, field_type))
                        
                        fields.append(field_info)
                    
                    # Second pass: add parent-child relationship validation
                    fields = self._enhance_field_relationships(fields)
                    
                    # Log field type distribution for validation
                    type_counts = {}
                    for field in fields:
                        field_type = field['type']
                        type_counts[field_type] = type_counts.get(field_type, 0) + 1
                    
                    self.logger.info(f"Successfully extracted {len(fields)} fields using sample_data")
                    self.logger.info(f"Field type distribution: {type_counts}")
                    
                    # Validate against expected LIFE-1528-Q pattern (if applicable)
                    if len(fields) > 50:  # Likely LIFE-1528-Q or similar complex form
                        self._validate_complex_form_structure(fields, type_counts)
                
                else:
                    self.logger.warning("sample_data returned empty - no form fields detected")
                    
            except Exception as e:
                self.logger.error(f"Failed to access sample_data: {e}")
                
                # Fallback: try schema method (legacy)
                try:
                    schema = self.wrapper.schema
                    if schema:
                        self.logger.info("Falling back to schema method")
                        for field_name, field_info in schema.items():
                            fields.append({
                                'name': field_name,
                                'type': field_info.get('type', 'unknown'),
                                'properties': field_info,
                                'value': None
                            })
                except (AttributeError, Exception) as schema_error:
                    self.logger.warning(f"Schema fallback also failed: {schema_error}")
            
            self.logger.info(f"Final result: extracted {len(fields)} fields from PDF")
            return fields
            
        except Exception as e:
            self.logger.error(f"Failed to extract fields: {e}")
            return []
    
    def _detect_field_type(self, field_name: str, field_value: Any) -> str:
        """
        Enhanced field type detection based on LIFE-1528-Q training data patterns.
        
        Patterns observed in training data:
        - RadioGroups: end with '--group' (e.g., 'address-change--group', 'dividend--group')
        - RadioButtons: use '_' for grouping (e.g., 'dividend_accumulate', 'stop_direct')
        - Nested TextFields: use '__' for sub-fields (e.g., 'address-change_owner__name')
        
        Args:
            field_name: Name of the field
            field_value: Current value of the field
            
        Returns:
            Detected field type as string
        """
        name_lower = field_name.lower()
        
        # RadioGroup detection (MOST SPECIFIC - check first)
        if field_name.endswith('--group'):
            return 'RadioGroup'
        
        # Signature field detection
        if ('signature' in name_lower or 'sign' in name_lower) and 'date' not in name_lower:
            return 'Signature'
        
        # Date field detection (including signature dates)
        if 'date' in name_lower:
            return 'SignatureDate'
        
        # RadioButton detection based on training data patterns
        # Pattern: section_option (e.g., dividend_accumulate, stop_direct, name-change_insured)
        if ('_' in field_name and '__' not in field_name and 
            not field_name.endswith('--group') and
            not any(x in name_lower for x in ['signature', 'date', 'former', 'present', 'amount', 'specify'])):
            
            # Check for known RadioButton patterns from training data
            radio_patterns = [
                'dividend_', 'stop_', 'frequency_', 'name-change_', 'address-change_'
            ]
            if any(field_name.startswith(pattern) for pattern in radio_patterns):
                return 'RadioButton'
        
        # Nested TextField detection (uses __ pattern)
        # Pattern: section_option__field (e.g., address-change_owner__name)
        if '__' in field_name:
            return 'TextField'
        
        # Checkbox detection (specific patterns from training data)
        if (('same' in name_lower and 'owner' in name_lower) or
            ('change' in name_lower and 'amount' in name_lower) or
            'check' in name_lower or 'box' in name_lower):
            return 'CheckBox'
        
        # Standalone TextField patterns (common field names)
        if any(x in name_lower for x in ['name', 'former', 'present', 'amount', 'specify', 'first', 'last', 'address', 'city', 'state', 'zip', 'phone', 'email', 'ssn', 'contract']):
            return 'TextField'
        
        # Default to TextField for unknown patterns
        return 'TextField'
    
    def _analyze_field_relationships(self, field_name: str, field_type: str) -> Dict[str, Any]:
        """
        Analyze field relationships for RadioGroups and hierarchical structures.
        
        Args:
            field_name: Name of the field to analyze
            field_type: Detected field type
            
        Returns:
            Dictionary with relationship metadata
        """
        relationships = {
            'parent_group': None,
            'is_nested': False,
            'nesting_level': 0,
            'group_prefix': None
        }
        
        # Analyze RadioGroup relationships
        if field_type == 'RadioGroup':
            # Extract group prefix (e.g., 'address-change' from 'address-change--group')
            if field_name.endswith('--group'):
                relationships['group_prefix'] = field_name[:-7]  # Remove '--group'
        
        elif field_type == 'RadioButton':
            # Find parent group by pattern matching
            # Pattern: 'section_option' where parent would be 'section--group'
            if '_' in field_name:
                parts = field_name.split('_', 1)
                if len(parts) >= 2:
                    potential_parent = f"{parts[0]}--group"
                    relationships['parent_group'] = potential_parent
                    relationships['group_prefix'] = parts[0]
        
        elif field_type == 'TextField' and '__' in field_name:
            # Nested TextField analysis: section_option__field
            # Parent could be RadioButton: section_option
            parts = field_name.split('__', 1)
            if len(parts) >= 2:
                potential_parent = parts[0]  # e.g., 'address-change_owner'
                relationships['parent_group'] = potential_parent
                relationships['is_nested'] = True
                relationships['nesting_level'] = 2
                
                # Also identify the main group
                if '_' in potential_parent:
                    group_parts = potential_parent.split('_', 1)
                    if len(group_parts) >= 2:
                        relationships['group_prefix'] = group_parts[0]
        
        return relationships
    
    def _enhance_field_relationships(self, fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance field relationships by cross-referencing all fields.
        
        Args:
            fields: List of field dictionaries
            
        Returns:
            Enhanced fields list with validated relationships
        """
        # Create field name lookup for validation
        field_names = {field['name'] for field in fields}
        
        for field in fields:
            parent_group = field.get('parent_group')
            if parent_group and parent_group in field_names:
                field['parent_exists'] = True
                field['parent_validated'] = True
            else:
                field['parent_exists'] = False
                field['parent_validated'] = False
        
        return fields
    
    def _validate_complex_form_structure(self, fields: List[Dict[str, Any]], type_counts: Dict[str, int]):
        """
        Validate complex form structure against expected patterns (like LIFE-1528-Q).
        
        Args:
            fields: List of extracted fields
            type_counts: Count of each field type
        """
        # Expected LIFE-1528-Q structure:
        # - 6 RadioGroups
        # - 20+ RadioButtons  
        # - 15+ TextFields
        # - Total: ~73 fields
        
        radio_groups = type_counts.get('RadioGroup', 0)
        radio_buttons = type_counts.get('RadioButton', 0)
        text_fields = type_counts.get('TextField', 0)
        
        self.logger.info(f"Complex form validation:")
        self.logger.info(f"  RadioGroups: {radio_groups} (expected: ~6)")
        self.logger.info(f"  RadioButtons: {radio_buttons} (expected: ~20)")
        self.logger.info(f"  TextFields: {text_fields} (expected: ~45)")
        
        # Validate RadioGroup patterns
        radio_group_fields = [f for f in fields if f['type'] == 'RadioGroup']
        if radio_group_fields:
            self.logger.info(f"RadioGroup fields detected:")
            for field in radio_group_fields:
                self.logger.info(f"  - {field['name']}")
        
        # Warn if numbers are significantly off
        if radio_groups == 0 and len(fields) > 50:
            self.logger.warning("No RadioGroups detected in complex form - possible detection issue")
        
        if radio_buttons == 0 and len(fields) > 50:
            self.logger.warning("No RadioButtons detected in complex form - possible detection issue")
    
    def rename_fields(self, mappings: Dict[str, str]) -> List[FieldRenameResult]:
        """
        Rename multiple fields with progress tracking.
        
        Args:
            mappings: Dictionary mapping old field names to new field names
            
        Returns:
            List of FieldRenameResult objects with detailed results
        """
        if not self.wrapper:
            raise RuntimeError("PDF not loaded. Call load_pdf() first.")
        
        results = []
        total_fields = len(mappings)
        
        self.logger.info(f"Starting field renaming: {total_fields} fields")
        
        # Report initial progress
        if self.progress_callback:
            progress = ProgressUpdate(
                current=0,
                total=total_fields,
                percentage=0.0,
                operation="Initializing field renaming",
                elapsed_time=0.0
            )
            self.progress_callback(progress)
        
        import time
        start_time = time.time()
        
        for i, (old_name, new_name) in enumerate(mappings.items(), 1):
            result = FieldRenameResult(
                success=False,
                old_name=old_name,
                new_name=new_name
            )
            
            try:
                # Attempt to rename the field using PyPDFForm's update_widget_key
                self.wrapper = self.wrapper.update_widget_key(old_name, new_name)
                result.success = True
                self.logger.debug(f"Successfully renamed: {old_name} → {new_name}")
                
            except Exception as e:
                result.error = str(e)
                self.logger.warning(f"Failed to rename {old_name} → {new_name}: {e}")
            
            results.append(result)
            
            # Report progress
            if self.progress_callback:
                elapsed = time.time() - start_time
                progress = ProgressUpdate(
                    current=i,
                    total=total_fields,
                    percentage=(i / total_fields) * 100,
                    operation=f"Renaming field {i}/{total_fields}",
                    elapsed_time=elapsed
                )
                self.progress_callback(progress)
        
        # Report completion
        successful = sum(1 for r in results if r.success)
        success_rate = (successful / total_fields) * 100 if total_fields > 0 else 0
        
        self.logger.info(
            f"Field renaming completed: {successful}/{total_fields} "
            f"successful ({success_rate:.1f}%)"
        )
        
        if self.progress_callback:
            elapsed = time.time() - start_time
            progress = ProgressUpdate(
                current=total_fields,
                total=total_fields,
                percentage=100.0,
                operation="Field renaming completed",
                elapsed_time=elapsed
            )
            self.progress_callback(progress)
        
        return results
    
    def validate_mappings(self, mappings: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Validate field mappings before applying changes.
        
        Args:
            mappings: Dictionary of field name mappings to validate
            
        Returns:
            Dictionary with 'errors' and 'warnings' lists
        """
        validation_results = {
            'errors': [],
            'warnings': []
        }
        
        if not mappings:
            validation_results['errors'].append("No field mappings provided")
            return validation_results
        
        # Check for duplicate target names
        new_names = list(mappings.values())
        duplicates = set([name for name in new_names if new_names.count(name) > 1])
        if duplicates:
            validation_results['errors'].extend([
                f"Duplicate target name: {name}" for name in duplicates
            ])
        
        # Check for empty names
        for old_name, new_name in mappings.items():
            if not old_name.strip():
                validation_results['errors'].append("Empty source field name found")
            if not new_name.strip():
                validation_results['errors'].append(f"Empty target name for field: {old_name}")
        
        # Check for self-mappings (unnecessary operations)
        self_mappings = [old for old, new in mappings.items() if old == new]
        if self_mappings:
            validation_results['warnings'].extend([
                f"Field maps to itself (no change needed): {name}" 
                for name in self_mappings
            ])
        
        self.logger.info(
            f"Validation completed: {len(validation_results['errors'])} errors, "
            f"{len(validation_results['warnings'])} warnings"
        )
        
        return validation_results
    
    def save_pdf(self, output_path: str) -> bool:
        """
        Save modified PDF to specified path.
        
        Args:
            output_path: Path where to save the modified PDF
            
        Returns:
            True if saved successfully, False otherwise
        """
        if not self.wrapper:
            self.logger.error("No PDF loaded or modified to save")
            return False
        
        try:
            output_path = Path(output_path)
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the modified PDF
            with open(output_path, 'wb') as output_file:
                output_file.write(self.wrapper.read())
            
            self.logger.info(f"Successfully saved PDF to: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save PDF to {output_path}: {e}")
            return False
    
    def get_rename_preview(self, mappings: Dict[str, str]) -> Dict[str, Any]:
        """
        Get a preview of field renaming without making changes.
        
        Args:
            mappings: Dictionary of proposed field name mappings
            
        Returns:
            Dictionary with preview information and validation results
        """
        validation_results = self.validate_mappings(mappings)
        
        preview = {
            'total_fields': len(mappings),
            'validation_results': validation_results,
            'estimated_success_rate': 'To be determined',  # Will be validated during testing
            'preview_mappings': [
                {
                    'old_name': old,
                    'new_name': new,
                    'status': 'ready' if not validation_results['errors'] else 'blocked'
                }
                for old, new in mappings.items()
            ]
        }
        
        return preview
    
    @staticmethod
    def get_success_rate(results: List[FieldRenameResult]) -> float:
        """
        Calculate success rate from rename results.
        
        Args:
            results: List of FieldRenameResult objects
            
        Returns:
            Success rate as percentage (0.0 to 100.0)
        """
        if not results:
            return 0.0
        
        successful = sum(1 for r in results if r.success)
        return (successful / len(results)) * 100
    
    def get_field_summary(self, results: List[FieldRenameResult]) -> Dict[str, Any]:
        """
        Get a summary of field renaming results.
        
        Args:
            results: List of FieldRenameResult objects
            
        Returns:
            Dictionary with summary statistics
        """
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        
        return {
            'total_fields': total,
            'successful_renames': successful,
            'failed_renames': failed,
            'success_rate': self.get_success_rate(results),
            'errors': [r.error for r in results if r.error],
            'pdf_path': str(self.pdf_path)
        }
