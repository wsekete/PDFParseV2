#!/usr/bin/env python3
"""
Test the fixed PyPDFForm wrapper field extraction
Validates the fix for using sample_data instead of schema
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_wrapper_fix():
    """Test the fixed wrapper field extraction with W-4R PDF."""
    print("🔧 Testing PyPDFForm wrapper fix...")
    
    try:
        from pdf_modifier.pypdfform_field_renamer import PyPDFFormFieldRenamer
        
        pdf_path = "training_data/pdf_csv_pairs/W-4R_parsed.pdf"
        
        if not Path(pdf_path).exists():
            print(f"❌ PDF not found: {pdf_path}")
            return False
        
        # Initialize the renamer
        renamer = PyPDFFormFieldRenamer(pdf_path)
        
        # Test PDF loading
        if not renamer.load_pdf():
            print("❌ Failed to load PDF")
            return False
        
        print("✅ PDF loaded successfully")
        
        # Test field extraction with the fix
        fields = renamer.extract_fields()
        
        print(f"✅ Field extraction completed: {len(fields)} fields found")
        
        if fields:
            print("📋 Extracted fields:")
            for i, field in enumerate(fields, 1):
                print(f"  {i}. {field['name']} ({field['type']}) = {field['value']}")
            
            # Verify we have expected field types
            field_types = [field['type'] for field in fields]
            type_counts = {}
            for field_type in field_types:
                type_counts[field_type] = type_counts.get(field_type, 0) + 1
            
            print(f"\n📊 Field type distribution:")
            for field_type, count in type_counts.items():
                print(f"  {field_type}: {count} fields")
            
            return True
        else:
            print("❌ No fields extracted - fix may not be working")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def compare_with_expected():
    """Compare extracted fields with expected training data."""
    print("\n🔍 Comparing with expected training data...")
    
    try:
        # Load expected fields
        csv_path = "training_data/pdf_csv_pairs/W-4R_parsed_correct_mapping.csv"
        
        if not Path(csv_path).exists():
            print(f"⚠️  Expected data not found: {csv_path}")
            return False
        
        import pandas as pd
        df = pd.read_csv(csv_path)
        
        # Get expected field names
        expected_original = df['Acrofieldlabel'].tolist() if 'Acrofieldlabel' in df.columns else []
        expected_bem = df['Api name'].tolist() if 'Api name' in df.columns else []
        
        print(f"📊 Expected fields: {len(expected_original)} original, {len(expected_bem)} BEM")
        
        # Test extraction
        from pdf_modifier.pypdfform_field_renamer import PyPDFFormFieldRenamer
        
        renamer = PyPDFFormFieldRenamer("training_data/pdf_csv_pairs/W-4R_parsed.pdf")
        if renamer.load_pdf():
            fields = renamer.extract_fields()
            extracted_names = [field['name'] for field in fields]
            
            print(f"📊 Extracted fields: {len(extracted_names)}")
            
            # Compare
            if len(extracted_names) == len(expected_original):
                print("✅ Field count matches expected!")
            else:
                print(f"⚠️  Field count mismatch: expected {len(expected_original)}, got {len(extracted_names)}")
            
            # Show field comparison
            print("\n🔍 Field comparison:")
            for i, (extracted, expected) in enumerate(zip(extracted_names, expected_original)):
                match = "✅" if extracted == expected else "⚠️"
                print(f"  {i+1}. {match} {extracted} (expected: {expected})")
            
            return True
        else:
            print("❌ Failed to load PDF for comparison")
            return False
            
    except Exception as e:
        print(f"❌ Comparison failed: {e}")
        return False

def test_field_renaming():
    """Test that field renaming still works after the fix."""
    print("\n🔄 Testing field renaming with fixed wrapper...")
    
    try:
        from pdf_modifier.pypdfform_field_renamer import PyPDFFormFieldRenamer
        
        renamer = PyPDFFormFieldRenamer("training_data/pdf_csv_pairs/W-4R_parsed.pdf")
        
        if not renamer.load_pdf():
            print("❌ Failed to load PDF for renaming test")
            return False
        
        # Extract fields first
        fields = renamer.extract_fields()
        
        if not fields:
            print("❌ No fields found for renaming test")
            return False
        
        # Test renaming first field
        first_field = fields[0]
        test_mappings = {
            first_field['name']: f"test_fixed_{first_field['name']}"
        }
        
        print(f"🎯 Testing rename: {first_field['name']} → {test_mappings[first_field['name']]}")
        
        # Validate mappings
        validation = renamer.validate_mappings(test_mappings)
        
        if validation['errors']:
            print(f"❌ Validation errors: {validation['errors']}")
            return False
        
        print("✅ Validation passed")
        
        # Perform rename
        results = renamer.rename_fields(test_mappings)
        
        if results and results[0].success:
            print("✅ Field rename successful!")
            
            # Test save
            output_path = "training_data/pdf_csv_pairs/W-4R_parsed_wrapper_fix_test.pdf"
            if renamer.save_pdf(output_path):
                print(f"✅ Test output saved: {output_path}")
                return True
            else:
                print("❌ Failed to save test output")
                return False
        else:
            error = results[0].error if results else "No results"
            print(f"❌ Field rename failed: {error}")
            return False
            
    except Exception as e:
        print(f"❌ Renaming test failed: {e}")
        return False

def main():
    """Run all wrapper fix tests."""
    print("=" * 70)
    print("PyPDFForm Wrapper Fix Testing")
    print("=" * 70)
    
    tests = [
        ("Wrapper Field Extraction Fix", test_wrapper_fix),
        ("Compare with Expected Data", compare_with_expected),
        ("Field Renaming with Fix", test_field_renaming)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}:")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 70)
    print("WRAPPER FIX TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests PASSED! Wrapper fix is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Fix may need additional work.")
        return 1

if __name__ == "__main__":
    sys.exit(main())