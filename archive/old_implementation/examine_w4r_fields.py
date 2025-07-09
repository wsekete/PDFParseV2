#!/usr/bin/env python3
"""
Examine W-4R PDF fields using different methods
Task 2.1.2 - Understanding actual field structure
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def examine_with_pypdfform():
    """Examine fields using PyPDFForm"""
    print("🔍 Examining W-4R PDF with PyPDFForm...")
    
    try:
        from PyPDFForm import PdfWrapper
        
        pdf_path = "training_data/pdf_csv_pairs/W-4R_parsed.pdf"
        pdf = PdfWrapper(pdf_path)
        
        # Method 1: sample_data
        sample_data = pdf.sample_data
        print(f"📊 sample_data found {len(sample_data)} fields:")
        for name, value in sample_data.items():
            print(f"  - {name}: {value}")
        
        # Method 2: Try to access schema
        try:
            schema = pdf.schema
            print(f"📊 schema found {len(schema)} fields:")
            for name, info in schema.items():
                print(f"  - {name}: {info}")
        except Exception as e:
            print(f"⚠️  schema not accessible: {e}")
        
        # Method 3: Try other attributes
        print(f"📋 PDF attributes:")
        for attr in dir(pdf):
            if not attr.startswith('_') and not callable(getattr(pdf, attr)):
                try:
                    value = getattr(pdf, attr)
                    if value is not None:
                        print(f"  - {attr}: {type(value)} = {str(value)[:100]}")
                except:
                    pass
        
        return sample_data
        
    except Exception as e:
        print(f"❌ PyPDFForm examination failed: {e}")
        return {}

def examine_with_pypdf2():
    """Examine fields using PyPDF2 for comparison"""
    print("\n🔍 Examining W-4R PDF with PyPDF2 for comparison...")
    
    try:
        import PyPDF2
        
        pdf_path = "training_data/pdf_csv_pairs/W-4R_parsed.pdf"
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # Check if form fields exist
            if reader.get_fields():
                fields = reader.get_fields()
                print(f"📊 PyPDF2 found {len(fields)} fields:")
                for name, field in fields.items():
                    print(f"  - {name}: {field}")
            else:
                print("⚠️  PyPDF2 found no form fields")
            
            # Check pages for annotations
            print(f"📄 PDF has {len(reader.pages)} pages")
            for i, page in enumerate(reader.pages):
                if '/Annots' in page:
                    annots = page['/Annots']
                    print(f"  Page {i+1}: {len(annots)} annotations")
                else:
                    print(f"  Page {i+1}: No annotations")
        
        return True
        
    except Exception as e:
        print(f"❌ PyPDF2 examination failed: {e}")
        return False

def examine_training_data():
    """Examine the expected fields from training data"""
    print("\n🔍 Examining expected fields from training data...")
    
    csv_path = "training_data/pdf_csv_pairs/W-4R_parsed_correct_mapping.csv"
    
    if not Path(csv_path).exists():
        print(f"⚠️  Training data not found: {csv_path}")
        return []
    
    try:
        import pandas as pd
        df = pd.read_csv(csv_path)
        
        print(f"📊 Training data has {len(df)} field records")
        print(f"📋 Columns: {list(df.columns)}")
        
        if 'Api name' in df.columns:
            api_names = df['Api name'].tolist()
            print(f"📊 Expected BEM field names ({len(api_names)}):")
            for name in api_names:
                print(f"  - {name}")
            return api_names
        
        if 'Acrofieldlabel' in df.columns:
            original_names = df['Acrofieldlabel'].tolist()
            print(f"📊 Original field names ({len(original_names)}):")
            for name in original_names:
                print(f"  - {name}")
            return original_names
            
        return []
        
    except Exception as e:
        print(f"❌ Training data examination failed: {e}")
        return []

def main():
    print("=" * 70)
    print("W-4R PDF Field Examination - Task 2.1.2")
    print("=" * 70)
    
    # Examine with different methods
    pypdfform_fields = examine_with_pypdfform()
    pypdf2_success = examine_with_pypdf2()
    expected_fields = examine_training_data()
    
    # Summary comparison
    print("\n" + "=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)
    
    print(f"PyPDFForm detected fields: {len(pypdfform_fields)}")
    print(f"PyPDF2 examination: {'Success' if pypdf2_success else 'Failed'}")
    print(f"Expected fields (training): {len(expected_fields)}")
    
    if pypdfform_fields and expected_fields:
        print(f"\n🔍 Field name comparison:")
        pypdfform_names = set(pypdfform_fields.keys())
        expected_names = set(expected_fields)
        
        common = pypdfform_names.intersection(expected_names)
        pypdfform_only = pypdfform_names - expected_names
        expected_only = expected_names - pypdfform_names
        
        print(f"  Common fields: {len(common)}")
        print(f"  PyPDFForm only: {len(pypdfform_only)}")
        print(f"  Expected only: {len(expected_only)}")
        
        if common:
            print(f"  ✅ Common fields: {list(common)[:3]}...")
        if pypdfform_only:
            print(f"  🔍 PyPDFForm extra: {list(pypdfform_only)[:3]}...")
        if expected_only:
            print(f"  ⚠️  Missing from PyPDFForm: {list(expected_only)[:3]}...")

if __name__ == "__main__":
    main()