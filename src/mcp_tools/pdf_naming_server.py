#!/usr/bin/env python3
"""
PDF Naming MCP Server

Provides MCP tools for Claude Desktop integration:
- extract_fields: Extract PDF form fields 
- generate_names: AI-powered BEM naming
- validate_names: Name validation and conflict detection
- export_mapping: Export structured field mappings

This server integrates the existing PDF field extraction with AI-powered
naming to create a seamless workflow in Claude Desktop.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp import server
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Import our existing PDF extraction functionality and tool classes
import sys
sys.path.append(str(Path(__file__).parent.parent))
from pdf_parser.field_extractor import PDFFieldExtractor
from .tools import ExtractFieldsTool, GenerateNamesTool, ValidateNamesTool, ExportMappingTool
from .config.server_config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pdf_naming_server")

class PDFNamingServer:
    """MCP Server for PDF field naming workflow."""
    
    def __init__(self, environment: str = "development"):
        """Initialize the PDF naming server."""
        self.config = get_config(environment)
        self.server = Server("pdf-naming")
        
        # Initialize tool instances
        self.extract_tool = ExtractFieldsTool()
        self.generate_tool = GenerateNamesTool()
        self.validate_tool = ValidateNamesTool()
        self.export_tool = ExportMappingTool()
        
        self._setup_tools()
        
    def _setup_tools(self):
        """Register all MCP tools with the server."""
        
        # Tool 1: Extract PDF Fields
        @self.server.call_tool()
        async def extract_fields(
            pdf_path: str,
            context_radius: int = 50,
            output_format: str = "csv"
        ) -> List[TextContent]:
            """Extract form fields from a PDF file."""
            try:
                result = await self.extract_tool.execute(pdf_path, context_radius, output_format)
                
                if not result["success"]:
                    return [TextContent(
                        type="text",
                        text=f"❌ Field extraction failed: {result.get('error', 'Unknown error')}"
                    )]
                
                return [TextContent(
                    type="text", 
                    text=f"✅ Successfully extracted {result['extraction_metadata']['field_count']} fields from {result['extraction_metadata']['pages_processed']} pages.\n\n" +
                         f"Field extraction data:\n{json.dumps(result, indent=2)}"
                )]
                
            except Exception as e:
                logger.error(f"Error in extract_fields: {str(e)}")
                return [TextContent(
                    type="text",
                    text=f"❌ Error extracting fields: {str(e)}"
                )]
        
        # Tool 2: Generate BEM Names
        @self.server.call_tool()
        async def generate_names(
            field_data: dict,
            use_training_data: bool = True,
            confidence_threshold: float = 0.7,
            naming_strategy: str = "context_aware"
        ) -> List[TextContent]:
            """Generate BEM-style API names for extracted fields."""
            try:
                result = await self.generate_tool.execute(
                    field_data, use_training_data, confidence_threshold, naming_strategy
                )
                
                if not result["success"]:
                    return [TextContent(
                        type="text",
                        text=f"❌ Name generation failed: {result.get('error', 'Unknown error')}"
                    )]
                
                metadata = result["generation_metadata"]
                return [TextContent(
                    type="text",
                    text=f"✅ Generated {metadata['generated_count']} BEM-style field names.\n" +
                         f"High confidence: {metadata['high_confidence_count']}\n\n" +
                         f"Name generation results:\n{json.dumps(result, indent=2)}"
                )]
                
            except Exception as e:
                logger.error(f"Error in generate_names: {str(e)}")
                return [TextContent(
                    type="text",
                    text=f"❌ Error generating names: {str(e)}"
                )]
        
        # Tool 3: Validate Names
        @self.server.call_tool()
        async def validate_names(
            name_data: dict,
            check_duplicates: bool = True,
            check_bem_compliance: bool = True,
            check_reserved_names: bool = True,
            strict_mode: bool = False
        ) -> List[TextContent]:
            """Validate generated field names for compliance and conflicts."""
            try:
                result = await self.validate_tool.execute(
                    name_data, check_duplicates, check_bem_compliance, 
                    check_reserved_names, strict_mode
                )
                
                if not result["success"]:
                    return [TextContent(
                        type="text",
                        text=f"❌ Validation failed: {result.get('error', 'Unknown error')}"
                    )]
                
                summary = result["validation_summary"]
                return [TextContent(
                    type="text",
                    text=f"✅ Validated {summary['valid_names']}/{result['validation_metadata']['total_names']} field names.\n" +
                         f"Errors: {summary['errors']}, Warnings: {summary['warnings']}\n\n" +
                         f"Validation results:\n{json.dumps(result, indent=2)}"
                )]
                
            except Exception as e:
                logger.error(f"Error in validate_names: {str(e)}")
                return [TextContent(
                    type="text",
                    text=f"❌ Error validating names: {str(e)}"
                )]
        
        # Tool 4: Export Mapping
        @self.server.call_tool()
        async def export_mapping(
            validated_names: dict,
            output_format: str = "json",
            include_metadata: bool = True,
            include_backup_plan: bool = True,
            validation_threshold: float = 0.0
        ) -> List[TextContent]:
            """Export final field mapping for PDF modification."""
            try:
                result = await self.export_tool.execute(
                    validated_names, output_format, include_metadata,
                    include_backup_plan, validation_threshold
                )
                
                if not result["success"]:
                    return [TextContent(
                        type="text",
                        text=f"❌ Export failed: {result.get('error', 'Unknown error')}"
                    )]
                
                metadata = result["export_metadata"]
                summary = result["export_summary"]
                return [TextContent(
                    type="text",
                    text=f"✅ Exported mapping for {metadata['exported_fields']}/{metadata['total_fields']} fields.\n" +
                         f"Ready for modification: {summary['ready_for_modification']}\n\n" +
                         f"Export results:\n{json.dumps(result, indent=2)}"
                )]
                
            except Exception as e:
                logger.error(f"Error in export_mapping: {str(e)}")
                return [TextContent(
                    type="text",
                    text=f"❌ Error exporting mapping: {str(e)}"
                )]

    async def run(self):
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server
        
        logger.info("Starting PDF Naming MCP Server")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

def main():
    """Main entry point for the MCP server."""
    server = PDFNamingServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main()