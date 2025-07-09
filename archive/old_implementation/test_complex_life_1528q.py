#!/usr/bin/env python3
"""
Test PyPDFForm implementation with complex LIFE-1528-Q PDF
Task 2.1.3 - Complex PDF testing with RadioGroups

This script tests the fixed PyPDFForm implementation with the LIFE-1528-Q PDF
which contains complex RadioGroup and RadioButton structures.
"""

import sys
import os
import time
from pathlib import Path
from typing import Dict, List, Any

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def analyze_expected_structure():
    """Analyze the expected structure of LIFE-1528-Q PDF."""
    print("🔍 Analyzing expected LIFE-1528-Q structure...")
    
    csv_path = "training_data/pdf_csv_pairs/LIFE-1528-Q__parsed_correct_mapping.csv"
    
    if not Path(csv_path).exists():
        print(f"❌ Expected data not found: {csv_path}")
        return {}
    
    try:
        import pandas as pd
        df = pd.read_csv(csv_path)
        
        total_fields = len(df)
        print(f"📊 Total expected fields: {total_fields}")
        
        # Analyze field types
        field_types = df['Type'].value_counts()
        print(f"📋 Field type distribution:")
        for field_type, count in field_types.items():
            print(f"  {field_type}: {count} fields")
        
        # Analyze the RadioGroup structure
        radio_groups = df[df['Type'] == 'RadioGroup']
        radio_buttons = df[df['Type'] == 'RadioButton']
        
        print(f"\n🔘 RadioGroup analysis:")
        print(f"  RadioGroups: {len(radio_groups)}")
        print(f"  RadioButtons: {len(radio_buttons)}")
        
        if len(radio_groups) > 0:
            print(f"  RadioGroup names:")
            for _, group in radio_groups.iterrows():
                print(f"    - {group['Acrofieldlabel']} → {group['Api name']}")
        
        # Show RadioButton parent relationships
        if len(radio_buttons) > 0:
            print(f"  RadioButton parent relationships:")
            for _, button in radio_buttons.iterrows():
                parent_id = button['Parent ID']
                parent_row = df[df['ID'] == parent_id]
                parent_name = parent_row['Api name'].iloc[0] if len(parent_row) > 0 else 'Unknown'
                print(f"    - {button['Api name']} → parent: {parent_name}")
        
        # Extract all field names for comparison
        expected_fields = {
            'original_names': df['Acrofieldlabel'].tolist(),
            'bem_names': df['Api name'].tolist(),
            'field_types': df['Type'].tolist(),
            'parent_relationships': df[['Api name', 'Type', 'Parent ID']].to_dict('records')
        }
        
        return expected_fields
        
    except Exception as e:
        print(f"❌ Failed to analyze expected structure: {e}")
        return {}

