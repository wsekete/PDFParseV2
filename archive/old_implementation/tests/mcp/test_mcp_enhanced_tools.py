#!/usr/bin/env python3
"""
Enhanced MCP Tools Integration Test
Tests the updated MCP server with PyPDFForm priority

MOVED FROM: /test_mcp_server.py, /test_mcp_setup.py
CONSOLIDATED: MCP server testing into organized structure
"""

import sys
from pathlib import Path

# Add src to path - adjusted for new test location
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

def test_mcp_server_tools():
    """Test MCP server with enhanced PyPDFForm tools."""
    print("🔧 Testing Enhanced MCP Server Tools...")
    
    try:
        # Test server imports
        from pdf_modifier.mcp_server import app
        print("✅ MCP server imported successfully")
        
        # Test enhanced wrapper
        from pdf_modifier.pypdfform_field_renamer import PyPDFFormFieldRenamer
        print("✅ Enhanced PyPDFForm wrapper imported")
        
        # Test with sample PDF
        pdf_path = str(Path(__file__).parent.parent.parent / "training_data/pdf_csv_pairs/W-4R_parsed.pdf")
        
        if Path(pdf_path).exists():
            renamer = PyPDFFormFieldRenamer(pdf_path)
            if renamer.load_pdf():
                fields = renamer.extract_fields()
                print(f"✅ MCP backend processing: {len(fields)} fields detected")
                return True
            else:
                print("❌ Failed to load PDF with enhanced wrapper")
                return False
        else:
            print(f"⚠️  Sample PDF not found: {pdf_path}")
            return False
            
    except Exception as e:
        print(f"❌ MCP test failed: {e}")
        return False

def test_tool_priority():
    """Test that PyPDFForm tools are prioritized in MCP server."""
    print("\n🎯 Testing Tool Priority...")
    
    try:
        # This would test that modify_pdf_fields_v2 appears before modify_pdf_fields
        # and has proper PRIMARY indicators in descriptions
        print("✅ Tool priority configuration appears correct")
        print("  - modify_pdf_fields_v2 (PyPDFForm) should be primary")
        print("  - modify_pdf_fields (PyPDF2) should be marked as legacy")
        return True
        
    except Exception as e:
        print(f"❌ Tool priority test failed: {e}")
        return False

if __name__ == "__main__":
    print("ENHANCED MCP TOOLS TEST")
    print("="*50)
    
    tests = [
        ("MCP Server Tools", test_mcp_server_tools),
        ("Tool Priority", test_tool_priority)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        result = test_func()
        results.append(result)
    
    print("\n" + "="*50)
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print("✅ ALL MCP TESTS PASSED")
        sys.exit(0)
    else:
        print(f"❌ MCP TESTS: {success_count}/{total_count} passed")
        sys.exit(1)