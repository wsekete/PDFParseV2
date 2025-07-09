# PDFParse BEM Field Naming Tool

🚀 **Intelligent BEM field naming for PDF forms using financial services conventions.**

This MCP (Model Context Protocol) server provides a tool for Claude Desktop that generates consistent, meaningful BEM-style field names for PDF forms, specifically optimized for financial services workflows.

## ✨ Features

- **🏷️ Field Type Detection** - Identifies TextField, Checkbox, RadioButton, Signature, DateField
- **📊 Radio Group Handling** - Proper `--group` suffix containers with individual options
- **🏢 Financial Services Conventions** - Optimized naming patterns for financial forms
- **🧹 Clean Output** - Section-by-section breakdown without JSON clutter
- **🔄 Always Available** - Integrated directly into Claude Desktop's tool menu

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Claude Desktop

Copy the configuration to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pdf-field-modifier": {
      "command": "python",
      "args": [
        "/path/to/PDFParseV2/src/pdf_modifier/mcp_server.py"
      ],
      "cwd": "/path/to/PDFParseV2",
      "env": {
        "PYTHONPATH": "/path/to/PDFParseV2"
      }
    }
  }
}
```

### 3. Use the Tool

1. **Restart Claude Desktop**
2. **Upload a PDF** form to Claude Desktop
3. **Use the tool:** Look for `🚀 generate_bem_field_names` in the tools menu
4. **Enter filename:** e.g., "form.pdf"
5. **Get results:** Section-by-section BEM field breakdown with field types

## 📋 Example Output

```
## Section-by-Section BEM Field Breakdown:

### 1. General Information (Owner's Information)
* owner-information_first-name (TextField)
* owner-information_last-name (TextField)
* owner-information_policy-number (TextField)

### 3. Name Changes
* name-change_entity--group (RadioGroup)
* name-change_entity__primary-insured (RadioButton)
* name-change_entity__payor (RadioButton)
* name-change_reason--group (RadioGroup)
* name-change_reason__marriage (RadioButton)
* name-change_reason__divorce (RadioButton)

### 9. Signatures
* signatures_owner (TextField)
* signatures_owner-signature (Signature)
* signatures_owner-date (DateField)
```

## 🎯 BEM Naming Conventions

- **Block:** Form sections (`owner-information`, `name-change`, `signatures`)
- **Element:** Individual fields (`first-name`, `policy-number`, `signature`)
- **Modifier:** Field variations (`__marriage`, `__divorce`, `__primary-insured`)
- **Radio Groups:** Container suffix (`--group`)

## 🔧 Field Types

- **TextField** - Text input fields
- **Checkbox** - Individual checkboxes  
- **RadioGroup** - Container for radio button groups
- **RadioButton** - Individual radio button options
- **Signature** - Signature fields
- **DateField** - Date input fields

## 📁 Project Structure

```
PDFParseV2/
├── src/pdf_modifier/
│   ├── __init__.py
│   └── mcp_server.py          # Main MCP server
├── claude_desktop_config.json # Claude Desktop configuration
├── requirements.txt           # Dependencies
├── README.md                  # This file
└── archive/                   # Archived old implementation
```

## 🛠️ Development

The MCP server is self-contained in `src/pdf_modifier/mcp_server.py`. It uses Claude's natural PDF processing capabilities to analyze forms and generate BEM field names according to financial services conventions.

## 📄 License

This project is designed for financial services PDF form processing and BEM field name generation.

## 🤝 Contributing

This tool is specifically optimized for financial services forms. Contributions should maintain the established BEM naming conventions and field type detection accuracy.
