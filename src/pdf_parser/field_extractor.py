"""PDF Field Extractor for extracting form fields with context and metadata."""

import PyPDF2
import pdfplumber
import json
import uuid
import csv
import io
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)


class PDFFieldExtractor:
    """Extract PDF form fields with comprehensive context and metadata."""
    
    def __init__(self):
        """Initialize the PDF Field Extractor."""
        self.field_data = []
    
    def extract_fields(self, pdf_path: str, context_radius: int = 50, output_format: str = "csv") -> Dict[str, Any]:
        """
        Main extraction method to extract fields from PDF with context.
        
        Args:
            pdf_path: Path to the PDF file to process
            context_radius: Pixel radius around field to extract text context
            output_format: Output format ('csv' or 'json')
            
        Returns:
            Dict with 'success', 'data', 'field_count', 'pages_processed' keys
        """
        try:
            logger.info(f"Starting field extraction for: {pdf_path}")
            
            # Validate input file exists and is readable
            pdf_file = Path(pdf_path)
            if not pdf_file.exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            if not pdf_file.is_file():
                raise ValueError(f"Path is not a file: {pdf_path}")
            if pdf_file.suffix.lower() != '.pdf':
                raise ValueError(f"File is not a PDF: {pdf_path}")
            if pdf_file.stat().st_size == 0:
                raise ValueError(f"PDF file is empty: {pdf_path}")
            if pdf_file.stat().st_size > 100 * 1024 * 1024:  # 100MB limit
                logger.warning(f"Large PDF file ({pdf_file.stat().st_size / 1024 / 1024:.1f}MB): {pdf_path}")
            
            # Test file readability
            try:
                with open(pdf_path, 'rb') as test_file:
                    test_file.read(8)  # Read PDF header
            except PermissionError:
                raise PermissionError(f"Permission denied reading PDF: {pdf_path}")
            except IOError as e:
                raise IOError(f"Cannot read PDF file: {pdf_path} - {str(e)}")
            
            # Step 1: Extract acrofields using PyPDF2
            logger.info("Extracting acrofields with PyPDF2...")
            acrofields = self._extract_acrofields(pdf_path)
            
            # Step 2: Extract text context using pdfplumber
            logger.info("Extracting text context with pdfplumber...")
            text_context = self._extract_text_context(pdf_path, acrofields, context_radius)
            
            # Step 3: Combine data and format output
            logger.info("Combining field and context data...")
            combined_data = self._combine_field_and_context_data(acrofields, text_context)
            
            # Step 4: Detect radio button groups and hierarchies
            logger.info("Processing field relationships...")
            processed_data = self._process_field_relationships(combined_data)
            
            # Step 5: Skip automatic RadioGroup generation - fields already have correct types
            logger.info("Skipping automatic RadioGroup generation - using PDF field types...")
            final_data = processed_data
            
            # Step 6: Enhance output structure to match CSV schema
            logger.info("Enhancing output structure for CSV compatibility...")
            enhanced_data = self._enhance_output_structure(final_data)
            
            # Step 7: Export to CSV if requested
            csv_export_success = False
            if output_format.lower() == 'csv':
                csv_path = pdf_path.replace('.pdf', '_extracted_fields.csv')
                logger.info(f"Exporting to CSV format: {csv_path}")
                csv_export_success = self.export_to_csv(enhanced_data, csv_path)
            
            return {
                'success': True,
                'data': enhanced_data,
                'field_count': len(enhanced_data),
                'pages_processed': self._get_page_count(pdf_path),
                'output_format': output_format,
                'csv_export_success': csv_export_success if output_format.lower() == 'csv' else None
            }
            
        except FileNotFoundError as e:
            logger.error(f"File not found: {str(e)}")
            return {
                'success': False,
                'error': f"File not found: {str(e)}",
                'error_type': 'FileNotFoundError',
                'data': []
            }
        except PermissionError as e:
            logger.error(f"Permission denied: {str(e)}")
            return {
                'success': False,
                'error': f"Permission denied: {str(e)}",
                'error_type': 'PermissionError',
                'data': []
            }
        except ValueError as e:
            logger.error(f"Invalid PDF or parameters: {str(e)}")
            return {
                'success': False,
                'error': f"Invalid PDF or parameters: {str(e)}",
                'error_type': 'ValueError',
                'data': []
            }
        except PyPDF2.errors.PdfReadError as e:
            logger.error(f"PDF read error: {str(e)}")
            return {
                'success': False,
                'error': f"PDF read error: {str(e)}",
                'error_type': 'PdfReadError',
                'data': []
            }
        except Exception as e:
            logger.error(f"Unexpected error extracting fields from {pdf_path}: {str(e)}")
            logger.error(f"Exception type: {type(e).__name__}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'error_type': type(e).__name__,
                'data': []
            }
    
    def _extract_acrofields(self, pdf_path: str) -> List[Dict]:
        """Extract all form fields using PyPDF2."""
        logger.info("Extracting acrofields using PyPDF2...")
        acrofields = []
        
        try:
            with open(pdf_path, 'rb') as file:
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                except PyPDF2.errors.PdfReadError as e:
                    raise ValueError(f"Invalid or corrupted PDF file: {pdf_path} - {str(e)}")
                except Exception as e:
                    raise RuntimeError(f"Failed to read PDF with PyPDF2: {pdf_path} - {str(e)}")
                
                # Validate PDF structure
                if len(pdf_reader.pages) == 0:
                    raise ValueError(f"PDF has no pages: {pdf_path}")
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    logger.warning(f"PDF is encrypted, attempting to decrypt: {pdf_path}")
                    try:
                        pdf_reader.decrypt('')  # Try empty password
                    except Exception as e:
                        raise ValueError(f"Cannot decrypt encrypted PDF: {pdf_path} - {str(e)}")
                
                # Check if PDF has form fields
                try:
                    form_fields = pdf_reader.get_fields()
                except Exception as e:
                    logger.warning(f"Error accessing form fields, PDF may not have AcroForm: {pdf_path} - {str(e)}")
                    return []
                
                if form_fields is None:
                    logger.warning(f"No AcroForm fields found in {pdf_path}")
                    return []
                
                logger.info(f"Found {len(form_fields)} form fields")
                
                # Process form fields with enhanced annotation processing
                for field_name, field_obj in form_fields.items():
                    try:
                        field_data = self._process_form_field(field_name, field_obj)
                        if field_data:
                            acrofields.append(field_data)
                            
                            # Check for RadioGroup children
                            if field_data.get('type') == 'RadioGroup':
                                child_fields = self._extract_radiogroup_children(field_name, field_obj)
                                acrofields.extend(child_fields)
                                
                    except Exception as e:
                        logger.error(f"Error processing field {field_name}: {str(e)}")
                        continue
                
                # Enhanced annotation processing for coordinates and field types
                logger.info("Processing page annotations for coordinate extraction...")
                annotation_data = self._extract_annotations_with_coordinates(pdf_reader, form_fields)
                
                # Merge annotation data with acrofields
                acrofields = self._merge_annotation_data(acrofields, annotation_data)
                
                logger.info(f"Successfully extracted {len(acrofields)} acrofields")
                return acrofields
                
        except Exception as e:
            logger.error(f"Error extracting acrofields: {str(e)}")
            raise
    
    def _process_form_field(self, field_name: str, field_obj: Any) -> Optional[Dict]:
        """Process a form field object and extract metadata."""
        try:
            field_data = {}
            
            field_data['name'] = field_name
            field_data['id'] = str(uuid.uuid4())
            
            # Check for RadioGroup pattern first
            if field_name.endswith('--group'):
                field_data['type'] = 'RadioGroup'
            else:
                # Determine field type from PDF field type
                field_data['type'] = 'TextField'  # Default
                if hasattr(field_obj, 'field_type'):
                    field_type = str(field_obj.field_type)
                    if '/Tx' in field_type:
                        field_data['type'] = 'TextField'
                    elif '/Btn' in field_type:
                        if field_name.endswith('--group'):
                            field_data['type'] = 'RadioGroup'
                        else:
                            # Check if it's actually a checkbox or radio button
                            field_data['type'] = self._determine_button_type(field_obj, field_name)
                    elif '/Sig' in field_type:
                        field_data['type'] = 'Signature'
            
            # Get field value
            field_data['value'] = ''
            if hasattr(field_obj, 'value') and field_obj.value:
                field_data['value'] = str(field_obj.value)
            
            # Default coordinates (will be improved later with annotation processing)
            field_data['page'] = 0
            field_data['x'] = 0
            field_data['y'] = 0
            field_data['width'] = 0
            field_data['height'] = 0
            field_data['flags'] = []
            
            return field_data
            
        except Exception as e:
            logger.error(f"Error processing form field {field_name}: {str(e)}")
            return None
    
    def _determine_button_type(self, field_obj: Any, field_name: str) -> str:
        """Determine if a /Btn field is a RadioButton or CheckBox."""
        try:
            # Get the field object dictionary to check flags
            field_dict = field_obj.get_object() if hasattr(field_obj, 'get_object') else field_obj
            
            if isinstance(field_dict, dict):
                # Check field flags (/Ff) to determine button type
                if '/Ff' in field_dict:
                    flags = int(field_dict['/Ff'])
                    
                    # Bit 15 (0x8000) = Radio button
                    # Bit 16 (0x10000) = Pushbutton  
                    # No special flags = Checkbox
                    if flags & (1 << 15):  # Radio button flag
                        return 'RadioButton'
                    elif flags & (1 << 16):  # Pushbutton flag
                        return 'Button'
                    else:
                        return 'CheckBox'  # Flags present but not radio/push = checkbox
                else:
                    # No flags = CheckBox (this is the key fix!)
                    return 'CheckBox'
            
        except Exception as e:
            logger.debug(f"Error determining button type for {field_name}: {e}")
        
        # Safe default
        return 'CheckBox'
    
    def _extract_radiogroup_children(self, group_name: str, group_obj: Any) -> List[Dict]:
        """Extract child RadioButton fields from a RadioGroup."""
        child_fields = []
        
        try:
            # Get the RadioGroup object dictionary
            group_dict = group_obj.get_object() if hasattr(group_obj, 'get_object') else group_obj
            
            if isinstance(group_dict, dict) and '/Kids' in group_dict:
                kids = group_dict['/Kids']
                
                for i, kid in enumerate(kids):
                    try:
                        child_obj = kid.get_object() if hasattr(kid, 'get_object') else kid
                        
                        if isinstance(child_obj, dict):
                            # Extract child field name
                            child_name = None
                            if '/T' in child_obj:
                                child_name = str(child_obj['/T'])
                            else:
                                # Generate name based on parent and index
                                child_name = f"{group_name}_option{i+1}"
                            
                            # Create child field data
                            child_field = {
                                'id': str(uuid.uuid4()),
                                'name': child_name,
                                'type': 'RadioButton',
                                'value': '',
                                'page': 0,
                                'x': 0,
                                'y': 0, 
                                'width': 0,
                                'height': 0,
                                'flags': [],
                                'parent_group': group_name
                            }
                            
                            # Extract coordinates if available
                            if '/Rect' in child_obj:
                                rect = child_obj['/Rect']
                                child_field['x'] = float(rect[0])
                                child_field['y'] = float(rect[1])
                                child_field['width'] = float(rect[2]) - float(rect[0])
                                child_field['height'] = float(rect[3]) - float(rect[1])
                            
                            # Extract value/export value
                            if '/AS' in child_obj:
                                child_field['value'] = str(child_obj['/AS'])
                            elif '/V' in child_obj:
                                child_field['value'] = str(child_obj['/V'])
                            
                            child_fields.append(child_field)
                            
                    except Exception as e:
                        logger.debug(f"Error processing child {i} of {group_name}: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error extracting children from RadioGroup {group_name}: {str(e)}")
        
        logger.info(f"Extracted {len(child_fields)} child RadioButtons from {group_name}")
        return child_fields
    
    def _extract_annotations_with_coordinates(self, pdf_reader, form_fields: Dict) -> Dict[str, Dict]:
        """Extract field annotations with coordinates from all pages."""
        annotation_data = {}
        
        try:
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                
                # Check if page has annotations
                if '/Annots' not in page:
                    continue
                
                annotations = page.get('/Annots')
                if not annotations:
                    continue
                
                # Handle IndirectObject
                if hasattr(annotations, 'get_object'):
                    annotations = annotations.get_object()
                
                # Convert to list if needed
                if not isinstance(annotations, list):
                    continue
                
                logger.debug(f"Processing {len(annotations)} annotations on page {page_num}")
                
                for annot_ref in annotations:
                    try:
                        annot = annot_ref.get_object()
                        
                        # Check if this is a form field annotation
                        if '/Subtype' not in annot or annot.get('/Subtype') != '/Widget':
                            continue
                        
                        # Extract field data with coordinates
                        field_info = self._process_field_annotation_enhanced(annot, page_num, form_fields)
                        if field_info and field_info.get('name'):
                            annotation_data[field_info['name']] = field_info
                            
                    except Exception as e:
                        logger.debug(f"Error processing annotation on page {page_num}: {str(e)}")
                        continue
            
            logger.info(f"Extracted annotation data for {len(annotation_data)} fields")
            return annotation_data
            
        except Exception as e:
            logger.error(f"Error extracting annotations: {str(e)}")
            return {}
    
    def _process_field_annotation_enhanced(self, annot: Dict, page_num: int, form_fields: Dict) -> Optional[Dict]:
        """Process a field annotation with enhanced coordinate and type detection."""
        try:
            field_info = {}
            
            # Get field name
            field_name = None
            if '/T' in annot:
                field_name = str(annot['/T'])
            elif '/Parent' in annot:
                try:
                    parent = annot['/Parent']
                    if hasattr(parent, 'get_object'):
                        parent_obj = parent.get_object()
                        if '/T' in parent_obj:
                            field_name = str(parent_obj['/T'])
                except:
                    pass
            
            if not field_name:
                return None
            
            field_info['name'] = field_name
            field_info['page'] = page_num
            
            # Extract coordinates
            if '/Rect' in annot:
                rect = annot['/Rect']
                field_info['x'] = float(rect[0])
                field_info['y'] = float(rect[1])
                field_info['width'] = float(rect[2]) - float(rect[0])
                field_info['height'] = float(rect[3]) - float(rect[1])
            else:
                field_info['x'] = 0
                field_info['y'] = 0
                field_info['width'] = 0
                field_info['height'] = 0
            
            # Enhanced field type detection
            field_info['type'] = self._determine_field_type_enhanced(annot, form_fields.get(field_name))
            
            # Get field value
            field_info['value'] = ''
            if '/V' in annot:
                field_info['value'] = str(annot['/V'])
            
            # Get field flags for additional type information
            field_info['flags'] = []
            if '/Ff' in annot:
                field_info['flags'] = self._parse_field_flags(annot['/Ff'])
            
            return field_info
            
        except Exception as e:
            logger.debug(f"Error processing enhanced annotation: {str(e)}")
            return None
    
    def _determine_field_type_enhanced(self, annot: Dict, form_field: Any) -> str:
        """Enhanced field type determination using annotation properties."""
        field_name = ''
        if '/T' in annot:
            field_name = str(annot['/T'])
        
        # Check for RadioGroup pattern first (fields ending with --group)
        if field_name.endswith('--group'):
            return 'RadioGroup'
        
        # Check form field type
        if form_field and hasattr(form_field, 'field_type'):
            field_type = str(form_field.field_type)
            if '/Tx' in field_type:
                return 'TextField'
            elif '/Btn' in field_type:
                # Check if it's a RadioGroup by name pattern
                if field_name.endswith('--group'):
                    return 'RadioGroup'
                # Check flags for button type
                if '/Ff' in annot:
                    flags = int(annot['/Ff'])
                    if flags & (1 << 15):  # Radio button flag
                        return 'RadioButton'
                    elif flags & (1 << 16):  # Pushbutton flag
                        return 'Button'
                    else:
                        return 'CheckBox'
                # Default buttons to RadioButton if no specific flags
                return 'RadioButton'
            elif '/Sig' in field_type:
                return 'Signature'
        
        # Fallback to annotation field type
        if '/FT' in annot:
            ft = str(annot['/FT'])
            if '/Tx' in ft:
                return 'TextField'
            elif '/Btn' in ft:
                # Check name pattern for RadioGroup
                if field_name.endswith('--group'):
                    return 'RadioGroup'
                # Check flags
                if '/Ff' in annot:
                    flags = int(annot['/Ff'])
                    if flags & (1 << 15):  # Radio button
                        return 'RadioButton'
                    elif flags & (1 << 16):  # Pushbutton
                        return 'Button'
                    else:
                        return 'CheckBox'
                return 'RadioButton'  # Default buttons to RadioButton
            elif '/Sig' in ft:
                return 'Signature'
        
        return 'TextField'  # Default fallback
    
    def _merge_annotation_data(self, acrofields: List[Dict], annotation_data: Dict[str, Dict]) -> List[Dict]:
        """Merge annotation coordinate and type data with acrofield data."""
        enhanced_fields = []
        
        for field in acrofields:
            field_name = field.get('name', '')
            enhanced_field = field.copy()
            
            # Merge annotation data if available
            if field_name in annotation_data:
                annot_data = annotation_data[field_name]
                
                # Update coordinates
                enhanced_field['x'] = annot_data.get('x', field.get('x', 0))
                enhanced_field['y'] = annot_data.get('y', field.get('y', 0))
                enhanced_field['width'] = annot_data.get('width', field.get('width', 0))
                enhanced_field['height'] = annot_data.get('height', field.get('height', 0))
                enhanced_field['page'] = annot_data.get('page', field.get('page', 0))
                
                # Update field type with enhanced detection, but preserve RadioGroups and CheckBoxes
                original_type = field.get('type', 'TextField')
                if original_type in ['RadioGroup', 'CheckBox']:
                    # Don't override RadioGroup or CheckBox types
                    enhanced_field['type'] = original_type
                else:
                    enhanced_field['type'] = annot_data.get('type', original_type)
                
                # Update flags
                enhanced_field['flags'] = annot_data.get('flags', field.get('flags', []))
                
                # Mark as having coordinate data
                enhanced_field['has_coordinates'] = True
            else:
                enhanced_field['has_coordinates'] = False
            
            enhanced_fields.append(enhanced_field)
        
        logger.info(f"Enhanced {len(enhanced_fields)} fields with annotation data")
        return enhanced_fields
    
    def _process_field_annotation(self, annot: Dict, page_num: int, form_fields: Dict) -> Optional[Dict]:
        """Process a single field annotation and extract metadata."""
        try:
            field_data = {}
            
            # Get field name
            field_name = None
            if '/T' in annot:
                field_name = annot['/T']
            elif '/Parent' in annot and '/T' in annot['/Parent']:
                field_name = annot['/Parent']['/T']
            
            if not field_name:
                return None
            
            field_data['name'] = str(field_name)
            field_data['page'] = page_num
            
            # Get field type
            field_data['type'] = self._determine_field_type(annot, form_fields.get(field_name))
            
            # Get field rectangle (coordinates)
            if '/Rect' in annot:
                rect = annot['/Rect']
                field_data['x'] = float(rect[0])
                field_data['y'] = float(rect[1])
                field_data['width'] = float(rect[2]) - float(rect[0])
                field_data['height'] = float(rect[3]) - float(rect[1])
            else:
                # Default values if no rectangle found
                field_data['x'] = 0
                field_data['y'] = 0
                field_data['width'] = 0
                field_data['height'] = 0
            
            # Get field value if available
            field_data['value'] = ''
            if '/V' in annot:
                field_data['value'] = str(annot['/V'])
            
            # Get field flags
            field_data['flags'] = []
            if '/Ff' in annot:
                field_data['flags'] = self._parse_field_flags(annot['/Ff'])
            
            # Generate unique ID
            field_data['id'] = str(uuid.uuid4())
            
            return field_data
            
        except Exception as e:
            logger.error(f"Error processing field annotation: {str(e)}")
            return None
    
    def _determine_field_type(self, annot: Dict, form_field: Any) -> str:
        """Determine the type of form field."""
        # Check form field type first
        if form_field and hasattr(form_field, 'field_type'):
            field_type = str(form_field.field_type)
            if 'Text' in field_type:
                return 'TextField'
            elif 'Check' in field_type:
                return 'CheckBox'
            elif 'Radio' in field_type:
                return 'RadioButton'
            elif 'Choice' in field_type:
                return 'ChoiceField'
            elif 'Signature' in field_type:
                return 'Signature'
        
        # Fallback to annotation subtype
        if '/FT' in annot:
            ft = str(annot['/FT'])
            if '/Tx' in ft:
                return 'TextField'
            elif '/Btn' in ft:
                # Check if it's a checkbox or radio button
                if '/Ff' in annot:
                    flags = int(annot['/Ff'])
                    if flags & (1 << 15):  # Radio button flag
                        return 'RadioButton'
                    else:
                        return 'CheckBox'
                return 'CheckBox'
            elif '/Ch' in ft:
                return 'ChoiceField'
            elif '/Sig' in ft:
                return 'Signature'
        
        return 'TextField'  # Default to text field
    
    def _parse_field_flags(self, flags: int) -> List[str]:
        """Parse field flags into readable format."""
        flag_meanings = {
            1: 'ReadOnly',
            2: 'Required',
            3: 'NoExport',
            13: 'Multiline',
            14: 'Password',
            15: 'Radio',
            16: 'Pushbutton',
            17: 'Combo',
            18: 'Edit',
            19: 'Sort',
            21: 'FileSelect',
            23: 'MultiSelect',
            24: 'DoNotSpellCheck',
            25: 'DoNotScroll',
            26: 'Comb',
            27: 'RadiosInUnison'
        }
        
        result = []
        for bit, meaning in flag_meanings.items():
            if flags & (1 << (bit - 1)):
                result.append(meaning)
        return result
    
    def _extract_text_context(self, pdf_path: str, fields: List[Dict], radius: int) -> Dict:
        """Extract surrounding text for each field using pdfplumber."""
        logger.info(f"Extracting text context with radius {radius} pixels...")
        context_data = {}
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                logger.info(f"Opened PDF with {len(pdf.pages)} pages using pdfplumber")
                
                for field in fields:
                    field_name = field.get('name', '')
                    page_num = field.get('page', 0)
                    x = field.get('x', 0)
                    y = field.get('y', 0)
                    width = field.get('width', 0)
                    height = field.get('height', 0)
                    
                    # Initialize context for this field
                    context_data[field_name] = {
                        'surrounding_text': '',
                        'text_above': '',
                        'text_below': '',
                        'text_left': '',
                        'text_right': '',
                        'section_header': ''
                    }
                    
                    # Skip if coordinates are not available (will be fixed later)
                    if x == 0 and y == 0 and width == 0 and height == 0:
                        logger.debug(f"Skipping context extraction for {field_name} - no coordinates")
                        continue
                    
                    # Get the page
                    if page_num < len(pdf.pages):
                        page = pdf.pages[page_num]
                        
                        # Extract text context in different regions
                        context_data[field_name] = self._extract_field_context_regions(
                            page, x, y, width, height, radius
                        )
                
                logger.info(f"Extracted text context for {len(fields)} fields")
                return context_data
                
        except Exception as e:
            logger.error(f"Error extracting text context: {str(e)}")
            # Return empty context for all fields if extraction fails
            for field in fields:
                field_name = field.get('name', '')
                context_data[field_name] = {
                    'surrounding_text': '',
                    'text_above': '',
                    'text_below': '',
                    'text_left': '',
                    'text_right': '',
                    'section_header': ''
                }
            return context_data
    
    def _extract_field_context_regions(self, page, x: float, y: float, width: float, height: float, radius: int) -> Dict[str, str]:
        """Extract text in different regions around a field."""
        # Note: pdfplumber uses bottom-left origin, PDF coordinates may use top-left
        # We'll need to handle coordinate system conversion
        
        page_height = page.height
        
        # Convert coordinates if needed (PDF often uses top-left origin)
        # For now, assume coordinates are correct
        
        # Define regions around the field
        regions = {
            'surrounding_text': self._get_text_in_bbox(page, 
                x - radius, y - radius, x + width + radius, y + height + radius),
            'text_above': self._get_text_in_bbox(page,
                x - radius, y + height, x + width + radius, y + height + radius),
            'text_below': self._get_text_in_bbox(page,
                x - radius, y - radius, x + width + radius, y),
            'text_left': self._get_text_in_bbox(page,
                x - radius, y, x, y + height),
            'text_right': self._get_text_in_bbox(page,
                x + width, y, x + width + radius, y + height)
        }
        
        # Try to identify section header (look for text above the field)
        header_bbox = (x - radius*2, y + height, x + width + radius*2, y + height + radius*2)
        regions['section_header'] = self._get_text_in_bbox(page, *header_bbox)
        
        # Clean up text
        for key, text in regions.items():
            regions[key] = self._clean_extracted_text(text)
        
        return regions
    
    def _get_text_in_bbox(self, page, x0: float, y0: float, x1: float, y1: float) -> str:
        """Extract text within a bounding box."""
        try:
            # Ensure bbox coordinates are within page bounds
            x0 = max(0, x0)
            y0 = max(0, y0)
            x1 = min(page.width, x1)
            y1 = min(page.height, y1)
            
            # Skip if bbox is invalid
            if x0 >= x1 or y0 >= y1:
                return ""
            
            # Crop page to bbox and extract text
            cropped_page = page.crop((x0, y0, x1, y1))
            return cropped_page.extract_text() or ""
            
        except Exception as e:
            logger.debug(f"Error extracting text from bbox ({x0}, {y0}, {x1}, {y1}): {str(e)}")
            return ""
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        
        # Remove common PDF artifacts
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # Limit length for practical use
        if len(text) > 200:
            text = text[:200] + "..."
        
        return text.strip()
    
    def _infer_bem_category(self, field_name: str, field_data: Dict) -> str:
        """Infer BEM category from field name and context."""
        field_name_lower = field_name.lower()
        
        # Don't change RadioGroups - they have their own category
        if field_data.get('type') == 'RadioGroup':
            return 'general-information'
        
        # Check if field already has BEM naming
        if '_' in field_name and any(block in field_name_lower for block in ['personal-information', 'contingent-benficiary', 'sign-here']):
            parts = field_name.split('_')
            if len(parts) >= 2:
                return parts[0]  # Return the Block part
        
        # Infer category from field name patterns
        if any(term in field_name_lower for term in ['name', 'first', 'last', 'middle', 'mi']):
            return 'personal-information'
        elif any(term in field_name_lower for term in ['ssn', 'social', 'security']):
            return 'personal-information'
        elif any(term in field_name_lower for term in ['address', 'street', 'city', 'state', 'zip', 'postal']):
            return 'personal-information'
        elif any(term in field_name_lower for term in ['phone', 'email', 'contact']):
            return 'personal-information'
        elif any(term in field_name_lower for term in ['signature', 'sign', 'date']):
            return 'sign-here'
        elif any(term in field_name_lower for term in ['beneficiary', 'contingent', 'primary']):
            return 'contingent-benficiary'
        elif any(term in field_name_lower for term in ['employer', 'company', 'organization']):
            return 'employer-information'
        elif any(term in field_name_lower for term in ['tax', 'withholding', 'allowance']):
            return 'tax-information'
        else:
            return 'general-information'
    
    def _combine_field_and_context_data(self, acrofields: List[Dict], text_context: Dict) -> List[Dict]:
        """Combine field metadata with text context."""
        logger.info(f"Combining {len(acrofields)} acrofields with context data...")
        
        combined_data = []
        
        for field in acrofields:
            field_name = field.get('name', '')
            
            # Create a copy of the field data
            combined_field = field.copy()
            
            # Debug: check if RadioGroup type is preserved in copy
            if field.get('type') == 'RadioGroup':
                logger.debug(f"Processing RadioGroup: {field_name}, type after copy: {combined_field.get('type')}")
            
            # Add context data if available
            if field_name in text_context:
                context = text_context[field_name]
                combined_field.update({
                    'surrounding_text': context.get('surrounding_text', ''),
                    'text_above': context.get('text_above', ''),
                    'text_below': context.get('text_below', ''),
                    'text_left': context.get('text_left', ''),
                    'text_right': context.get('text_right', ''),
                    'section_header': context.get('section_header', ''),
                    'has_context': True
                })
            else:
                # Add empty context fields if no context was extracted
                combined_field.update({
                    'surrounding_text': '',
                    'text_above': '',
                    'text_below': '',
                    'text_left': '',
                    'text_right': '',
                    'section_header': '',
                    'has_context': False
                })
            
            # Add additional metadata
            combined_field['extraction_timestamp'] = str(uuid.uuid4())[:8]  # Short identifier
            
            # Debug: check field type before and after bem category inference
            original_type = combined_field.get('type', 'Unknown')
            combined_field['bem_category'] = self._infer_bem_category(field_name, combined_field)
            new_type = combined_field.get('type', 'Unknown')
            
            if original_type != new_type:
                logger.debug(f"Field type changed for {field_name}: {original_type} -> {new_type}")
            
            combined_data.append(combined_field)
        
        logger.info(f"Successfully combined {len(combined_data)} fields with context data")
        return combined_data
    
    def _process_field_relationships(self, field_data: List[Dict]) -> List[Dict]:
        """Detect and process radio button groups and field hierarchies."""
        logger.info("Processing field relationships and radio button groups...")
        
        # Group fields by BEM category for hierarchy detection
        categories = {}
        for field in field_data:
            category = field.get('bem_category', 'general-information')
            if category not in categories:
                categories[category] = []
            categories[category].append(field)
        
        # Detect radio button groups
        radio_groups = self._detect_radio_button_groups(field_data)
        
        # Process each field with relationship data
        processed_fields = []
        for field in field_data:
            processed_field = field.copy()
            
            # Add category information
            processed_field['category_fields_count'] = len(categories.get(field.get('bem_category', 'general-information'), []))
            
            # Add radio group information
            radio_group = self._find_field_radio_group(field, radio_groups)
            if radio_group:
                processed_field['radio_group'] = radio_group['group_name']
                processed_field['radio_group_size'] = len(radio_group['fields'])
                processed_field['is_radio_group_member'] = True
            else:
                processed_field['radio_group'] = None
                processed_field['radio_group_size'] = 0
                processed_field['is_radio_group_member'] = False
            
            # Add field relationships
            processed_field['related_fields'] = self._find_related_fields(field, field_data)
            processed_field['field_hierarchy_level'] = self._determine_hierarchy_level(field)
            
            # Add field ordering within category
            category_fields = categories.get(field.get('bem_category', 'general-information'), [])
            processed_field['category_order'] = self._get_field_order_in_category(field, category_fields)
            
            processed_fields.append(processed_field)
        
        logger.info(f"Processed {len(processed_fields)} fields with relationship data")
        logger.info(f"Found {len(radio_groups)} radio button groups")
        logger.info(f"Identified {len(categories)} field categories")
        
        return processed_fields
    
    def _detect_radio_button_groups(self, field_data: List[Dict]) -> List[Dict]:
        """Detect radio button groups based on field names and types."""
        radio_groups = []
        processed_fields = set()
        
        for field in field_data:
            if field['id'] in processed_fields:
                continue
                
            field_name = field.get('name', '')
            
            # Look for radio button patterns
            if field.get('type') == 'RadioButton' or self._is_radio_button_field(field_name):
                # Find all fields with similar names (radio group)
                group_fields = []
                base_name = self._get_radio_button_base_name(field_name)
                
                for other_field in field_data:
                    other_name = other_field.get('name', '')
                    if (self._get_radio_button_base_name(other_name) == base_name and 
                        other_field['id'] not in processed_fields):
                        group_fields.append(other_field)
                        processed_fields.add(other_field['id'])
                
                if len(group_fields) > 1:
                    radio_groups.append({
                        'group_name': f"{base_name}--group",
                        'base_name': base_name,
                        'fields': group_fields,
                        'field_count': len(group_fields)
                    })
        
        return radio_groups
    
    def _is_radio_button_field(self, field_name: str) -> bool:
        """Check if field name suggests it's part of a radio button group."""
        field_name_lower = field_name.lower()
        radio_indicators = [
            'radio', 'option', 'choice', 'select',
            'yes', 'no', 'male', 'female', 'single', 'married'
        ]
        return any(indicator in field_name_lower for indicator in radio_indicators)
    
    def _get_radio_button_base_name(self, field_name: str) -> str:
        """Extract base name for radio button grouping."""
        # Remove common radio button suffixes
        suffixes_to_remove = ['_yes', '_no', '_1', '_2', '_3', '_option1', '_option2', '_male', '_female']
        
        base_name = field_name
        for suffix in suffixes_to_remove:
            if base_name.lower().endswith(suffix.lower()):
                base_name = base_name[:-len(suffix)]
                break
        
        return base_name
    
    def _find_field_radio_group(self, field: Dict, radio_groups: List[Dict]) -> Optional[Dict]:
        """Find the radio group that contains this field."""
        field_id = field['id']
        for group in radio_groups:
            for group_field in group['fields']:
                if group_field['id'] == field_id:
                    return group
        return None
    
    def _find_related_fields(self, field: Dict, all_fields: List[Dict]) -> List[str]:
        """Find fields related to this field by category or naming pattern."""
        related = []
        field_category = field.get('bem_category', '')
        field_name = field.get('name', '')
        
        for other_field in all_fields:
            if other_field['id'] == field['id']:
                continue
                
            # Related by same category
            if other_field.get('bem_category') == field_category:
                related.append(other_field.get('name', ''))
        
        return related[:5]  # Limit to 5 most related fields
    
    def _determine_hierarchy_level(self, field: Dict) -> int:
        """Determine the hierarchy level of a field (0=top, 1=section, 2=subsection, etc.)."""
        field_name = field.get('name', '')
        
        # Count underscores and dashes to infer hierarchy
        underscore_count = field_name.count('_')
        dash_count = field_name.count('-')
        
        # Basic heuristic: more separators = deeper level
        if underscore_count == 0 and dash_count <= 2:
            return 0  # Top level
        elif underscore_count == 1:
            return 1  # Section level
        elif underscore_count == 2:
            return 2  # Subsection level
        else:
            return 3  # Deep subsection
    
    def _get_field_order_in_category(self, field: Dict, category_fields: List[Dict]) -> int:
        """Get the order/position of this field within its category."""
        field_name = field.get('name', '')
        
        # Sort category fields by name for consistent ordering
        sorted_fields = sorted(category_fields, key=lambda x: x.get('name', ''))
        
        for i, cat_field in enumerate(sorted_fields):
            if cat_field['id'] == field['id']:
                return i + 1  # 1-based ordering
        
        return 0  # Default if not found
    
    def _generate_radio_group_containers(self, field_data: List[Dict]) -> List[Dict]:
        """Generate RadioGroup containers and establish parent-child relationships."""
        logger.info("Generating RadioGroup containers...")
        
        enhanced_fields = []
        radio_groups = {}
        
        # First pass: identify potential radio button groups
        for field in field_data:
            field_name = field.get('name', '')
            field_type = field.get('type', '')
            
            # Look for radio button patterns or checkboxes that should be radio groups
            if (field_type in ['CheckBox', 'RadioButton'] or 
                self._is_radio_button_field_by_pattern(field_name)):
                
                # Extract base group name
                group_name = self._extract_radio_group_base_name(field_name)
                
                if group_name not in radio_groups:
                    radio_groups[group_name] = {
                        'group_name': f"{group_name}--group",
                        'fields': [],
                        'base_name': group_name
                    }
                
                # Update field type to RadioButton if it was CheckBox
                if field_type == 'CheckBox':
                    field['type'] = 'RadioButton'
                
                radio_groups[group_name]['fields'].append(field)
            
            enhanced_fields.append(field)
        
        # Second pass: create RadioGroup containers and update parent relationships
        final_fields = []
        created_groups = set()
        
        for field in enhanced_fields:
            field_name = field.get('name', '')
            field_type = field.get('type', '')
            
            # Check if this field belongs to a radio group
            group_base = None
            for base_name, group_info in radio_groups.items():
                if any(f['name'] == field_name for f in group_info['fields']):
                    group_base = base_name
                    break
            
            if group_base and group_base not in created_groups:
                # Create RadioGroup container
                group_info = radio_groups[group_base]
                if len(group_info['fields']) > 1:  # Only create if multiple radio buttons
                    radio_group = self._create_radio_group_container(group_info)
                    final_fields.append(radio_group)
                    created_groups.add(group_base)
                    
                    # Update parent IDs for radio buttons in this group
                    for radio_field in group_info['fields']:
                        radio_field['parent_id'] = radio_group['id']
                        radio_field['radio_group'] = radio_group['name']
                        radio_field['is_radio_group_member'] = True
            
            final_fields.append(field)
        
        logger.info(f"Generated {len(created_groups)} RadioGroup containers")
        logger.info(f"Total fields (including containers): {len(final_fields)}")
        
        return final_fields
    
    def _is_radio_button_field_by_pattern(self, field_name: str) -> bool:
        """Check if field name pattern suggests it's part of a radio button group."""
        # SIMPLIFIED: Let the PDF field type detection do most of the work
        # Only exclude obvious text field patterns
        field_name_lower = field_name.lower()
        
        # These are clearly NOT radio buttons (text input fields)
        text_field_indicators = [
            '__name', '__address', '__city', '__state', '__zip', '__phone', '__email',
            '__county', '__specify', '__first', '__last', '__contract', '__date',
            '_former', '_present', '_amount'
        ]
        
        for indicator in text_field_indicators:
            if indicator in field_name_lower:
                return False
        
        # Everything else could potentially be a radio button - let field type detection decide
        return True
    
    def _extract_radio_group_base_name(self, field_name: str) -> str:
        """Extract the base name for radio group from field name."""
        # Handle special patterns first
        field_name_lower = field_name.lower()
        
        # For name-change reason fields
        if 'name-change_reason__' in field_name_lower:
            return 'name-change_reason'
        
        # For payment method sub-choices
        if 'payment-method_direct-deposit__' in field_name_lower:
            return 'payment-method_direct-deposit'
            
        # Standard suffixes to remove for radio button choices
        suffixes_to_remove = [
            '_owner', '_insured', '_payor', '_other',
            '_marriage', '_divorce', '_correction', '_adoption', '_court',
            '_accumulate', '_reduce', '_purchase', '_principal', '_paid',
            '_direct', '_no', '_mail-check', '_custodial-account', '_company-organization-fbo'
        ]
        
        base_name = field_name
        for suffix in suffixes_to_remove:
            if base_name.lower().endswith(suffix.lower()):
                base_name = base_name[:-len(suffix)]
                break
        
        return base_name
    
    def _create_radio_group_container(self, group_info: Dict) -> Dict:
        """Create a RadioGroup container field."""
        import uuid
        
        group_name = group_info['group_name']
        base_name = group_info['base_name']
        
        # Create RadioGroup container
        radio_group = {
            'id': str(uuid.uuid4()),
            'name': group_name,
            'type': 'RadioGroup',
            'bem_category': self._infer_bem_category(base_name, {}),
            'value': '',
            'page': 0,  # Will be updated based on children
            'x': 0,
            'y': 0,
            'width': 0,
            'height': 0,
            'flags': [],
            'has_coordinates': False,
            'has_context': False,
            'surrounding_text': '',
            'text_above': '',
            'text_below': '',
            'text_left': '',
            'text_right': '',
            'section_header': '',
            'extraction_timestamp': str(uuid.uuid4())[:8],
            'parent_id': None,
            'child_fields': [f['name'] for f in group_info['fields']],
            'child_count': len(group_info['fields']),
            'radio_group': None,
            'radio_group_size': 0,
            'is_radio_group_member': False,
            'related_fields': [],
            'field_hierarchy_level': 0,
            'category_fields_count': 1,
            'category_order': 1
        }
        
        # Update page and coordinates based on first child field
        if group_info['fields']:
            first_field = group_info['fields'][0]
            radio_group['page'] = first_field.get('page', 0)
            radio_group['bem_category'] = first_field.get('bem_category', 'general-information')
        
        return radio_group
    
    def _enhance_output_structure(self, field_data: List[Dict]) -> List[Dict]:
        """Enhance output structure to match training data CSV schema."""
        logger.info("Enhancing output structure for CSV compatibility...")
        
        enhanced_fields = []
        
        for field in field_data:
            enhanced_field = self._create_csv_compatible_field(field)
            enhanced_fields.append(enhanced_field)
        
        # Sort fields to match training data ordering (RadioGroups first, then their children)
        sorted_fields = self._sort_fields_for_csv(enhanced_fields)
        
        logger.info(f"Enhanced {len(sorted_fields)} fields for CSV output")
        return sorted_fields
    
    def _create_csv_compatible_field(self, field: Dict) -> Dict:
        """Create a field structure compatible with the training data CSV schema."""
        import datetime
        
        # Generate consistent IDs (in real implementation, these would be from database)
        field_id = hash(field.get('name', '')) % 9999999  # Simple hash for consistent IDs
        
        # Map our field structure to CSV schema
        csv_field = {
            # Required CSV columns
            'ID': field_id,
            'Created at': datetime.datetime.now().isoformat() + 'Z',
            'Updated at': datetime.datetime.now().isoformat() + 'Z',
            'Label': self._generate_field_label(field),
            'Description': '',
            'Form ID': 52471,  # Static form ID from training data
            'Order': field.get('category_order', 1),
            'Api name': field.get('name', ''),
            'UUID': field.get('id', ''),
            'Type': field.get('type', 'TextField'),
            'Parent ID': field.get('parent_id', ''),
            'Delete Parent ID': 'Delete Parent ID',  # Static from training data
            'Acrofieldlabel': field.get('name', ''),
            'Section ID': self._determine_section_id(field),
            'Excluded': 'false',
            'Partial label': field.get('name', ''),
            'Custom': 'false',
            'Show group label': 'true' if field.get('type') == 'RadioGroup' else 'false',
            'Height': field.get('height', ''),
            'Page': field.get('page', ''),
            'Width': field.get('width', ''),
            'X': field.get('x', ''),
            'Y': field.get('y', ''),
            'Unified field ID': field.get('category_order', ''),
            'Delete': 'Delete',
            'Hidden': 'false',
            'Toggle description': 'false',
            
            # Additional metadata for processing
            '_field_type': field.get('type', 'TextField'),
            '_bem_category': field.get('bem_category', 'general-information'),
            '_is_radio_member': field.get('is_radio_group_member', False),
            '_child_fields': field.get('child_fields', []),
            '_context_data': {
                'surrounding_text': field.get('surrounding_text', ''),
                'text_above': field.get('text_above', ''),
                'text_below': field.get('text_below', ''),
                'section_header': field.get('section_header', '')
            }
        }
        
        return csv_field
    
    def _generate_field_label(self, field: Dict) -> str:
        """Generate a human-readable label for the field."""
        field_name = field.get('name', '')
        field_type = field.get('type', '')
        
        # Special cases for known field types
        if field_type == 'RadioGroup':
            if 'address-change' in field_name:
                return 'Address Change Options'
            elif 'name-change' in field_name and 'reason' in field_name:
                return 'Reason for Change'
            elif 'name-change' in field_name:
                return 'Change the name of'
            elif 'dividend' in field_name:
                return 'Future Dividend Application'
            elif 'payment-method' in field_name:
                return 'Payment Method'
            elif 'stop' in field_name:
                return 'Stopping Payment Options'
            else:
                return field_name.replace('--group', '').replace('_', ' ').replace('-', ' ').title()
        
        # Generate labels for regular fields
        name_parts = field_name.replace('_', ' ').replace('-', ' ').split()
        
        # Common field name mappings
        label_mappings = {
            'first': 'First Name',
            'last': 'Last Name', 
            'name': 'Name',
            'address': 'Address',
            'city': 'City',
            'state': 'State',
            'zip': 'ZIP',
            'phone': 'Phone',
            'email': 'Email',
            'ssn': 'SSN',
            'contract': 'Contract Number',
            'signature': 'Signature',
            'date': 'Date',
            'owner': 'Policy Owner',
            'insured': 'Primary / Joint / Additional Insured',
            'payor': 'Premium Payor'
        }
        
        # Try to map the last meaningful part
        for part in reversed(name_parts):
            if part in label_mappings:
                return label_mappings[part]
        
        # Default to title case
        return ' '.join(name_parts).title()
    
    def _determine_section_id(self, field: Dict) -> int:
        """Determine the section ID based on field category."""
        bem_category = field.get('bem_category', 'general-information')
        
        # Section ID mappings based on training data patterns
        section_mappings = {
            'personal-information': 8261,
            'general-information': 8261,
            'sign-here': 8265,
            'tax-information': 7099,
            'employer-information': 7095,
            'contingent-benficiary': 8262
        }
        
        return section_mappings.get(bem_category, 8261)  # Default section
    
    def _sort_fields_for_csv(self, fields: List[Dict]) -> List[Dict]:
        """Sort fields to match training data ordering."""
        # Sort by: RadioGroups first, then by section, then by order
        def sort_key(field):
            field_type = field.get('_field_type', 'TextField')
            section_id = field.get('Section ID', 8261)
            order = field.get('Order', 999)
            
            # RadioGroups come first in their section
            type_priority = 0 if field_type == 'RadioGroup' else 1
            
            return (section_id, type_priority, order)
        
        return sorted(fields, key=sort_key)
    
    def _get_page_count(self, pdf_path: str) -> int:
        """Get the number of pages in the PDF."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)
        except Exception as e:
            logger.error(f"Error getting page count: {str(e)}")
            return 0
    
    def export_to_csv(self, field_data: List[Dict], output_path: str, form_id: str = "52471") -> bool:
        """Export field data to CSV format matching training data schema exactly.
        
        Args:
            field_data: List of field dictionaries from extract_fields
            output_path: Path to save the CSV file
            form_id: Form ID to use in the CSV (default matches training data)
            
        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            logger.info(f"Exporting {len(field_data)} fields to CSV: {output_path}")
            
            # CSV schema from training data
            csv_headers = [
                'ID', 'Created at', 'Updated at', 'Label', 'Description', 'Form ID', 'Order', 
                'Api name', 'UUID', 'Type', 'Parent ID', 'Delete Parent ID', 'Acrofieldlabel', 
                'Section ID', 'Excluded', 'Partial label', 'Custom', 'Show group label', 
                'Height', 'Page', 'Width', 'X', 'Y', 'Unified field ID', 'Delete', 'Hidden', 
                'Toggle description'
            ]
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write BOM for Excel compatibility (like training data)
                csvfile.write('\ufeff')
                csvfile.seek(0, 2)  # Move to end after BOM
                
                # Write header
                writer.writerow(csv_headers)
                
                # Convert field data to CSV rows
                csv_rows = self._convert_fields_to_csv_rows(field_data, form_id)
                
                # Write data rows
                for row in csv_rows:
                    writer.writerow(row)
            
            logger.info(f"Successfully exported {len(csv_rows)} rows to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            return False
    
    def _convert_fields_to_csv_rows(self, field_data: List[Dict], form_id: str) -> List[List]:
        """Convert field data to CSV rows matching training data schema."""
        csv_rows = []
        current_time = datetime.now().isoformat() + 'Z'
        section_id_map = self._generate_section_ids(field_data)
        
        # Sort fields for consistent ordering
        sorted_fields = sorted(field_data, key=lambda x: (
            x.get('bem_category', 'zzz'),  # Sort by category
            x.get('type', 'zzz'),          # Then by type  
            x.get('name', 'zzz')           # Then by name
        ))
        
        for order, field in enumerate(sorted_fields, 1):
            # Generate unique ID (simulate database auto-increment)
            field_id = 6727000 + order
            
            # Map field to CSV row format
            csv_row = [
                field_id,                                          # ID
                current_time,                                      # Created at
                current_time,                                      # Updated at
                self._generate_field_label(field),                # Label
                field.get('description', ''),                     # Description
                form_id,                                          # Form ID
                order,                                            # Order
                field.get('name', ''),                           # Api name
                field.get('id', str(uuid.uuid4())),             # UUID
                field.get('type', 'TextField'),                  # Type
                self._get_parent_id(field, sorted_fields),       # Parent ID
                'Delete Parent ID',                              # Delete Parent ID (constant)
                field.get('name', ''),                           # Acrofieldlabel
                section_id_map.get(field.get('bem_category', 'general-information'), 8261), # Section ID
                'false',                                         # Excluded
                field.get('name', ''),                          # Partial label
                'false',                                         # Custom
                'true' if field.get('type') == 'RadioGroup' else 'false', # Show group label
                field.get('height', ''),                         # Height
                field.get('page', ''),                          # Page
                field.get('width', ''),                         # Width
                field.get('x', ''),                             # X
                field.get('y', ''),                             # Y
                900 + order,                                     # Unified field ID
                'Delete',                                        # Delete (constant)
                'false',                                         # Hidden
                'false'                                          # Toggle description
            ]
            
            csv_rows.append(csv_row)
        
        return csv_rows
    
    def _generate_field_label(self, field: Dict) -> str:
        """Generate human-readable label from field name."""
        field_name = field.get('name', '')
        field_type = field.get('type', 'TextField')
        
        # For RadioGroups, create descriptive labels
        if field_type == 'RadioGroup':
            if 'address-change' in field_name:
                return 'Address Change Options'
            elif 'name-change' in field_name and 'reason' in field_name:
                return 'Reason for Change'
            elif 'name-change' in field_name:
                return 'Change the name of'
            elif 'dividend' in field_name:
                return 'Future Dividend Application'
            elif 'frequency' in field_name:
                return 'Frequency'
            elif 'stop' in field_name:
                return 'Stopping Payment Options'
            else:
                return field_name.replace('--group', '').replace('_', ' ').title()
        
        # For other fields, generate from BEM name
        if '_' in field_name:
            parts = field_name.split('_')
            if len(parts) >= 2:
                element = parts[-1]  # Last part is usually the element
                return element.replace('-', ' ').title()
        
        # Fallback
        return field_name.replace('_', ' ').replace('-', ' ').title()
    
    def _get_parent_id(self, field: Dict, all_fields: List[Dict]) -> str:
        """Get parent ID for RadioButton fields."""
        if field.get('type') == 'RadioButton':
            parent_group = field.get('parent_group', '')
            if parent_group:
                # Find the RadioGroup with matching name
                for i, other_field in enumerate(all_fields):
                    if (other_field.get('type') == 'RadioGroup' and 
                        other_field.get('name') == parent_group):
                        return str(6727000 + i + 1)  # Match ID generation logic
        
        return ''  # No parent
    
    def _generate_section_ids(self, field_data: List[Dict]) -> Dict[str, int]:
        """Generate section IDs for different BEM categories."""
        categories = set(field.get('bem_category', 'general-information') for field in field_data)
        
        section_id_map = {}
        base_section_id = 8261
        
        for i, category in enumerate(sorted(categories)):
            section_id_map[category] = base_section_id + i
        
        return section_id_map


# Test the basic class structure
if __name__ == "__main__":
    # Basic test to ensure imports work
    extractor = PDFFieldExtractor()
    print("✅ PDFFieldExtractor class created successfully")
    print("✅ All imports working correctly")