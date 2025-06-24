"""PDF Field Extractor for extracting form fields with context and metadata."""

import PyPDF2
import pdfplumber
import json
import uuid
from typing import Dict, List, Any, Optional
from pathlib import Path
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
            
            # Validate input file exists
            if not Path(pdf_path).exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
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
            
            return {
                'success': True,
                'data': processed_data,
                'field_count': len(processed_data),
                'pages_processed': self._get_page_count(pdf_path),
                'output_format': output_format
            }
            
        except Exception as e:
            logger.error(f"Error extracting fields from {pdf_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
    
    def _extract_acrofields(self, pdf_path: str) -> List[Dict]:
        """Extract all form fields using PyPDF2."""
        logger.info("Extracting acrofields using PyPDF2...")
        acrofields = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if PDF has form fields
                form_fields = pdf_reader.get_fields()
                if form_fields is None:
                    logger.warning(f"No form fields found in {pdf_path}")
                    return []
                
                logger.info(f"Found {len(form_fields)} form fields")
                
                # Process form fields directly (simpler approach)
                for field_name, field_obj in form_fields.items():
                    try:
                        field_data = self._process_form_field(field_name, field_obj)
                        if field_data:
                            acrofields.append(field_data)
                    except Exception as e:
                        logger.error(f"Error processing field {field_name}: {str(e)}")
                        continue
                
                # TODO: Add page-specific annotation processing later if needed
                # for page_num in range(len(pdf_reader.pages)):
                #     page = pdf_reader.pages[page_num]
                #     ...annotation processing...
                
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
            
            # Determine field type
            field_data['type'] = 'TextField'  # Default
            if hasattr(field_obj, 'field_type'):
                field_type = str(field_obj.field_type)
                if 'Text' in field_type:
                    field_data['type'] = 'TextField'
                elif 'Check' in field_type:
                    field_data['type'] = 'CheckBox'
                elif 'Radio' in field_type:
                    field_data['type'] = 'RadioButton'
                elif 'Choice' in field_type:
                    field_data['type'] = 'ChoiceField'
                elif 'Signature' in field_type:
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
    
    def _combine_field_and_context_data(self, acrofields: List[Dict], text_context: Dict) -> List[Dict]:
        """Combine field metadata with text context."""
        # For now, just return the acrofields data (will add context in Task 1.5)
        logger.info(f"Combining {len(acrofields)} acrofields with context data...")
        return acrofields
    
    def _process_field_relationships(self, field_data: List[Dict]) -> List[Dict]:
        """Detect and process radio button groups and field hierarchies."""
        # TODO: Implement in Task 1.6
        logger.info("_process_field_relationships method - placeholder")
        return field_data
    
    def _get_page_count(self, pdf_path: str) -> int:
        """Get the number of pages in the PDF."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)
        except Exception as e:
            logger.error(f"Error getting page count: {str(e)}")
            return 0


# Test the basic class structure
if __name__ == "__main__":
    # Basic test to ensure imports work
    extractor = PDFFieldExtractor()
    print("✅ PDFFieldExtractor class created successfully")
    print("✅ All imports working correctly")