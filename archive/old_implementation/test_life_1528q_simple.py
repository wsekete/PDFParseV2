#!/usr/bin/env python3
"""Simple test for LIFE-1528-Q PDF with fixed wrapper"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_life_1528q():
    print("Testing LIFE-1528-Q PDF with PyPDFForm and fixed wrapper...")
    
    pdf_path = "training_data/pdf_csv_pairs/LIFE-1528-Q__parsed.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        return False
    
    # Test 1: Basic PyPDFForm
    try:
        from PyPDFForm import PdfWrapper
        pdf = PdfWrapper(pdf_path)
        sample_data = pdf.sample_data
        
        print(f"✅ PyPDFForm detected {len(sample_data)} fields")
        
        # Show first few fields
        for i, (name, value) in enumerate(list(sample_data.items())[:5]):
            print(f"  {i+1}. {name} = {value}")
        
        # Count RadioGroup-like fields
        radio_groups = [name for name in sample_data.keys() if name.endswith('--group')]
        radio_buttons = [name for name in sample_data.keys() if '--' in name and not name.endswith('--group')]
        
        print(f"  RadioGroups: {len(radio_groups)}")
        print(f"  RadioButtons: {len(radio_buttons)}")
        
    except Exception as e:
        print(f"❌ PyPDFForm test failed: {e}")
        return False
    
    # Test 2: Fixed wrapper
    try:
        from pdf_modifier.pypdfform_field_renamer import PyPDFFormFieldRenamer
        
        renamer = PyPDFFormFieldRenamer(pdf_path)
        
        if renamer.load_pdf():
            fields = renamer.extract_fields()
            print(f"✅ Wrapper detected {len(fields)} fields")
            
            # Check field types
            type_counts = {}
            for field in fields:
                field_type = field['type']
                type_counts[field_type] = type_counts.get(field_type, 0) + 1
            
            print(f"  Field types:")
            for field_type, count in type_counts.items():
                print(f"    {field_type}: {count}")
            
            return True
        else:
            print("❌ Wrapper failed to load PDF")
            return False
            
    except Exception as e:
        print(f"❌ Wrapper test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_life_1528q()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1)