def test_pypdfform_with_complex_pdf():
    """Test PyPDFForm with the complex LIFE-1528-Q PDF."""
    print("\n🧪 Testing PyPDFForm with LIFE-1528-Q PDF...")
    
    pdf_path = "training_data/pdf_csv_pairs/LIFE-1528-Q__parsed.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        return False, [], {}
    
    try:
        from PyPDFForm import PdfWrapper
        
        # Test basic PyPDFForm functionality
        pdf = PdfWrapper(pdf_path)
        sample_data = pdf.sample_data
        
        print(f"✅ PyPDFForm loaded PDF: {len(sample_data)} fields detected")
        
        # Analyze detected fields
        field_analysis = {
            'total_fields': len(sample_data),
            'field_names': list(sample_data.keys()),
            'field_values': sample_data,
            'field_types': {}
        }
        
        # Simple field type detection
        for field_name in sample_data.keys():
            if field_name.endswith('--group'):
                field_analysis['field_types'][field_name] = 'RadioGroup'
            elif '--' in field_name and not field_name.endswith('--group'):
                field_analysis['field_types'][field_name] = 'RadioButton'
            else:
                field_analysis['field_types'][field_name] = 'TextField'
        
        # Show first 10 fields
        print(f"📋 First 10 detected fields:")
        for i, (name, value) in enumerate(list(sample_data.items())[:10]):
            field_type = field_analysis['field_types'].get(name, 'Unknown')
            print(f"  {i+1}. {name} ({field_type}) = {value}")
        
        if len(sample_data) > 10:
            print(f"  ... and {len(sample_data) - 10} more fields")
        
        return True, list(sample_data.keys()), field_analysis
        
    except Exception as e:
        print(f"❌ PyPDFForm test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, [], {}

def test_wrapper_with_complex_pdf():
    """Test the fixed wrapper with complex LIFE-1528-Q PDF."""
    print("\n🧪 Testing fixed wrapper with LIFE-1528-Q PDF...")
    
    pdf_path = "training_data/pdf_csv_pairs/LIFE-1528-Q__parsed.pdf"
    
    try:
        from pdf_modifier.pypdfform_field_renamer import PyPDFFormFieldRenamer
        
        # Initialize the renamer
        renamer = PyPDFFormFieldRenamer(pdf_path)
        
        # Test PDF loading
        if not renamer.load_pdf():
            print("❌ Failed to load PDF with wrapper")
            return False, []
        
        print("✅ PDF loaded successfully with wrapper")
        
        # Test field extraction with the fix
        fields = renamer.extract_fields()
        print(f"✅ Field extraction completed: {len(fields)} fields found")
        
        # Analyze field types detected by wrapper
        type_counts = {}
        for field in fields:
            field_type = field['type']
            type_counts[field_type] = type_counts.get(field_type, 0) + 1
        
        print(f"📊 Field type distribution (wrapper):")
        for field_type, count in type_counts.items():
            print(f"  {field_type}: {count} fields")
        
        # Show RadioGroup and RadioButton fields specifically
        radio_groups = [f for f in fields if f['type'] == 'RadioGroup']
        radio_buttons = [f for f in fields if f['type'] == 'RadioButton']
        
        print(f"\n🔘 RadioGroup/RadioButton analysis:")
        print(f"  RadioGroups detected: {len(radio_groups)}")
        print(f"  RadioButtons detected: {len(radio_buttons)}")
        
        if radio_groups:
            print(f"  RadioGroup names:")
            for group in radio_groups:
                print(f"    - {group['name']}")
        
        if radio_buttons:
            print(f"  RadioButton names (first 5):")
            for button in radio_buttons[:5]:
                print(f"    - {button['name']}")
        
        return True, fields
        
    except Exception as e:
        print(f"❌ Wrapper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, []

def compare_detection_results(expected, pypdfform_fields, wrapper_fields):
    """Compare detection results between expected, PyPDFForm, and wrapper."""
    print("\n📊 Comparing detection results...")
    
    expected_count = len(expected.get('original_names', []))
    pypdfform_count = len(pypdfform_fields)
    wrapper_count = len(wrapper_fields)
    
    print(f"Field counts:")
    print(f"  Expected: {expected_count}")
    print(f"  PyPDFForm: {pypdfform_count}")
    print(f"  Wrapper: {wrapper_count}")
    
    # Check if counts match
    if pypdfform_count == expected_count:
        print("✅ PyPDFForm field count matches expected!")
    else:
        print(f"⚠️  PyPDFForm field count mismatch: expected {expected_count}, got {pypdfform_count}")
    
    if wrapper_count == expected_count:
        print("✅ Wrapper field count matches expected!")
    else:
        print(f"⚠️  Wrapper field count mismatch: expected {expected_count}, got {wrapper_count}")
    
    # Type analysis
    expected_types = expected.get('field_types', [])
    if expected_types:
        expected_type_counts = {}
        for field_type in expected_types:
            expected_type_counts[field_type] = expected_type_counts.get(field_type, 0) + 1
        
        print(f"\nExpected field types:")
        for field_type, count in expected_type_counts.items():
            print(f"  {field_type}: {count}")

def test_field_renaming_complex():
    """Test field renaming with complex RadioGroup structure."""
    print("\n🔄 Testing field renaming with complex PDF...")
    
    try:
        from pdf_modifier.pypdfform_field_renamer import PyPDFFormFieldRenamer
        
        renamer = PyPDFFormFieldRenamer("training_data/pdf_csv_pairs/LIFE-1528-Q__parsed.pdf")
        
        if not renamer.load_pdf():
            print("❌ Failed to load PDF for renaming test")
            return False
        
        # Extract fields
        fields = renamer.extract_fields()
        
        if not fields:
            print("❌ No fields found for renaming test")
            return False
        
        # Test renaming a RadioGroup field
        radio_groups = [f for f in fields if f['type'] == 'RadioGroup']
        if radio_groups:
            test_field = radio_groups[0]
            print(f"🎯 Testing RadioGroup rename: {test_field['name']}")
            
            test_mappings = {
                test_field['name']: f"test_complex_{test_field['name']}"
            }
            
            # Validate mappings
            validation = renamer.validate_mappings(test_mappings)
            
            if validation['errors']:
                print(f"❌ Validation errors: {validation['errors']}")
                return False
            
            print("✅ RadioGroup rename validation passed")
            
            # Perform rename
            results = renamer.rename_fields(test_mappings)
            
            if results and results[0].success:
                print("✅ RadioGroup rename successful!")
                
                # Save test output
                output_path = "training_data/pdf_csv_pairs/LIFE-1528-Q__parsed_complex_test.pdf"
                if renamer.save_pdf(output_path):
                    print(f"✅ Complex test output saved: {output_path}")
                    return True
                else:
                    print("❌ Failed to save complex test output")
                    return False
            else:
                error = results[0].error if results else "No results"
                print(f"❌ RadioGroup rename failed: {error}")
                return False
        else:
            print("⚠️  No RadioGroups found for renaming test")
            return False
            
    except Exception as e:
        print(f"❌ Complex renaming test failed: {e}")
        return False

def main():
    """Run all complex PDF tests."""
    print("=" * 80)
    print("PyPDFForm Complex PDF Testing - Task 2.1.3")
    print("Testing with LIFE-1528-Q PDF (RadioGroups)")
    print("=" * 80)
    
    start_time = time.time()
    test_results = {}
    
    # Test 1: Analyze expected structure
    expected_data = analyze_expected_structure()
    test_results['expected_analysis'] = len(expected_data) > 0
    
    # Test 2: PyPDFForm basic functionality
    pypdfform_success, pypdfform_fields, pypdfform_analysis = test_pypdfform_with_complex_pdf()
    test_results['pypdfform_basic'] = pypdfform_success
    
    # Test 3: Wrapper functionality
    wrapper_success, wrapper_fields = test_wrapper_with_complex_pdf()
    test_results['wrapper_functionality'] = wrapper_success
    
    # Test 4: Compare results
    if expected_data and pypdfform_fields and wrapper_fields:
        compare_detection_results(expected_data, pypdfform_fields, wrapper_fields)
    
    # Test 5: Complex field renaming
    test_results['complex_renaming'] = test_field_renaming_complex()
    
    # Summary
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("COMPLEX PDF TEST SUMMARY")
    print("=" * 80)
    
    total_tests = 0
    passed_tests = 0
    
    for test_name, result in test_results.items():
        if isinstance(result, bool):
            total_tests += 1
            if result:
                passed_tests += 1
                print(f"✅ PASS: {test_name}")
            else:
                print(f"❌ FAIL: {test_name}")
    
    print(f"\n📊 Results Summary:")
    print(f"   Tests passed: {passed_tests}/{total_tests}")
    print(f"   Success rate: {(passed_tests/total_tests)*100:.1f}%")
    print(f"   Test duration: {elapsed_time:.2f} seconds")
    
    if expected_data:
        print(f"   Expected fields: {len(expected_data.get('original_names', []))}")
    if pypdfform_fields:
        print(f"   PyPDFForm detected: {len(pypdfform_fields)}")
    if wrapper_fields:
        print(f"   Wrapper detected: {len(wrapper_fields)}")
    
    # Final assessment
    if passed_tests == total_tests:
        print("\n🎉 All complex PDF tests PASSED!")
        print("✅ PyPDFForm handles RadioGroups and complex structures successfully!")
        return 0
    elif passed_tests >= total_tests * 0.7:
        print("\n⚠️  Most tests passed, but some complex features may need work.")
        return 1
    else:
        print("\n❌ Major issues with complex PDF handling detected.")
        return 2

if __name__ == "__main__":
    sys.exit(main())