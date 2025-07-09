#!/usr/bin/env python3
"""Direct test of PyPDFForm with W-4R PDF"""

try:
    print("Testing PyPDFForm import...")
    from PyPDFForm import PdfWrapper
    print("✅ PyPDFForm imported")
    
    print("Loading W-4R PDF...")
    pdf = PdfWrapper("training_data/pdf_csv_pairs/W-4R_parsed.pdf")
    print("✅ PDF loaded")
    
    print("Getting sample_data...")
    data = pdf.sample_data
    print(f"✅ Found {len(data)} fields")
    
    print("Fields:")
    for name, value in data.items():
        print(f"  {name}: {value}")
    
    print("Testing field rename...")
    if data:
        first_field = list(data.keys())[0]
        new_name = f"test_{first_field}"
        print(f"Renaming {first_field} to {new_name}")
        
        updated_pdf = pdf.update_widget_key(first_field, new_name)
        print("✅ Rename operation completed")
        
        # Check new fields
        new_data = updated_pdf.sample_data
        print(f"After rename: {len(new_data)} fields")
        
        if new_name in new_data and first_field not in new_data:
            print("✅ Rename successful!")
        else:
            print("⚠️ Rename verification unclear")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()