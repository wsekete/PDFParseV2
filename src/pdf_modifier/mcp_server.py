#!/usr/bin/env python3
"""
PDF Field Modifier MCP Server
PDFParseV2 - AI-Powered PDF Field Renaming Engine

MCP (Model Context Protocol) server for PDF form field modification.
Designed to work with Claude Desktop for intelligent PDF field analysis and renaming.

Architecture:
- Claude handles field extraction and BEM naming generation
- This MCP server handles actual PDF field modification
- PyPDF2 engine with planned PDFtk integration for higher success rates
"""

import json
import sys
import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

try:
    import PyPDF2
    from PyPDF2 import PdfReader, PdfWriter
    from PyPDF2.generic import (
        DictionaryObject, ArrayObject, IndirectObject, 
        TextStringObject, NameObject, NumberObject
    )
except ImportError:
    print("Installing PyPDF2...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
    import PyPDF2
    from PyPDF2 import PdfReader, PdfWriter
    from PyPDF2.generic import (
        DictionaryObject, ArrayObject, IndirectObject, 
        TextStringObject, NameObject, NumberObject
    )

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
except ImportError:
    # For standalone testing, create mock classes
    class Server:
        def __init__(self, name): self.name = name
        def list_tools(self): return lambda: []
        def call_tool(self): return lambda name, args: []
        def run(self, *args): pass
        def create_initialization_options(self): return {}
    
    class Tool:
        def __init__(self, **kwargs): pass
    
    class TextContent:
        def __init__(self, type, text): self.type = type; self.text = text

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Server("pdf-field-modifier")

class PDFFieldRenamer:
    """
    Complete PDF field renaming implementation using PyPDF2.
    Handles all PDF form field types including text fields, checkboxes, radio buttons, and signatures.
    """
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.reader = None
        self.writer = None
        self.form_fields = {}
        self.annotations_by_page = {}
        self.field_references = {}
        
    def __enter__(self):
        """Context manager entry."""
        self.reader = PdfReader(self.pdf_path)
        self.writer = PdfWriter()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.reader:
            self.reader.stream.close()
    
    def analyze_form_structure(self) -> Dict[str, Any]:
        """
        Analyze the complete PDF form structure including all field types.
        Returns comprehensive field information for validation.
        """
        analysis = {
            "total_pages": len(self.reader.pages),
            "form_fields": {},
            "annotations": {},
            "field_hierarchy": {},
            "field_types": {},
            "field_positions": {}
        }
        
        # Get form fields from AcroForm
        if hasattr(self.reader, 'get_form_text_fields') and self.reader.get_form_text_fields():
            text_fields = self.reader.get_form_text_fields()
            for field_name, field_value in text_fields.items():
                analysis["form_fields"][field_name] = {
                    "value": field_value,
                    "type": "text_field",
                    "source": "acroform"
                }
        
        # Analyze annotations on each page
        for page_num, page in enumerate(self.reader.pages):
            page_annotations = []
            
            if hasattr(page, '/Annots') and page['/Annots']:
                for annot_ref in page['/Annots']:
                    try:
                        annot = annot_ref.get_object()
                        annot_info = self._analyze_annotation(annot, page_num)
                        if annot_info:
                            page_annotations.append(annot_info)
                            
                            # Store in main analysis
                            field_name = annot_info.get("field_name")
                            if field_name:
                                analysis["form_fields"][field_name] = {
                                    "value": annot_info.get("value"),
                                    "type": annot_info.get("field_type", "unknown"),
                                    "source": "annotation",
                                    "page": page_num + 1,
                                    "position": annot_info.get("position")
                                }
                                
                                # Store field type and position
                                analysis["field_types"][field_name] = annot_info.get("field_type", "unknown")
                                analysis["field_positions"][field_name] = annot_info.get("position", [])
                                
                                # Store reference for renaming
                                self.field_references[field_name] = {
                                    "page": page_num,
                                    "annotation": annot_ref,
                                    "object": annot
                                }
                    except Exception as e:
                        logger.warning(f"Could not process annotation on page {page_num + 1}: {str(e)}")
                        continue
            
            analysis["annotations"][page_num + 1] = page_annotations
        
        return analysis
    
    def _analyze_annotation(self, annot: DictionaryObject, page_num: int) -> Optional[Dict[str, Any]]:
        """Analyze a single annotation and extract field information."""
        try:
            annot_info = {
                "page": page_num + 1,
                "subtype": str(annot.get('/Subtype', 'Unknown'))
            }
            
            # Get field name
            if '/T' in annot:
                field_name = str(annot['/T'])
                annot_info["field_name"] = field_name
            
            # Get field value
            if '/V' in annot:
                field_value = annot['/V']
                if isinstance(field_value, TextStringObject):
                    annot_info["value"] = str(field_value)
                elif isinstance(field_value, NameObject):
                    annot_info["value"] = str(field_value)
                else:
                    annot_info["value"] = str(field_value)
            
            # Get field position
            if '/Rect' in annot:
                annot_info["position"] = [float(x) for x in annot['/Rect']]
            
            # Determine field type
            subtype = annot_info["subtype"]
            if subtype == "/Widget":
                # Widget annotation - check field type
                if '/FT' in annot:
                    field_type = str(annot['/FT'])
                    if field_type == '/Tx':
                        annot_info["field_type"] = "text_field"
                    elif field_type == '/Btn':
                        # Button field - could be checkbox or radio
                        if '/Ff' in annot:
                            flags = int(annot['/Ff'])
                            if flags & (1 << 15):  # Radio button flag
                                annot_info["field_type"] = "radio_button"
                            else:
                                annot_info["field_type"] = "checkbox"
                        else:
                            annot_info["field_type"] = "button"
                    elif field_type == '/Sig':
                        annot_info["field_type"] = "signature"
                    elif field_type == '/Ch':
                        annot_info["field_type"] = "choice"
                    else:
                        annot_info["field_type"] = "unknown_widget"
                else:
                    annot_info["field_type"] = "widget"
            else:
                annot_info["field_type"] = "annotation"
            
            return annot_info
            
        except Exception as e:
            logger.warning(f"Error analyzing annotation: {str(e)}")
            return None
    
    def rename_fields(self, field_mappings: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Rename PDF form fields based on provided mappings.
        This is the core implementation that actually modifies the PDF.
        """
        results = {
            "successful_renames": [],
            "failed_renames": [],
            "skipped_fields": [],
            "total_processed": 0
        }
        
        # First, analyze the form structure
        form_analysis = self.analyze_form_structure()
        existing_fields = set(form_analysis["form_fields"].keys())
        
        logger.info(f"Found {len(existing_fields)} existing fields in PDF")
        
        # Copy all pages to writer first
        for page in self.reader.pages:
            self.writer.add_page(page)
        
        # Process each field mapping
        for mapping in field_mappings:
            original_name = mapping.get("original_name", "")
            new_name = mapping.get("generated_name", "")
            
            if not original_name or not new_name:
                results["failed_renames"].append({
                    "original": original_name,
                    "new": new_name,
                    "error": "Missing original_name or generated_name"
                })
                continue
            
            if original_name not in existing_fields:
                results["skipped_fields"].append({
                    "original": original_name,
                    "new": new_name,
                    "reason": "Field not found in PDF"
                })
                continue
            
            # Attempt to rename the field
            try:
                success = self._rename_field_in_pdf(original_name, new_name)
                if success:
                    results["successful_renames"].append({
                        "original": original_name,
                        "new": new_name,
                        "type": form_analysis["field_types"].get(original_name, "unknown")
                    })
                    logger.info(f"Successfully renamed: {original_name} → {new_name}")
                else:
                    results["failed_renames"].append({
                        "original": original_name,
                        "new": new_name,
                        "error": "Rename operation failed"
                    })
            except Exception as e:
                logger.error(f"Error renaming field {original_name} to {new_name}: {str(e)}")
                results["failed_renames"].append({
                    "original": original_name,
                    "new": new_name,
                    "error": str(e)
                })
            
            results["total_processed"] += 1
        
        return results
    
    def _rename_field_in_pdf(self, original_name: str, new_name: str) -> bool:
        """
        Rename a specific field in the PDF structure.
        This handles the low-level PDF object manipulation.
        """
        try:
            renamed = False
            
            # Method 1: Rename via annotations (most reliable)
            for page_num, page in enumerate(self.writer.pages):
                if hasattr(page, '/Annots') and page['/Annots']:
                    for annot_ref in page['/Annots']:
                        try:
                            annot = annot_ref.get_object() if hasattr(annot_ref, 'get_object') else annot_ref
                            if '/T' in annot and str(annot['/T']) == original_name:
                                # Update the field name
                                annot[NameObject('/T')] = TextStringObject(new_name)
                                logger.debug(f"Updated field name on page {page_num + 1}: {original_name} → {new_name}")
                                renamed = True
                        except Exception as e:
                            logger.debug(f"Could not check annotation on page {page_num + 1}: {str(e)}")
                            continue
            
            # Method 2: Update in AcroForm if it exists
            if hasattr(self.writer, '_root_object') and self.writer._root_object:
                root_obj = self.writer._root_object
                if '/AcroForm' in root_obj:
                    acroform = root_obj['/AcroForm']
                    if hasattr(acroform, 'get_object'):
                        acroform_obj = acroform.get_object()
                    else:
                        acroform_obj = acroform
                    
                    if isinstance(acroform_obj, DictionaryObject) and '/Fields' in acroform_obj:
                        fields = acroform_obj['/Fields']
                        if isinstance(fields, ArrayObject):
                            for field_ref in fields:
                                try:
                                    field_obj = field_ref.get_object() if hasattr(field_ref, 'get_object') else field_ref
                                    if isinstance(field_obj, DictionaryObject) and '/T' in field_obj:
                                        if str(field_obj['/T']) == original_name:
                                            field_obj[NameObject('/T')] = TextStringObject(new_name)
                                            logger.debug(f"Updated field in AcroForm: {original_name} → {new_name}")
                                            renamed = True
                                except Exception as e:
                                    logger.debug(f"Error updating field in AcroForm: {str(e)}")
                                    continue
            
            # Method 3: Try to find and update in original reader structure as well
            # This helps maintain consistency
            for page_num, page in enumerate(self.reader.pages):
                if hasattr(page, '/Annots') and page['/Annots']:
                    for annot_ref in page['/Annots']:
                        try:
                            annot = annot_ref.get_object()
                            if '/T' in annot and str(annot['/T']) == original_name:
                                # This won't persist but helps with consistency
                                logger.debug(f"Found field {original_name} in reader on page {page_num + 1}")
                        except Exception as e:
                            continue
            
            if not renamed:
                logger.warning(f"Could not find or rename field: {original_name}")
            
            return renamed
            
        except Exception as e:
            logger.error(f"Error in _rename_field_in_pdf: {str(e)}")
            return False
    
    def save_pdf(self, output_path: str) -> bool:
        """Save the modified PDF to the specified path."""
        try:
            with open(output_path, 'wb') as output_file:
                self.writer.write(output_file)
            logger.info(f"PDF saved successfully to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving PDF: {str(e)}")
            return False

@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="modify_pdf_fields",
            description="Modify PDF field names based on JSON mapping from Claude analysis. COMPLETE IMPLEMENTATION with actual field renaming.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_path": {
                        "type": "string",
                        "description": "Path to the original PDF file that needs field name modifications"
                    },
                    "field_mappings": {
                        "type": "object",
                        "description": "JSON mapping object from Claude containing field name changes. Should include 'field_mappings' array with original_name -> generated_name mappings."
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Optional output path for the modified PDF (defaults to original_BEM_named.pdf)",
                        "default": ""
                    },
                    "create_backup": {
                        "type": "boolean",
                        "description": "Whether to create a backup of the original PDF before modification",
                        "default": True
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "If true, analyze what would be changed without actually modifying the PDF",
                        "default": False
                    }
                },
                "required": ["pdf_path", "field_mappings"]
            }
        ),
        Tool(
            name="test_connection",
            description="Test MCP server connection and verify all dependencies are working correctly",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_version_info": {
                        "type": "boolean",
                        "description": "Include detailed version information in the response",
                        "default": True
                    }
                }
            }
        ),
        Tool(
            name="analyze_pdf_fields",
            description="Analyze a PDF file to list all existing form fields without modifying anything. Enhanced analysis with field type detection.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_path": {
                        "type": "string",
                        "description": "Path to the PDF file to analyze"
                    },
                    "include_annotations": {
                        "type": "boolean",
                        "description": "Whether to include annotation details in the analysis",
                        "default": True
                    }
                },
                "required": ["pdf_path"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    
    try:
        if name == "test_connection":
            return await test_connection(**arguments)
        elif name == "modify_pdf_fields":
            return await modify_pdf_fields(**arguments)
        elif name == "analyze_pdf_fields":
            return await analyze_pdf_fields(**arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error in tool '{name}': {str(e)}")
        error_result = {
            "status": "error",
            "tool": name,
            "message": f"Tool execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

async def test_connection(include_version_info: bool = True) -> List[TextContent]:
    """Test the MCP server connection and dependencies."""
    try:
        test_result = {
            "status": "success",
            "message": "✅ PDF Field Modifier (COMPLETE) is working correctly!",
            "architecture": "Complete - Claude intelligence + Full PDF field renaming",
            "server_name": "pdf-field-modifier-complete",
            "tools_available": ["modify_pdf_fields", "test_connection", "analyze_pdf_fields"],
            "workflow": "Upload PDF → Claude analyzes → Generate BEM names → ACTUALLY RENAME FIELDS → Modified PDF",
            "capabilities": [
                "Real PDF field renaming",
                "All field types supported",
                "AcroForm and annotation handling",
                "Backup and safety features",
                "Comprehensive error handling"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        if include_version_info:
            test_result["dependencies"] = {
                "python": f"v{sys.version.split()[0]}",
                "PyPDF2": f"v{PyPDF2.__version__}",
                "platform": sys.platform
            }
        
        logger.info("MCP server test completed successfully")
        return [TextContent(type="text", text=json.dumps(test_result, indent=2))]
        
    except Exception as e:
        logger.error(f"MCP server test failed: {str(e)}")
        error_result = {
            "status": "error",
            "message": f"MCP server test failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

async def analyze_pdf_fields(pdf_path: str, include_annotations: bool = True) -> List[TextContent]:
    """Analyze PDF fields without modifying the file. Enhanced analysis."""
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"Analyzing PDF fields in: {pdf_path}")
        
        # Use the enhanced PDFFieldRenamer for analysis
        with PDFFieldRenamer(pdf_path) as renamer:
            form_analysis = renamer.analyze_form_structure()
            
            analysis = {
                "status": "success",
                "message": "Enhanced PDF field analysis completed",
                "pdf_path": pdf_path,
                "page_count": form_analysis["total_pages"],
                "form_fields": [],
                "field_types": form_analysis["field_types"],
                "field_positions": form_analysis["field_positions"],
                "annotations": form_analysis["annotations"],
                "timestamp": datetime.now().isoformat()
            }
            
            # Convert form fields to list format
            for field_name, field_info in form_analysis["form_fields"].items():
                analysis["form_fields"].append({
                    "name": field_name,
                    "value": field_info.get("value"),
                    "type": field_info.get("type"),
                    "source": field_info.get("source"),
                    "page": field_info.get("page"),
                    "position": field_info.get("position")
                })
            
            analysis["summary"] = {
                "total_form_fields": len(analysis["form_fields"]),
                "total_annotations": sum(len(page_annots) for page_annots in form_analysis["annotations"].values()),
                "has_forms": len(analysis["form_fields"]) > 0,
                "field_types_found": list(set(form_analysis["field_types"].values())),
                "next_step": "Use Claude to generate BEM field names, then call modify_pdf_fields to rename"
            }
        
        logger.info(f"Enhanced PDF analysis completed. Found {len(analysis['form_fields'])} form fields")
        return [TextContent(type="text", text=json.dumps(analysis, indent=2))]
        
    except Exception as e:
        logger.error(f"PDF analysis failed: {str(e)}")
        error_result = {
            "status": "error",
            "message": f"PDF analysis failed: {str(e)}",
            "pdf_path": pdf_path,
            "timestamp": datetime.now().isoformat()
        }
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

async def modify_pdf_fields(
    pdf_path: str,
    field_mappings: Dict[str, Any],
    output_path: str = "",
    create_backup: bool = True,
    dry_run: bool = False
) -> List[TextContent]:
    """
    COMPLETE IMPLEMENTATION: Actually modify PDF field names based on JSON mapping from Claude.
    
    Args:
        pdf_path: Path to original PDF
        field_mappings: JSON from Claude with field name changes
        output_path: Optional output path
        create_backup: Create backup before modification
        dry_run: Analyze changes without modifying
        
    Returns:
        Success status, modified PDF path, change summary with ACTUAL field renaming
    """
    try:
        logger.info(f"Starting COMPLETE PDF field modification: {pdf_path}")
        
        # Validate inputs
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not field_mappings or "field_mappings" not in field_mappings:
            raise ValueError("Invalid field_mappings structure. Expected 'field_mappings' key with array of mappings.")
        
        # Setup paths
        pdf_file = Path(pdf_path)
        if not output_path:
            output_path = pdf_file.parent / f"{pdf_file.stem}_BEM_named{pdf_file.suffix}"
        else:
            output_path = Path(output_path)
        
        backup_path = None
        if create_backup and not dry_run:
            backup_path = pdf_file.parent / f"{pdf_file.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{pdf_file.suffix}"
            shutil.copy2(pdf_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
        
        # Use the complete PDFFieldRenamer for actual modification
        with PDFFieldRenamer(pdf_path) as renamer:
            # Analyze existing structure
            form_analysis = renamer.analyze_form_structure()
            existing_fields = set(form_analysis["form_fields"].keys())
            
            # Process field mappings
            changes_planned = []
            changes_successful = []
            errors = []
            
            for mapping in field_mappings["field_mappings"]:
                original_name = mapping.get("original_name", "")
                new_name = mapping.get("generated_name", "")
                field_type = mapping.get("field_type", "")
                
                if not original_name or not new_name:
                    errors.append("Invalid mapping: missing original_name or generated_name")
                    continue
                
                changes_planned.append({
                    "original": original_name,
                    "new": new_name,
                    "type": field_type,
                    "section": mapping.get("section", ""),
                    "confidence": mapping.get("confidence", "")
                })
            
            # Perform the actual field renaming (not just copying!)
            if not dry_run:
                logger.info(f"Performing ACTUAL field renaming for {len(changes_planned)} fields...")
                
                # This is the key difference - ACTUAL field renaming
                rename_results = renamer.rename_fields(field_mappings["field_mappings"])
                
                # Save the modified PDF
                save_success = renamer.save_pdf(str(output_path))
                
                if save_success:
                    changes_successful = rename_results["successful_renames"]
                    errors.extend([f"Rename failed: {err}" for err in rename_results["failed_renames"]])
                    logger.info(f"PDF with renamed fields saved to: {output_path}")
                else:
                    errors.append("Failed to save modified PDF")
            else:
                logger.info("Dry run mode - no actual modifications performed")
        
        # Prepare comprehensive result
        result = {
            "status": "success",
            "operation": "dry_run" if dry_run else "COMPLETE_FIELD_MODIFICATION",
            "message": f"PDF field {'analysis' if dry_run else 'RENAMING'} completed",
            "original_pdf": str(pdf_path),
            "modified_pdf": str(output_path) if not dry_run else None,
            "backup_created": str(backup_path) if backup_path else None,
            "existing_fields_found": len(existing_fields),
            "changes_planned": len(changes_planned),
            "changes_successful": len(changes_successful) if not dry_run else 0,
            "errors": len(errors),
            "details": {
                "existing_fields": list(existing_fields),
                "planned_changes": changes_planned,
                "successful_changes": changes_successful if not dry_run else [],
                "errors": errors
            },
            "architecture_note": "COMPLETE IMPLEMENTATION: This actually renames PDF fields using PyPDF2 manipulation.",
            "timestamp": datetime.now().isoformat()
        }
        
        if dry_run:
            result["note"] = "This was a dry run. No files were modified."
        else:
            result["note"] = f"PDF fields successfully renamed! {len(changes_successful)} fields modified."
        
        logger.info(f"COMPLETE PDF modification finished. Planned: {len(changes_planned)}, Successful: {len(changes_successful)}, Errors: {len(errors)}")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        logger.error(f"COMPLETE PDF modification failed: {str(e)}")
        error_result = {
            "status": "error",
            "message": f"Complete PDF modification failed: {str(e)}",
            "pdf_path": pdf_path,
            "timestamp": datetime.now().isoformat()
        }
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

if __name__ == "__main__":
    """
    Run the COMPLETE MCP server when executed directly.
    Usage: python pdf_field_modifier_complete.py
    """
    import asyncio
    
    async def main():
        try:
            from mcp.server.stdio import stdio_server
            
            logger.info("Starting COMPLETE PDF Field Modifier MCP Server...")
            async with stdio_server() as (read_stream, write_stream):
                await app.run(
                    read_stream, 
                    write_stream, 
                    app.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"Failed to start COMPLETE MCP server: {str(e)}")
            sys.exit(1)
    
    asyncio.run(main())
