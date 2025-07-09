#!/usr/bin/env python3
"""
Simple PyPDFForm test for Task 2.1.2
Tests basic functionality with W-4R PDF
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_pypdfform():
    print("Testing PyPDFForm with W-4R PDF...")
    
    try:
        from PyPDFForm import PdfWrapper
        print("✅ PyPDFForm imported successfully")
    except ImportError as e:
        print(f"❌ PyPDFForm import failed: {e}")
        return False
    
    # Test with W-4R PDF
    pdf_path = "training_data/pdf_csv_pairs/W-4R_parsed.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        return False
    
    try:
        pdf = PdfWrapper(pdf_path)
        print("✅ PDF loaded successfully")
        
        # Get field data
        sample_data = pdf.sample_data
        print(f"✅ Found {len(sample_data)} fields")
        
        # Show first few fields
        for i, (name, value) in enumerate(list(sample_data.items())[:3]):
            print(f"  Field {i+1}: {name} = {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ PyPDFForm test failed: {e}")
        return False

def test_wrapper():
    print("\nTesting PyPDFForm wrapper...")
    
    try:
        from pdf_modifier.pypdfform_field_renamer import PyPDFFormFieldRenamer
        print("✅ Wrapper imported successfully")
    except ImportError as e:
        print(f"❌ Wrapper import failed: {e}")
        return False
    
    pdf_path = "training_data/pdf_csv_pairs/W-4R_parsed.pdf"
    
    try:
        renamer = PyPDFFormFieldRenamer(pdf_path)
        
        if renamer.load_pdf():
            print("✅ PDF loaded with wrapper")
            
            fields = renamer.extract_fields()
            print(f"✅ Extracted {len(fields)} fields with wrapper")
            
            return True
        else:
            print("❌ Failed to load PDF with wrapper")
            return False
            
    except Exception as e:
        print(f"❌ Wrapper test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("PyPDFForm Simple Test - Task 2.1.2")
    print("=" * 50)
    
    test1 = test_pypdfform()
    test2 = test_wrapper()
    
    print(f"\nResults: PyPDFForm={test1}, Wrapper={test2}")
    
    if test1 and test2:
        print("🎉 Basic tests PASSED!")
    else:
        print("❌ Some tests FAILED!")