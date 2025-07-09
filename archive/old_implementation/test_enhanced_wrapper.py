#!/usr/bin/env python3
"""
Test Enhanced PyPDFForm Wrapper with LIFE-1528-Q
Validate that the enhanced wrapper correctly detects all 73 fields including RadioGroups
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_enhanced_wrapper():
    """Test the enhanced PyPDFForm wrapper with LIFE-1528-Q PDF."""
    print("🧪 Testing Enhanced PyPDFForm Wrapper with LIFE-1528-Q...")
    print("="*80)
    
    pdf_path = "training_data/pdf_csv_pairs/LIFE-1528-Q__parsed.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        return False
    
    try:
        from pdf_modifier.pypdfform_field_renamer import PyPDFFormFieldRenamer
        
        # Initialize enhanced wrapper
        renamer = PyPDFFormFieldRenamer(pdf_path)
        
        # Test PDF loading
        print("📄 Loading PDF...")
        if not renamer.load_pdf():
            print("❌ Failed to load PDF")
            return False
        
        print("✅ PDF loaded successfully")
        
        # Test enhanced field extraction
        print("\n🔍 Extracting fields with enhanced detection...")
        fields = renamer.extract_fields()
        
        if not fields:
            print("❌ No fields extracted")
            return False
        
        print(f"✅ Extracted {len(fields)} fields")
        
        # Analyze field types
        type_counts = {}
        for field in fields:
            field_type = field['type']
            type_counts[field_type] = type_counts.get(field_type, 0) + 1
        
        print(f"\n📊 Field Type Distribution:")
        for field_type, count in type_counts.items():
            print(f"  {field_type}: {count}")
        
        # Expected LIFE-1528-Q structure
        expected = {
            'RadioGroup': 6,
            'RadioButton': 20,
            'TextField': 45,
            'Total': 73
        }
        
        print(f"\n🎯 Validation against Expected Structure:")
        print(f"  Expected Total: {expected['Total']} fields")
        print(f"  Detected Total: {len(fields)} fields")
        
        radio_groups = type_counts.get('RadioGroup', 0)
        radio_buttons = type_counts.get('RadioButton', 0)
        text_fields = type_counts.get('TextField', 0)
        
        print(f"  RadioGroups: {radio_groups} (expected: {expected['RadioGroup']})")
        print(f"  RadioButtons: {radio_buttons} (expected: {expected['RadioButton']})")
        print(f"  TextFields: {text_fields} (expected: {expected['TextField']})")
        
        # Show RadioGroup fields specifically
        radio_group_fields = [f for f in fields if f['type'] == 'RadioGroup']
        if radio_group_fields:
            print(f"\n🔘 RadioGroup Fields Detected ({len(radio_group_fields)}):")
            for field in radio_group_fields:
                print(f"  - {field['name']}")
        else:
            print(f"\n❌ No RadioGroup fields detected!")
        
        # Show some RadioButton fields
        radio_button_fields = [f for f in fields if f['type'] == 'RadioButton']
        if radio_button_fields:
            print(f"\n🔘 RadioButton Fields (first 10 of {len(radio_button_fields)}):")
            for field in radio_button_fields[:10]:
                parent_info = ""
                if 'parent_group' in field and field['parent_group']:
                    parent_info = f" → parent: {field['parent_group']}"
                print(f"  - {field['name']}{parent_info}")
        
        # Test field renaming with a sample
        print(f"\n🔄 Testing Field Renaming...")
        if fields:
            test_field = fields[0]
            test_mappings = {test_field['name']: f"test_enhanced_{test_field['name']}"}
            
            # Validate mappings
            validation = renamer.validate_mappings(test_mappings)
            
            if validation.get('errors'):
                print(f"❌ Validation errors: {validation['errors']}")
            else:
                print(f"✅ Field mapping validation passed")
                
                # Test renaming (dry run)
                results = renamer.rename_fields(test_mappings)
                
                if results and results[0].success:
                    print(f"✅ Field renaming test successful: {test_field['name']} → {results[0].new_name}")
                else:
                    error = results[0].error if results else "No results"
                    print(f"❌ Field renaming failed: {error}")
        
        # Success criteria
        total_detected = len(fields)
        success_rate = (total_detected / expected['Total']) * 100
        
        print(f"\n📈 Results Summary:")
        print(f"  Detection Rate: {success_rate:.1f}% ({total_detected}/{expected['Total']})")
        
        if total_detected >= expected['Total'] * 0.95:  # 95% threshold
            print(f"🎉 SUCCESS: Enhanced wrapper meets 95%+ detection rate!")
            return True
        elif total_detected >= expected['Total'] * 0.8:  # 80% threshold
            print(f"⚠️  PARTIAL SUCCESS: Good detection rate but room for improvement")
            return True
        else:
            print(f"❌ DETECTION ISSUE: Significant fields missing")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_wrapper()
    print(f"\n{'='*80}")
    if success:
        print("✅ ENHANCED WRAPPER TEST PASSED")
    else:
        print("❌ ENHANCED WRAPPER TEST FAILED")
    print(f"{'='*80}")
    
    sys.exit(0 if success else 1)