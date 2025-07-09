#!/usr/bin/env python3
"""Quick validation of the wrapper fix"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    print("Testing fixed wrapper...")
    
    from pdf_modifier.pypdfform_field_renamer import PyPDFFormFieldRenamer
    
    # Test with W-4R PDF
    renamer = PyPDFFormFieldRenamer("training_data/pdf_csv_pairs/W-4R_parsed.pdf")
    
    if renamer.load_pdf():
        print("✅ PDF loaded")
        
        fields = renamer.extract_fields()
        print(f"✅ Extracted {len(fields)} fields")
        
        if fields:
            print("📋 Fields found:")
            for field in fields[:5]:  # Show first 5
                print(f"  - {field['name']} ({field['type']})")
            
            print("✅ Wrapper fix is working!")
        else:
            print("❌ No fields extracted")
    else:
        print("❌ Failed to load PDF")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()