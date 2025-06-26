# PDF Naming MCP Server

This MCP (Model Context Protocol) server provides tools for Claude Desktop to perform intelligent PDF field extraction and naming.

## 🚀 **Quick Start**

### 1. Configure Claude Desktop

Add this configuration to your Claude Desktop MCP settings:

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

### 2. Available Tools

#### `extract_fields`
Extract form fields from a PDF file with context analysis.

**Parameters:**
- `pdf_path` (required): Path to the PDF file
- `context_radius` (optional): Pixel radius for text context extraction (default: 50)
- `output_format` (optional): Output format - 'csv' or 'json' (default: 'csv')

**Example:**
```
extract_fields("/path/to/document.pdf", context_radius=100, output_format="csv")
```

#### `generate_names`
Generate BEM-style API names for extracted PDF fields.

**Parameters:**
- `field_data` (required): Field data from extract_fields tool
- `use_training_data` (optional): Whether to use training data patterns (default: true)
- `confidence_threshold` (optional): Minimum confidence for auto-accept (default: 0.7)
- `naming_strategy` (optional): Strategy - 'context_aware' or 'pattern_based' (default: 'context_aware')

**Example:**
```
generate_names(field_data, use_training_data=true, confidence_threshold=0.8)
```

#### `validate_names`
Validate generated field names for compliance and conflicts.

**Parameters:**
- `name_data` (required): Generated names from generate_names tool
- `check_duplicates` (optional): Check for duplicate names (default: true)
- `check_bem_compliance` (optional): Validate BEM syntax (default: true)
- `check_reserved_names` (optional): Check against reserved names (default: true)
- `strict_mode` (optional): Enable strict validation rules (default: false)

**Example:**
```
validate_names(name_data, check_duplicates=true, strict_mode=true)
```

#### `export_mapping`
Export validated field mappings for PDF modification.

**Parameters:**
- `validated_names` (required): Validated names from validate_names tool
- `output_format` (optional): Export format - 'json' or 'csv' (default: 'json')
- `include_metadata` (optional): Include modification metadata (default: true)
- `include_backup_plan` (optional): Include backup strategy (default: true)
- `validation_threshold` (optional): Minimum validation score to include field (default: 0.0)

**Example:**
```
export_mapping(validated_names, output_format="json", include_backup_plan=true)
```

## 🔄 **Typical Workflow**

1. **Extract fields** from PDF:
   ```
   extract_fields("/path/to/form.pdf")
   ```

2. **Generate BEM names** for the fields:
   ```
   generate_names(field_data_from_step1)
   ```

3. **Validate the generated names**:
   ```
   validate_names(generated_names_from_step2)
   ```

4. **Export final mapping** for PDF modification:
   ```
   export_mapping(validated_names_from_step3)
   ```

## 📋 **Output Formats**

### Field Extraction Output
```json
{
  "success": true,
  "extraction_metadata": {
    "pdf_path": "/path/to/form.pdf",
    "field_count": 25,
    "pages_processed": 3,
    "output_format": "csv"
  },
  "fields": [
    {
      "ID": 12345,
      "Label": "First Name",
      "Api name": "personal-information_first-name",
      "Type": "TextField",
      "X": 100,
      "Y": 200,
      "Width": 150,
      "Height": 20
    }
  ]
}
```

### Name Generation Output
```json
{
  "success": true,
  "generation_metadata": {
    "total_fields": 25,
    "generated_count": 25,
    "high_confidence_count": 20
  },
  "generated_names": [
    {
      "field_id": "uuid-123",
      "original_name": "FirstName",
      "suggested_name": "personal-information_first-name",
      "field_type": "TextField",
      "confidence": 0.9,
      "reasoning": "Applied BEM pattern with context analysis"
    }
  ]
}
```

### Validation Output
```json
{
  "success": true,
  "validation_summary": {
    "valid_names": 23,
    "warnings": 2,
    "errors": 0
  },
  "field_validations": [
    {
      "field_id": "uuid-123",
      "suggested_name": "personal-information_first-name",
      "is_valid": true,
      "errors": [],
      "warnings": [],
      "suggestions": []
    }
  ]
}
```

### Export Output
```json
{
  "success": true,
  "export_metadata": {
    "exported_fields": 25,
    "export_timestamp": "2025-06-26T11:00:00Z"
  },
  "mapping_data": {
    "field_mappings": [
      {
        "field_id": "uuid-123",
        "original_name": "FirstName",
        "new_name": "personal-information_first-name",
        "field_type": "TextField",
        "validation_status": "approved"
      }
    ],
    "modification_plan": {
      "backup_required": true,
      "modification_type": "acrofield_rename"
    }
  }
}
```

## 🔧 **Development**

### Running Tests
```bash
# Test tool imports
python -c "from src.mcp_tools.tools import *; print('✅ All imports successful')"

# Test field extraction
python -c "
import asyncio
from src.mcp_tools.tools.extract_fields import ExtractFieldsTool
async def test():
    tool = ExtractFieldsTool()
    result = await tool.execute('training_data/pdf_csv_pairs/W-4R_parsed.pdf')
    print(f'Success: {result[\"success\"]}')
asyncio.run(test())
"
```

### Configuration
- Development config: Enhanced logging, debug output enabled
- Production config: Optimized performance, minimal logging

### Architecture
```
src/mcp_tools/
├── pdf_naming_server.py    # Main MCP server
├── tools/                  # Individual tool implementations
│   ├── extract_fields.py   # PDF field extraction
│   ├── generate_names.py   # BEM name generation
│   ├── validate_names.py   # Name validation
│   └── export_mapping.py   # Mapping export
└── config/                 # Configuration files
    ├── server_config.py    # Tool definitions and settings
    └── claude_desktop_config.json  # Claude Desktop integration
```

## 📚 **Related Documentation**
- `PHASE2_TASKS.md` - Detailed implementation plan
- `CLAUDE.md` - Project overview and current status
- `training_data/` - BEM naming examples and test PDFs

---

**Status**: Task 2.1.1 Complete ✅ | Ready for Task 2.1.2 Implementation