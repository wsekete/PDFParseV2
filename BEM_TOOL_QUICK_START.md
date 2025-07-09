# BEM Field Naming Tool - Quick Start Guide

## ✅ Setup Complete!

Your MCP server has been updated to include the **BEM Field Naming Tool** that uses the proven prompt from your testing.

## 🚀 How to Use

### Step 1: Restart Claude Desktop
After any MCP server changes, restart Claude Desktop to load the new tool.

### Step 2: Upload PDF
- Upload your PDF form to Claude Desktop using drag & drop or the attachment button
- Note the exact filename (e.g., "Life-1528-Q.pdf")

### Step 3: Use the Tool
In Claude Desktop, you'll now see a new tool in the tools menu:
- **🚀 generate_bem_field_names** - Generate BEM field names for PDF forms

### Step 4: Get Results
1. Call the tool with the PDF filename
2. Get section-by-section BEM field breakdown
3. Get JSON mapping ready for PDF modifier tools

## 📋 Tool Details

**Tool Name:** `generate_bem_field_names`

**Parameters:**
- `pdf_filename` (required) - Name of uploaded PDF file

**Output:**
- Section-by-section BEM field breakdown
- JSON mapping structure
- Financial services naming conventions applied

## 🔧 Example Usage

```
Tool: generate_bem_field_names
Parameter: pdf_filename = "Life-1528-Q.pdf"
```

**Result:**
```
## Section-by-Section BEM Field Breakdown:

### 1. General Information (Owner's Information)
* owner-information_first-name
* owner-information_last-name
* owner-information_policy-number

### 3. Name Changes
* name-change_reason__marriage
* name-change_reason__divorce
* name-change_entity__primary-insured

### 9. Signatures
* signatures_owner
* signatures_owner-date
* signatures_joint-owner
```

## 🎯 Benefits

✅ **Always Available** - Tool appears in Claude Desktop's tool menu  
✅ **Repeatable Process** - Same workflow every time  
✅ **Proven Results** - Uses the exact prompt that gave great results  
✅ **No UI Maintenance** - Claude Desktop handles the interface  
✅ **Independent Operation** - Works with any PDF, anywhere

## 🔗 Integration with Other Tools

After generating BEM names, you can use them with other MCP tools:
- `modify_pdf_fields_v2` - Apply the generated names to rename PDF fields
- `preview_field_renames` - Preview changes before applying
- `extract_pdf_fields_enhanced` - Get detailed field information

## ⚠️ Troubleshooting

If the tool doesn't appear:
1. Restart Claude Desktop
2. Check MCP server logs
3. Verify configuration in claude_desktop_config.json

The tool is now ready to use! Upload a PDF and try it out.
