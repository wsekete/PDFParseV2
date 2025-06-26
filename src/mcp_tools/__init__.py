"""
MCP Tools for PDF Field Naming and Claude Desktop Integration

Provides Model Context Protocol (MCP) tools for:
- PDF form field extraction with context analysis
- AI-powered BEM naming generation
- Field name validation and conflict detection  
- Structured mapping export for PDF modification

Usage:
    from src.mcp_tools import PDFNamingServer
    server = PDFNamingServer()
    asyncio.run(server.run())

Tools Available:
- extract_fields: Extract PDF form fields
- generate_names: Generate BEM-style names
- validate_names: Validate generated names
- export_mapping: Export field mappings

See README.md for detailed usage instructions.
"""

from .pdf_naming_server import PDFNamingServer
from .tools import ExtractFieldsTool, GenerateNamesTool, ValidateNamesTool, ExportMappingTool
from .config.server_config import get_config

__all__ = [
    "PDFNamingServer",
    "ExtractFieldsTool",
    "GenerateNamesTool", 
    "ValidateNamesTool",
    "ExportMappingTool",
    "get_config"
]

__version__ = "1.0.0"