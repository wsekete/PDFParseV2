# Claude Desktop MCP Integration Verification Guide

## Overview

This guide provides step-by-step instructions for verifying and troubleshooting the Claude Desktop MCP integration for the PDFParseV2 project.

## Quick Verification Steps

### 1. Run the Setup Test Script

```bash
cd /Users/wseke/Desktop/PDFParseV2
python3 test_mcp_setup.py
```

This will check:
- Python version compatibility
- MCP dependencies
- MCP server file existence
- Claude Desktop configuration
- PDF samples availability

### 2. Install Claude Desktop Configuration

```bash
python3 setup_claude_desktop.py
```

This will:
- Check all dependencies
- Verify MCP server
- Install configuration to Claude Desktop
- Create backups of existing config

### 3. Test MCP Server Directly

```bash
python3 src/pdf_modifier/mcp_server.py
```

Expected output: Server should start without errors and show MCP server initialization.

## Configuration Details

### Correct Configuration File Location

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

### Expected Configuration Content

```json
{
  "mcpServers": {
    "pdf-field-modifier": {
      "command": "python3",
      "args": [
        "/Users/wseke/Desktop/PDFParseV2/src/pdf_modifier/mcp_server.py"
      ],
      "cwd": "/Users/wseke/Desktop/PDFParseV2",
      "env": {
        "PYTHONPATH": "/Users/wseke/Desktop/PDFParseV2"
      },
      "description": "PDF Field Modifier - AI-powered PDF form field renaming engine"
    }
  },
  "global": {
    "allowAnalytics": false,
    "logLevel": "info"
  }
}
```

**Important**: Update the path `/Users/wseke/Desktop/PDFParseV2` to match your actual project location.

## Available MCP Tools

Once properly configured, these tools will be available in Claude Desktop:

### 1. `test_connection`
- **Purpose**: Verify MCP server is working
- **Parameters**: `include_version_info` (optional, boolean)
- **Usage**: Test this first to ensure connectivity

### 2. `analyze_pdf_fields`
- **Purpose**: Analyze PDF form fields without modification
- **Parameters**: 
  - `pdf_path` (required, string)
  - `include_annotations` (optional, boolean)
- **Usage**: Extract field information from PDF

### 3. `modify_pdf_fields`
- **Purpose**: Actually rename PDF form fields
- **Parameters**:
  - `pdf_path` (required, string)
  - `field_mappings` (required, object)
  - `output_path` (optional, string)
  - `create_backup` (optional, boolean)
  - `dry_run` (optional, boolean)
- **Usage**: Perform actual field renaming

### 4. Enhanced PyPDFForm Tools (v2.0.0)
- `modify_pdf_fields_v2` - Enhanced field modification
- `preview_field_renames` - Preview changes without applying
- `extract_pdf_fields_enhanced` - Enhanced field extraction

## Testing Workflow

### Step 1: Test Connection
```
Use test_connection tool with:
{
  "include_version_info": true
}
```

Expected result: Success message with version information.

### Step 2: Analyze Sample PDF
```
Use analyze_pdf_fields tool with:
{
  "pdf_path": "/Users/wseke/Desktop/PDFParseV2/training_data/pdf_csv_pairs/W-4R_parsed.pdf",
  "include_annotations": true
}
```

Expected result: List of form fields with types and positions.

### Step 3: Test Field Modification (Dry Run)
```
Use modify_pdf_fields tool with:
{
  "pdf_path": "/Users/wseke/Desktop/PDFParseV2/training_data/pdf_csv_pairs/W-4R_parsed.pdf",
  "field_mappings": {
    "field_mappings": [
      {
        "original_name": "firstName",
        "generated_name": "personal-information_first-name"
      }
    ]
  },
  "dry_run": true
}
```

Expected result: Analysis of what would be changed without actual modification.

## Common Issues and Solutions

### Issue 1: MCP Server Not Found
**Symptoms**: Tools don't appear in Claude Desktop
**Solutions**:
1. Check configuration file path is correct
2. Verify MCP server file exists at specified path
3. Restart Claude Desktop after configuration changes

### Issue 2: Python Import Errors
**Symptoms**: MCP server fails to start
**Solutions**:
1. Check Python environment: `python3 --version`
2. Install dependencies: `pip install -r requirements.txt`
3. Verify PYTHONPATH in configuration

### Issue 3: Permission Errors
**Symptoms**: Cannot read/write files
**Solutions**:
1. Check file permissions: `ls -la [file_path]`
2. Ensure Claude Desktop has necessary permissions
3. Try running with different user permissions

### Issue 4: PDF Processing Errors
**Symptoms**: Tools work but PDF processing fails
**Solutions**:
1. Check PDF file is not corrupted
2. Verify PyPDF2 and PyPDFForm are installed
3. Try with different PDF files

### Issue 5: Configuration Not Loading
**Symptoms**: Configuration exists but not recognized
**Solutions**:
1. Check JSON syntax: `python3 -m json.tool config.json`
2. Verify configuration file location
3. Check Claude Desktop logs for errors

## Debugging Tips

### Enable Detailed Logging
Set log level to "debug" in configuration:
```json
{
  "global": {
    "logLevel": "debug"
  }
}
```

### Check Claude Desktop Logs
- **macOS**: `~/Library/Logs/Claude/`
- **Windows**: `%APPDATA%\Claude\logs\`
- **Linux**: `~/.config/Claude/logs/`

### Test MCP Server Independently
```bash
cd /Users/wseke/Desktop/PDFParseV2
python3 -c "from src.pdf_modifier.mcp_server import app; print('Server loaded successfully')"
```

## Dependency Requirements

### Core Dependencies
- Python 3.8+
- mcp >= 0.2.0
- PyPDF2 >= 3.0.1
- PyPDFForm >= 3.1.2
- pdfplumber >= 0.7.6
- pandas >= 2.1.3
- pydantic >= 2.5.0
- loguru >= 0.7.2

### Installation
```bash
pip install -r requirements.txt
```

## Verification Checklist

- [ ] Python 3.8+ installed
- [ ] All dependencies installed
- [ ] MCP server file exists and is readable
- [ ] Claude Desktop configuration installed
- [ ] Claude Desktop restarted
- [ ] `test_connection` tool works
- [ ] `analyze_pdf_fields` tool works
- [ ] PDF samples available for testing
- [ ] Field modification works (dry run)
- [ ] Full workflow tested

## Support

If you encounter issues not covered in this guide:

1. Check the main project documentation in `CLAUDE.md`
2. Review the implementation details in `PHASE2_TASKS.md`
3. Run `python3 test_mcp_setup.py` for diagnostic information
4. Check Claude Desktop logs for detailed error messages

## Sample PDFs for Testing

The following PDFs are available in `training_data/pdf_csv_pairs/`:
- `W-4R_parsed.pdf` - Simple text fields (good for initial testing)
- `LIFE-1528-Q__parsed.pdf` - Complex form with radio buttons
- `FAF-0485AO__parsed.pdf` - Checkbox-heavy form

Start with `W-4R_parsed.pdf` for initial testing as it has the simplest field structure.