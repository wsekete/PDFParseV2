# Claude Desktop Integration Setup

This guide will help you integrate the PDF Field Naming System with Claude Desktop using MCP (Model Context Protocol).

## Prerequisites

- Claude Desktop application installed
- Python 3.8+ with required dependencies
- PDFParseV2 project cloned and dependencies installed

## Installation Steps

### 1. Install Dependencies

```bash
cd /Users/wseke/Desktop/PDFParseV2
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Configure Claude Desktop

1. **Locate Claude Desktop Configuration**
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Update Configuration**
   Copy the contents of `claude_desktop_config.json` from this project into your Claude Desktop config file:

```json
{
  "mcpServers": {
    "pdf-naming": {
      "command": "python",
      "args": [
        "/Users/wseke/Desktop/PDFParseV2/src/mcp_tools/pdf_naming_server.py"
      ],
      "cwd": "/Users/wseke/Desktop/PDFParseV2",
      "env": {
        "PYTHONPATH": "/Users/wseke/Desktop/PDFParseV2"
      }
    }
  }
}
```

**Important**: Update the path `/Users/wseke/Desktop/PDFParseV2` to match your actual project location.

### 3. Restart Claude Desktop

After updating the configuration, restart Claude Desktop to load the MCP server.

## Available Tools

Once configured, you'll have access to these tools in Claude Desktop:

### 🔍 `extract_fields`
Extract form fields from PDF files with context analysis.

**Parameters:**
- `pdf_path` (required): Path to PDF file
- `context_radius` (optional): Pixel radius for text context (default: 50)
- `output_format` (optional): "csv" or "json" (default: "csv")

### 🏷️ `generate_names`
Generate BEM-style API names for extracted fields.

**Parameters:**
- `field_data` (required): Output from extract_fields
- `use_training_data` (optional): Use training patterns (default: true)
- `confidence_threshold` (optional): Min confidence 0.0-1.0 (default: 0.7)
- `naming_strategy` (optional): "context_aware" or "pattern_based"

### ✅ `validate_names`
Validate generated names for BEM compliance and conflicts.

**Parameters:**
- `name_data` (required): Output from generate_names
- `check_duplicates` (optional): Check for duplicates (default: true)
- `check_bem_compliance` (optional): Validate BEM syntax (default: true)
- `check_reserved_names` (optional): Check reserved names (default: true)
- `strict_mode` (optional): Enable strict validation (default: false)

### 📤 `export_mapping`
Export structured field mappings for PDF modification.

**Parameters:**
- `validated_names` (required): Output from validate_names
- `output_format` (optional): "json" or "csv" (default: "json")
- `include_metadata` (optional): Include metadata (default: true)
- `include_backup_plan` (optional): Include backup strategy (default: true)
- `validation_threshold` (optional): Min score 0.0-1.0 (default: 0.0)

## Example Workflow

1. **Upload PDF**: Share a PDF file with Claude Desktop
2. **Extract Fields**: Use `extract_fields` tool with the PDF path
3. **Generate Names**: Use `generate_names` with the extracted field data
4. **Validate Names**: Use `validate_names` to check for issues
5. **Export Mapping**: Use `export_mapping` to get structured output

## Troubleshooting

### MCP Server Not Starting
- Check Python path is correct in configuration
- Verify all dependencies are installed
- Check Claude Desktop logs for error messages

### Permission Errors
- Ensure Claude Desktop has file system permissions
- Check that PDF files are accessible
- Verify write permissions for output directories

### Tool Not Found
- Restart Claude Desktop after configuration changes
- Verify JSON syntax in configuration file
- Check MCP server logs for startup errors

## Support

For issues and questions:
- Check the project documentation in `CLAUDE.md`
- Review task details in `PHASE2_TASKS.md`
- Submit issues to the GitHub repository

## Security Notes

- The MCP server runs in a sandboxed environment
- File system access is limited to project directories
- No network access is required or granted
- Processing timeout is set to 5 minutes maximum