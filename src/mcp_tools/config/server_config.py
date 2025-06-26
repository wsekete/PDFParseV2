"""
MCP Server Configuration

Defines configuration settings for the PDF naming MCP server,
including tool definitions, permissions, and Claude Desktop integration.
"""

from typing import Dict, Any, List

# Server metadata
SERVER_INFO = {
    "name": "pdf-naming",
    "version": "1.0.0",
    "description": "PDF field extraction and intelligent naming for Claude Desktop",
    "author": "PDFParseV2",
    "homepage": "https://github.com/wsekete/PDFParseV2"
}

# Tool definitions for MCP registration
TOOL_DEFINITIONS = [
    {
        "name": "extract_fields",
        "description": "Extract form fields from a PDF file with context analysis",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pdf_path": {
                    "type": "string",
                    "description": "Path to the PDF file to process"
                },
                "context_radius": {
                    "type": "integer",
                    "description": "Pixel radius for text context extraction",
                    "default": 50,
                    "minimum": 10,
                    "maximum": 200
                },
                "output_format": {
                    "type": "string",
                    "description": "Output format for extracted data",
                    "enum": ["csv", "json"],
                    "default": "csv"
                }
            },
            "required": ["pdf_path"]
        }
    },
    {
        "name": "generate_names",
        "description": "Generate BEM-style API names for extracted PDF fields",
        "inputSchema": {
            "type": "object",
            "properties": {
                "field_data": {
                    "type": "object",
                    "description": "Field data from extract_fields tool"
                },
                "use_training_data": {
                    "type": "boolean",
                    "description": "Whether to use training data patterns",
                    "default": True
                },
                "confidence_threshold": {
                    "type": "number",
                    "description": "Minimum confidence for auto-accept",
                    "default": 0.7,
                    "minimum": 0.0,
                    "maximum": 1.0
                },
                "naming_strategy": {
                    "type": "string",
                    "description": "Strategy for name generation",
                    "enum": ["context_aware", "pattern_based"],
                    "default": "context_aware"
                }
            },
            "required": ["field_data"]
        }
    },
    {
        "name": "validate_names",
        "description": "Validate generated field names for compliance and conflicts",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name_data": {
                    "type": "object",
                    "description": "Generated names from generate_names tool"
                },
                "check_duplicates": {
                    "type": "boolean",
                    "description": "Check for duplicate names",
                    "default": True
                },
                "check_bem_compliance": {
                    "type": "boolean",
                    "description": "Validate BEM syntax compliance",
                    "default": True
                },
                "check_reserved_names": {
                    "type": "boolean",
                    "description": "Check against reserved names",
                    "default": True
                },
                "strict_mode": {
                    "type": "boolean",
                    "description": "Enable strict validation rules",
                    "default": False
                }
            },
            "required": ["name_data"]
        }
    },
    {
        "name": "export_mapping",
        "description": "Export validated field mappings for PDF modification",
        "inputSchema": {
            "type": "object",
            "properties": {
                "validated_names": {
                    "type": "object",
                    "description": "Validated names from validate_names tool"
                },
                "output_format": {
                    "type": "string",
                    "description": "Export format",
                    "enum": ["json", "csv"],
                    "default": "json"
                },
                "include_metadata": {
                    "type": "boolean",
                    "description": "Include modification metadata",
                    "default": True
                },
                "include_backup_plan": {
                    "type": "boolean",
                    "description": "Include backup strategy information",
                    "default": True
                },
                "validation_threshold": {
                    "type": "number",
                    "description": "Minimum validation score to include field",
                    "default": 0.0,
                    "minimum": 0.0,
                    "maximum": 1.0
                }
            },
            "required": ["validated_names"]
        }
    }
]

# Resource definitions (for file access if needed)
RESOURCE_DEFINITIONS = [
    {
        "uri": "file://training_data/",
        "name": "Training Data",
        "description": "Access to PDF field naming training data",
        "mimeType": "text/csv"
    }
]

# Claude Desktop integration settings
CLAUDE_DESKTOP_CONFIG = {
    "mcpServers": {
        "pdf-naming": {
            "command": "python",
            "args": [
                "-m", "src.mcp_tools.pdf_naming_server"
            ],
            "cwd": ".",
            "env": {
                "PYTHONPATH": "."
            }
        }
    }
}

# Development configuration
DEV_CONFIG = {
    "logging": {
        "level": "DEBUG",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    },
    "tools": {
        "enable_debug_output": True,
        "max_field_count": 1000,
        "timeout_seconds": 30
    }
}

# Production configuration  
PROD_CONFIG = {
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(levelname)s - %(message)s"
    },
    "tools": {
        "enable_debug_output": False,
        "max_field_count": 500,
        "timeout_seconds": 60
    }
}

def get_config(environment: str = "development") -> Dict[str, Any]:
    """Get configuration for specified environment."""
    
    base_config = {
        "server_info": SERVER_INFO,
        "tool_definitions": TOOL_DEFINITIONS,
        "resource_definitions": RESOURCE_DEFINITIONS,
        "claude_desktop_config": CLAUDE_DESKTOP_CONFIG
    }
    
    if environment == "production":
        base_config.update(PROD_CONFIG)
    else:
        base_config.update(DEV_CONFIG)
    
    return base_config