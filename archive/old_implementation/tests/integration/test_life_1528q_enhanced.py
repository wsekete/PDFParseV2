#!/usr/bin/env python3
"""
Enhanced LIFE-1528-Q Integration Test
Tests the improved PyPDFForm wrapper with complex RadioGroup structures

MOVED FROM: /test_life_1528q_simple.py, /test_complex_life_1528q.py
CONSOLIDATED: Multiple test scripts into organized integration test
"""

import sys
from pathlib import Path

# Add src to path - adjusted for new test location
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

def test_enhanced_life_1528q():
    """Test enhanced PyPDFForm wrapper with LIFE-1528-Q complex form."""
    print("🧪 Testing Enhanced LIFE-1528-Q Processing...")
    print("Expected: 73 fields (6 RadioGroups, 20+ RadioButtons, 45+ TextFields)")
    
    pdf_path = str(Path(__file__).parent.parent.parent / "training_data/pdf_csv_pairs/LIFE-1528-Q__parsed.pdf")
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        return False
    
    try:
        from pdf_modifier.pypdfform_field_renamer import PyPDFFormFieldRenamer
        
        # Test enhanced wrapper
        renamer = PyPDFFormFieldRenamer(pdf_path)
        
        if not renamer.load_pdf():
            print("❌ Failed to load PDF")
            return False
        
        print("✅ PDF loaded with enhanced wrapper")
        
        # Extract fields with enhanced detection
        fields = renamer.extract_fields()
        print(f"📊 Fields detected: {len(fields)}")
        
        # Analyze field types
        type_counts = {}
        for field in fields:
            field_type = field['type']
            type_counts[field_type] = type_counts.get(field_type, 0) + 1
        
        print("Field type distribution:")
        for field_type, count in type_counts.items():
            print(f"  {field_type}: {count}")
        
        # Validation against expected structure
        radio_groups = type_counts.get('RadioGroup', 0)
        radio_buttons = type_counts.get('RadioButton', 0)
        text_fields = type_counts.get('TextField', 0)
        
        print(f"\nValidation Results:")
        print(f"  RadioGroups: {radio_groups}/6 expected")
        print(f"  RadioButtons: {radio_buttons}/20+ expected") 
        print(f"  TextFields: {text_fields}/45+ expected")
        print(f"  Total: {len(fields)}/73 expected")
        
        # Success criteria: 95%+ detection rate
        success_rate = (len(fields) / 73) * 100
        print(f"  Detection Rate: {success_rate:.1f}%")
        
        if success_rate >= 95:
            print("🎉 SUCCESS: Enhanced wrapper meets 95%+ detection target!")
            return True
        elif success_rate >= 80:
            print("⚠️  PARTIAL: Good improvement but not yet optimal")
            return True
        else:
            print("❌ NEEDS WORK: Still significant detection issues")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("ENHANCED LIFE-1528-Q INTEGRATION TEST")
    print("="*60)
    success = test_enhanced_life_1528q()
    print("="*60)
    if success:
        print("✅ INTEGRATION TEST PASSED")
    else:
        print("❌ INTEGRATION TEST FAILED")
    
    sys.exit(0 if success else 1)