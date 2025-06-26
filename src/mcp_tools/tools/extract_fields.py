"""
Extract Fields MCP Tool

Wraps the existing PDF field extraction functionality for Claude Desktop integration.
Handles PDF file processing and returns structured field data.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List

# Import existing field extractor
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from pdf_parser.field_extractor import PDFFieldExtractor

logger = logging.getLogger(__name__)

class ExtractFieldsTool:
    """MCP tool for extracting PDF form fields."""
    
    def __init__(self):
        """Initialize the extract fields tool."""
        self.extractor = PDFFieldExtractor()
    
    async def execute(
        self,
        pdf_path: str,
        context_radius: int = 50,
        output_format: str = "csv"
    ) -> Dict[str, Any]:
        """
        Extract form fields from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            context_radius: Pixel radius for text context extraction  
            output_format: Output format ('csv' or 'json')
            
        Returns:
            Dictionary containing extraction results and field data
        """
        try:
            logger.info(f"Extracting fields from: {pdf_path}")
            
            # Validate PDF file exists
            if not Path(pdf_path).exists():
                return {
                    "success": False,
                    "error": f"PDF file not found: {pdf_path}",
                    "error_type": "FileNotFoundError"
                }
            
            # Extract fields using existing functionality
            result = self.extractor.extract_fields(
                pdf_path=pdf_path,
                context_radius=context_radius,
                output_format=output_format
            )
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown extraction error"),
                    "error_type": result.get("error_type", "ExtractionError")
                }
            
            # Format data for MCP consumption
            formatted_result = {
                "success": True,
                "extraction_metadata": {
                    "pdf_path": pdf_path,
                    "field_count": result["field_count"],
                    "pages_processed": result["pages_processed"],
                    "output_format": output_format,
                    "context_radius": context_radius
                },
                "fields": result["data"],
                "extraction_summary": {
                    "total_fields": result["field_count"],
                    "field_types": self._analyze_field_types(result["data"]),
                    "has_radio_groups": any(
                        field.get("Type") == "RadioGroup" 
                        for field in result["data"]
                    ),
                    "has_coordinates": any(
                        field.get("X") and field.get("Y")
                        for field in result["data"] 
                    )
                }
            }
            
            logger.info(f"Successfully extracted {result['field_count']} fields")
            return formatted_result
            
        except Exception as e:
            logger.error(f"Error in extract_fields: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_type": type(e).__name__
            }
    
    def _analyze_field_types(self, fields: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze field types in the extracted data."""
        type_counts = {}
        for field in fields:
            field_type = field.get("Type", "Unknown")
            type_counts[field_type] = type_counts.get(field_type, 0) + 1
        return type_counts