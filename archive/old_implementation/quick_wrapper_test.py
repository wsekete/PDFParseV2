#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

# Test basic import and functionality
try:
    from pdf_modifier.pypdfform_field_renamer import PyPDFFormFieldRenamer
    print("✅ Enhanced wrapper imported successfully")
    
    # Test with LIFE-1528-Q
    pdf_path = "training_data/pdf_csv_pairs/LIFE-1528-Q__parsed.pdf"
    
    if Path(pdf_path).exists():
        print(f"📄 Testing with: {pdf_path}")
        renamer = PyPDFFormFieldRenamer(pdf_path)
        
        if renamer.load_pdf():
            print("✅ PDF loaded")
            fields = renamer.extract_fields()
            print(f"📊 Fields extracted: {len(fields)}")
            
            # Count field types
            type_counts = {}
            for field in fields:
                field_type = field['type']
                type_counts[field_type] = type_counts.get(field_type, 0) + 1
            
            print("Field types:")
            for field_type, count in type_counts.items():
                print(f"  {field_type}: {count}")
            
            # Show RadioGroups specifically
            radio_groups = [f for f in fields if f['type'] == 'RadioGroup']
            if radio_groups:
                print("RadioGroups found:")
                for rg in radio_groups:
                    print(f"  - {rg['name']}")
            else:
                print("❌ No RadioGroups detected")
                
        else:
            print("❌ Failed to load PDF")
    else:
        print(f"❌ PDF not found: {pdf_path}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()