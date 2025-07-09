#!/usr/bin/env python3
"""
Phase 1 Validation Script
Tests the current PDF modification implementation to validate claimed success rates.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_pypdfform_import():
    """Test PyPDFForm import and basic functionality."""
    try:
        from PyPDFForm import PdfWrapper
        print("✅ PyPDFForm imported successfully")
        return True
    except ImportError as e:
        print(f"❌ PyPDFForm import failed: {e}")
        return False

def test_mcp_server_import():
    """Test MCP server import."""
    try:
        from pdf_modifier.mcp_server import app, PDFFieldRenamer
        print("✅ MCP server imported successfully")
        return True
    except ImportError as e:
        print(f"❌ MCP server import failed: {e}")
        return False

def test_pypdfform_wrapper_import():
    """Test PyPDFForm wrapper import."""
    try:
        from pdf_modifier.pypdfform_field_renamer import PyPDFFormFieldRenamer
        print("✅ PyPDFForm wrapper imported successfully")
        return True
    except ImportError as e:
        print(f"❌ PyPDFForm wrapper import failed: {e}")
        return False

def test_sample_pdf_availability():
    """Test that sample PDFs are available for testing."""
    sample_dir = Path("training_data/pdf_csv_pairs")
    if not sample_dir.exists():
        print(f"❌ Sample directory not found: {sample_dir}")
        return False
    
    pdf_files = list(sample_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ No PDF files found in {sample_dir}")
        return False
    
    print(f"✅ Found {len(pdf_files)} sample PDFs")
    return True

def test_simple_field_extraction():
    """Test basic field extraction from a sample PDF."""
    try:
        from PyPDFForm import PdfWrapper
        
        # Try with W-4R PDF (simplest test case)
        sample_pdf = Path("training_data/pdf_csv_pairs/W-4R_parsed.pdf")
        if not sample_pdf.exists():
            print(f"❌ Sample PDF not found: {sample_pdf}")
            return False
        
        # Test basic PyPDFForm functionality
        pdf = PdfWrapper(str(sample_pdf))
        fields = pdf.sample_data
        
        print(f"✅ Successfully extracted {len(fields)} fields from W-4R PDF")
        
        # Show first few fields
        for i, (field_name, field_value) in enumerate(list(fields.items())[:3]):
            print(f"  - {field_name}: {field_value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Field extraction failed: {e}")
        return False

def main():
    """Run all Phase 1 validation tests."""
    print("=" * 60)
    print("PDFParseV2 - Phase 1 Validation")
    print("=" * 60)
    
    tests = [
        ("PyPDFForm Import", test_pypdfform_import),
        ("MCP Server Import", test_mcp_server_import),
        ("PyPDFForm Wrapper Import", test_pypdfform_wrapper_import),
        ("Sample PDF Availability", test_sample_pdf_availability),
        ("Simple Field Extraction", test_simple_field_extraction)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Phase 1 validation SUCCESSFUL!")
        return 0
    else:
        print("❌ Phase 1 validation FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())