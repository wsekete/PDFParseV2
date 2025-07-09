#!/usr/bin/env python3
"""
Basic MCP Server Test
PDFParseV2 - Test MCP server functionality independently

This script tests the MCP server without requiring Claude Desktop.
"""

import sys
import os
import json
import traceback
from pathlib import Path

# Add project root to path
project_root = Path("/Users/wseke/Desktop/PDFParseV2")
sys.path.insert(0, str(project_root))

def test_imports():
    """Test if all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        # Test basic dependencies
        import PyPDF2
        print(f"✅ PyPDF2 v{PyPDF2.__version__}")
        
        # Test PyPDFForm (optional)
        try:
            from PyPDFForm import PdfWrapper
            print("✅ PyPDFForm available")
        except ImportError:
            print("⚠️  PyPDFForm not available (optional)")
        
        # Test MCP
        from mcp.server import Server
        from mcp.types import Tool, TextContent
        print("✅ MCP framework available")
        
        # Test other dependencies
        import pdfplumber
        import pandas
        import pydantic
        import loguru
        print("✅ All core dependencies available")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_mcp_server_module():
    """Test if the MCP server module can be loaded."""
    print("\n🚀 Testing MCP server module...")
    
    try:
        # Import the server module
        from src.pdf_modifier import mcp_server
        print("✅ MCP server module imported successfully")
        
        # Check for expected components
        if hasattr(mcp_server, 'app'):
            print("✅ MCP server app found")
        else:
            print("❌ MCP server app not found")
            return False
            
        if hasattr(mcp_server, 'test_connection'):
            print("✅ test_connection function found")
        else:
            print("❌ test_connection function not found")
            return False
            
        if hasattr(mcp_server, 'analyze_pdf_fields'):
            print("✅ analyze_pdf_fields function found")
        else:
            print("❌ analyze_pdf_fields function not found")
            return False
            
        if hasattr(mcp_server, 'modify_pdf_fields'):
            print("✅ modify_pdf_fields function found")
        else:
            print("❌ modify_pdf_fields function not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ MCP server module error: {e}")
        traceback.print_exc()
        return False

def test_mcp_tools():
    """Test individual MCP tools."""
    print("\n🔧 Testing MCP tools...")
    
    try:
        from src.pdf_modifier.mcp_server import test_connection, analyze_pdf_fields
        
        # Test connection tool
        print("Testing test_connection...")
        result = test_connection(include_version_info=True)
        if result:
            print("✅ test_connection works")
        else:
            print("❌ test_connection failed")
            return False
        
        # Test analyze_pdf_fields with a sample PDF
        sample_pdf = project_root / "training_data" / "pdf_csv_pairs" / "W-4R_parsed.pdf"
        if sample_pdf.exists():
            print(f"Testing analyze_pdf_fields with {sample_pdf.name}...")
            result = analyze_pdf_fields(str(sample_pdf), include_annotations=True)
            if result:
                print("✅ analyze_pdf_fields works")
            else:
                print("❌ analyze_pdf_fields failed")
                return False
        else:
            print("⚠️  Sample PDF not found, skipping analyze_pdf_fields test")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP tools test error: {e}")
        traceback.print_exc()
        return False

def test_pdf_field_renamer():
    """Test the PDFFieldRenamer class."""
    print("\n📄 Testing PDFFieldRenamer...")
    
    try:
        from src.pdf_modifier.mcp_server import PDFFieldRenamer
        
        # Test with sample PDF
        sample_pdf = project_root / "training_data" / "pdf_csv_pairs" / "W-4R_parsed.pdf"
        if sample_pdf.exists():
            print(f"Testing PDFFieldRenamer with {sample_pdf.name}...")
            
            with PDFFieldRenamer(str(sample_pdf)) as renamer:
                # Test form analysis
                analysis = renamer.analyze_form_structure()
                fields_count = len(analysis.get("form_fields", {}))
                print(f"✅ Found {fields_count} form fields")
                
                if fields_count > 0:
                    print("✅ PDFFieldRenamer works correctly")
                    return True
                else:
                    print("⚠️  No form fields found (may be normal for some PDFs)")
                    return True
        else:
            print("⚠️  Sample PDF not found, skipping PDFFieldRenamer test")
            return True
        
    except Exception as e:
        print(f"❌ PDFFieldRenamer test error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🔍 PDFParseV2 MCP Server Basic Test")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("MCP Server Module", test_mcp_server_module),
        ("MCP Tools", test_mcp_tools),
        ("PDF Field Renamer", test_pdf_field_renamer),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} - Exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MCP server is ready for Claude Desktop integration.")
        print("\nNext steps:")
        print("1. Run: python3 setup_claude_desktop.py")
        print("2. Restart Claude Desktop")
        print("3. Test tools in Claude Desktop")
    else:
        print("⚠️  Some tests failed. Fix issues before proceeding with Claude Desktop setup.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)