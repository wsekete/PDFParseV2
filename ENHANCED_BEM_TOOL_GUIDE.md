# Enhanced BEM Field Naming Tool - Quick Start Guide

## ✅ Updates Complete! 

Your MCP server has been enhanced with the improved **BEM Field Naming Tool** that includes:
- ✅ Field types in output
- ✅ Proper radio group handling with --group suffix
- ✅ Cleaner output (no JSON clutter)

## 🚀 How to Use

### Step 1: Restart Claude Desktop
After any MCP server changes, restart Claude Desktop to load the enhanced tool.

### Step 2: Upload PDF
- Upload your PDF form to Claude Desktop using drag & drop or the attachment button
- Note the exact filename (e.g., "Life-1528-Q.pdf")

### Step 3: Use the Enhanced Tool
In Claude Desktop, you'll see the enhanced tool in the tools menu:
- **🚀 generate_bem_field_names** - Generate BEM field names with field types and radio group handling

### Step 4: Get Enhanced Results
1. Call the tool with the PDF filename
2. Get section-by-section BEM field breakdown **with field types**
3. See proper radio group handling with **--group suffix**

## 📋 Enhanced Tool Details

**Tool Name:** `generate_bem_field_names`

**Parameters:**
- `pdf_filename` (required) - Name of uploaded PDF file

**Enhanced Output:**
- Field types in parentheses: `(TextField)`, `(Checkbox)`, `(RadioButton)`, etc.
- Radio group containers: `name-change_reason--group (RadioGroup)`
- Individual radio options: `name-change_reason__marriage (RadioButton)`
- **No JSON output** for cleaner, more focused results

## 🔧 Example Usage

```
Tool: generate_bem_field_names
Parameter: pdf_filename = "Life-1528-Q.pdf"
```

**Enhanced Result:**
```
## Section-by-Section BEM Field Breakdown:

### 1. General Information (Owner's Information)
* owner-information_first-name (TextField)
* owner-information_last-name (TextField)
* owner-information_policy-number (TextField)

### 1. General Information (Insured's Information)
* insured-information_same-as-owner (Checkbox)

### 3. Name Changes
* name-change_entity--group (RadioGroup)
* name-change_entity__primary-insured (RadioButton)
* name-change_entity__payor (RadioButton)
* name-change_entity__owner (RadioButton)
* name-change_reason--group (RadioGroup)
* name-change_reason__marriage (RadioButton)
* name-change_reason__divorce (RadioButton)
* name-change_former-name (TextField)
* name-change_present-name (TextField)

### 9. Signatures
* signatures_owner (TextField)
* signatures_owner-signature (Signature)
* signatures_owner-date (DateField)
```

## 🎯 Enhanced Benefits

✅ **Field Type Clarity** - See exactly what type each field is  
✅ **Radio Group Handling** - Proper --group containers + individual options  
✅ **Cleaner Output** - No JSON clutter, just the field breakdown  
✅ **Always Available** - Tool permanently in Claude Desktop menu  
✅ **Proven Results** - Uses exact prompt that gave perfect results  
✅ **Universal** - Works with any PDF form

## 🔧 Field Types Recognized

- **TextField** - Text input fields
- **Checkbox** - Individual checkboxes  
- **RadioGroup** - Container for radio button groups (--group suffix)
- **RadioButton** - Individual radio button options
- **Signature** - Signature fields
- **DateField** - Date input fields

## 🔗 Integration with Other Tools

After generating enhanced BEM names, you can use them with other MCP tools:
- `modify_pdf_fields_v2` - Apply the generated names to rename PDF fields
- `preview_field_renames` - Preview changes before applying
- `extract_pdf_fields_enhanced` - Get detailed field information

## ⚠️ Troubleshooting

If the tool doesn't appear:
1. Restart Claude Desktop
2. Check MCP server logs
3. Verify configuration in claude_desktop_config.json

## 🚀 Ready to Test!

The enhanced tool is now ready! Try it with any PDF:
1. Upload a PDF to Claude Desktop
2. Use the `generate_bem_field_names` tool
3. See the improved output with field types and radio group handling

The enhancements provide much clearer, more actionable field naming results that are easier to work with.
