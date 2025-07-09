# Claude Desktop MCP Integration - Quick Start

## 🚀 Quick Setup (3 steps)

### Step 1: Test Your Setup
```bash
cd /Users/wseke/Desktop/PDFParseV2
python3 test_mcp_server_basic.py
```

### Step 2: Install Configuration
```bash
python3 setup_claude_desktop.py
```

### Step 3: Restart Claude Desktop
Close and reopen Claude Desktop to load the new configuration.

## 🧪 Testing in Claude Desktop

Once Claude Desktop is restarted, test these tools in order:

### 1. Test Connection
```
Use the test_connection tool with:
{
  "include_version_info": true
}
```

### 2. Analyze Sample PDF
```
Use the analyze_pdf_fields tool with:
{
  "pdf_path": "/Users/wseke/Desktop/PDFParseV2/training_data/pdf_csv_pairs/W-4R_parsed.pdf"
}
```

### 3. Test Field Modification (Dry Run)
```
Use the modify_pdf_fields tool with:
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

## 🎯 Expected Results

- **test_connection**: Should return success message with version info
- **analyze_pdf_fields**: Should list form fields found in the PDF
- **modify_pdf_fields**: Should show what would be changed (dry run)

## 🔧 Available Tools

1. **test_connection** - Verify MCP server is working
2. **analyze_pdf_fields** - Extract PDF form field information
3. **modify_pdf_fields** - Actually rename PDF form fields
4. **modify_pdf_fields_v2** - Enhanced field modification (PyPDFForm)
5. **preview_field_renames** - Preview changes before applying
6. **extract_pdf_fields_enhanced** - Enhanced field extraction

## 🚨 Troubleshooting

If tools don't appear:
1. Check Claude Desktop logs
2. Verify configuration was installed correctly
3. Ensure Python path is correct for your system
4. Try running `python3 test_mcp_setup.py` for diagnostics

## 📍 Configuration Location

Your configuration is installed at:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

## 💡 Usage Tips

1. Always test with `test_connection` first
2. Use `dry_run: true` for testing modifications
3. Start with simple PDFs like `W-4R_parsed.pdf`
4. Check backup files are created before modifications
5. Review the comprehensive guide in `CLAUDE_DESKTOP_VERIFICATION_GUIDE.md` for detailed troubleshooting

## 🎉 Success Criteria

✅ All 3 test tools work correctly
✅ PDF analysis shows form fields
✅ Field modification dry run completes without errors
✅ You can see field mappings and validation results

Your Claude Desktop MCP integration is working correctly!