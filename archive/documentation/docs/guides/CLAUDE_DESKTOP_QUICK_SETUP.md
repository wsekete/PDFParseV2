# Claude Desktop Setup Instructions

## Quick Setup

1. **Copy Configuration**
   ```bash
   # macOS
   cp claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
   
   # Windows  
   copy claude_desktop_config.json %APPDATA%\Claude\claude_desktop_config.json
   
   # Linux
   cp claude_desktop_config.json ~/.config/Claude/claude_desktop_config.json
   ```

2. **Restart Claude Desktop**

3. **Test with Sample Commands**
   - `extract_fields` - Extract PDF form fields
   - `generate_names` - Generate BEM-style names  
   - `validate_names` - Validate name compliance
   - `export_mapping` - Export structured mappings

## Sample Usage

1. **Upload a PDF** to Claude Desktop
2. **Extract fields**: Use extract_fields with the PDF path
3. **Generate names**: Use generate_names with the extracted data
4. **Validate names**: Use validate_names with the generated names
5. **Export mapping**: Use export_mapping for final structured output

## Troubleshooting

- Check Claude Desktop logs if tools don't appear
- Verify Python path in configuration matches your system
- Ensure all dependencies are installed: `pip install -r requirements.txt`

For detailed instructions, see CLAUDE_DESKTOP_SETUP.md