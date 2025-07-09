#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def main():
    print("Testing PyPDFForm with all training PDFs...")
    
    # Test imports
    try:
        from PyPDFForm import PdfWrapper
        print("✅ PyPDFForm imported successfully")
    except Exception as e:
        print(f"❌ PyPDFForm import failed: {e}")
        return 1
    
    try:
        from pdf_modifier.pypdfform_field_renamer import PyPDFFormFieldRenamer
        print("✅ PyPDFFormFieldRenamer imported successfully")
    except Exception as e:
        print(f"❌ PyPDFFormFieldRenamer import failed: {e}")
        return 1
    
    # Get training PDFs
    pairs_dir = Path("training_data/pdf_csv_pairs")
    pdf_files = list(pairs_dir.glob("*_parsed.pdf"))
    
    # Filter out test files
    clean_pdfs = []
    for pdf in pdf_files:
        if not any(skip in pdf.name for skip in ['backup', 'test', 'renamed']):
            clean_pdfs.append(pdf)
    
    print(f"\n📊 Found {len(clean_pdfs)} training PDFs:")
    for pdf in clean_pdfs:
        print(f"  - {pdf.name}")
    
    # Test each PDF
    results = []
    for pdf_path in clean_pdfs:
        print(f"\n📄 Testing {pdf_path.name}...")
        
        try:
            # Test PyPDFForm basic
            pdf = PdfWrapper(str(pdf_path))
            sample_data = pdf.sample_data
            
            if sample_data:
                print(f"  ✅ PyPDFForm: {len(sample_data)} fields detected")
                
                # Test wrapper
                renamer = PyPDFFormFieldRenamer(str(pdf_path))
                if renamer.load_pdf():
                    fields = renamer.extract_fields()
                    print(f"  ✅ Wrapper: {len(fields)} fields extracted")
                    
                    # Count field types
                    type_counts = {}
                    for field in fields:
                        field_type = field['type']
                        type_counts[field_type] = type_counts.get(field_type, 0) + 1
                    
                    print(f"  📊 Field types: {type_counts}")
                    
                    results.append({
                        'name': pdf_path.name,
                        'success': True,
                        'pypdfform_count': len(sample_data),
                        'wrapper_count': len(fields),
                        'field_types': type_counts
                    })
                else:
                    print(f"  ❌ Wrapper failed to load PDF")
                    results.append({'name': pdf_path.name, 'success': False, 'error': 'Wrapper load failed'})
            else:
                print(f"  ❌ PyPDFForm: No sample_data")
                results.append({'name': pdf_path.name, 'success': False, 'error': 'No sample_data'})
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append({'name': pdf_path.name, 'success': False, 'error': str(e)})
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"📈 Overall Success Rate: {successful}/{total} ({(successful/total)*100:.1f}%)")
    
    for result in results:
        if result['success']:
            print(f"✅ {result['name']}: {result['wrapper_count']} fields")
        else:
            print(f"❌ {result['name']}: {result['error']}")
    
    return 0 if successful == total else 1

if __name__ == "__main__":
    sys.exit(main())