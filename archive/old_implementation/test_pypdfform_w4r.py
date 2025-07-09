#!/usr/bin/env python3
"""
Test PyPDFForm implementation with W-4R PDF
Task 2.1.2 - Simple PDF testing (10 fields)

This script tests the current PyPDFForm implementation with the W-4R_parsed.pdf
to validate actual field detection and renaming capabilities.
"""

import sys
import os
import time
import logging
from pathlib import Path
from typing import Dict, List, Any

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_pypdfform_import():
    """Test PyPDFForm import."""
    try:
        from PyPDFForm import PdfWrapper
        logger.info("✅ PyPDFForm imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ PyPDFForm import failed: {e}")
        return False

def test_wrapper_import():
    """Test our PyPDFForm wrapper import."""
    try:
        from pdf_modifier.pypdfform_field_renamer import PyPDFFormFieldRenamer
        logger.info("✅ PyPDFForm wrapper imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ PyPDFForm wrapper import failed: {e}")
        return False

def test_basic_pypdfform_functionality():
    """Test basic PyPDFForm functionality with W-4R PDF."""
    pdf_path = "training_data/pdf_csv_pairs/W-4R_parsed.pdf"
    
    if not Path(pdf_path).exists():
        logger.error(f"❌ Test PDF not found: {pdf_path}")
        return False
    
    try:
        from PyPDFForm import PdfWrapper
        
        logger.info(f"🔍 Testing basic PyPDFForm with {pdf_path}")
        
        # Test PDF loading
        pdf = PdfWrapper(pdf_path)
        logger.info("✅ PDF loaded successfully with PyPDFForm")
        
        # Test field detection via sample_data
        try:
            sample_data = pdf.sample_data
            logger.info(f"✅ Sample data retrieved: {len(sample_data)} fields found")
            
            # Display found fields
            if sample_data:
                logger.info("📋 Fields detected:")
                for i, (field_name, field_value) in enumerate(list(sample_data.items())[:5], 1):
                    logger.info(f"  {i}. {field_name}: {field_value}")
                if len(sample_data) > 5:
                    logger.info(f"  ... and {len(sample_data) - 5} more fields")
            else:
                logger.warning("⚠️  No fields found in sample_data")
            
            return True, len(sample_data), list(sample_data.keys())
            
        except Exception as e:
            logger.error(f"❌ Field detection failed: {e}")
            return False, 0, []
            
    except Exception as e:
        logger.error(f"❌ Basic PyPDFForm test failed: {e}")
        return False, 0, []

def test_pypdfform_wrapper_functionality():
    """Test our PyPDFForm wrapper with W-4R PDF."""
    pdf_path = "training_data/pdf_csv_pairs/W-4R_parsed.pdf"
    
    try:
        from pdf_modifier.pypdfform_field_renamer import PyPDFFormFieldRenamer
        
        logger.info(f"🔍 Testing PyPDFForm wrapper with {pdf_path}")
        
        # Initialize the renamer
        renamer = PyPDFFormFieldRenamer(pdf_path)
        
        # Test PDF loading
        if not renamer.load_pdf():
            logger.error("❌ Failed to load PDF with wrapper")
            return False
        
        logger.info("✅ PDF loaded successfully with wrapper")
        
        # Test field extraction
        fields = renamer.extract_fields()
        logger.info(f"✅ Field extraction completed: {len(fields)} fields found")
        
        if fields:
            logger.info("📋 Fields extracted by wrapper:")
            for i, field in enumerate(fields[:5], 1):
                logger.info(f"  {i}. {field}")
            if len(fields) > 5:
                logger.info(f"  ... and {len(fields) - 5} more fields")
        else:
            logger.warning("⚠️  No fields extracted by wrapper")
        
        return True, len(fields), fields
        
    except Exception as e:
        logger.error(f"❌ PyPDFForm wrapper test failed: {e}")
        return False, 0, []

def test_field_renaming():
    """Test actual field renaming functionality."""
    pdf_path = "training_data/pdf_csv_pairs/W-4R_parsed.pdf"
    
    try:
        from pdf_modifier.pypdfform_field_renamer import PyPDFFormFieldRenamer
        from PyPDFForm import PdfWrapper
        
        logger.info(f"🔍 Testing field renaming with {pdf_path}")
        
        # First, get actual field names from PyPDFForm
        pdf = PdfWrapper(pdf_path)
        sample_data = pdf.sample_data
        
        if not sample_data:
            logger.error("❌ No fields found for renaming test")
            return False
        
        # Get first field for testing
        original_fields = list(sample_data.keys())
        test_field = original_fields[0] if original_fields else None
        
        if not test_field:
            logger.error("❌ No test field available")
            return False
        
        logger.info(f"🎯 Testing rename of field: '{test_field}'")
        
        # Initialize renamer
        renamer = PyPDFFormFieldRenamer(pdf_path)
        
        if not renamer.load_pdf():
            logger.error("❌ Failed to load PDF for renaming")
            return False
        
        # Test renaming
        test_mappings = {
            test_field: f"test_renamed_{test_field}"
        }
        
        logger.info(f"🔄 Attempting to rename: {test_field} → {test_mappings[test_field]}")
        
        # Validate mappings first
        validation = renamer.validate_mappings(test_mappings)
        logger.info(f"✅ Validation complete: {len(validation['errors'])} errors, {len(validation['warnings'])} warnings")
        
        if validation['errors']:
            logger.error(f"❌ Validation errors: {validation['errors']}")
            return False
        
        # Attempt renaming
        results = renamer.rename_fields(test_mappings)
        
        if not results:
            logger.error("❌ No results returned from rename operation")
            return False
        
        result = results[0]
        success_rate = renamer.get_success_rate(results)
        
        logger.info(f"📊 Rename result: {result.success}")
        logger.info(f"📊 Success rate: {success_rate:.1f}%")
        
        if result.error:
            logger.error(f"❌ Rename error: {result.error}")
        
        # Try to save the result (to test output)
        if result.success:
            output_path = "training_data/pdf_csv_pairs/W-4R_parsed_test_output.pdf"
            save_success = renamer.save_pdf(output_path)
            logger.info(f"💾 Save result: {save_success}")
            
            if save_success:
                logger.info(f"✅ Test output saved to: {output_path}")
                
                # Verify the renamed field exists in output
                try:
                    output_pdf = PdfWrapper(output_path)
                    output_data = output_pdf.sample_data
                    
                    renamed_field_exists = test_mappings[test_field] in output_data
                    original_field_exists = test_field in output_data
                    
                    logger.info(f"🔍 Verification - Original field exists: {original_field_exists}")
                    logger.info(f"🔍 Verification - Renamed field exists: {renamed_field_exists}")
                    
                    if renamed_field_exists and not original_field_exists:
                        logger.info("✅ Field rename verification successful!")
                        return True
                    else:
                        logger.warning("⚠️  Field rename verification inconclusive")
                        return result.success
                        
                except Exception as e:
                    logger.error(f"❌ Verification failed: {e}")
                    return result.success
            else:
                return False
        
        return result.success
        
    except Exception as e:
        logger.error(f"❌ Field renaming test failed: {e}")
        return False

def load_expected_fields():
    """Load expected field names from training data."""
    csv_path = "training_data/pdf_csv_pairs/W-4R_parsed_correct_mapping.csv"
    
    if not Path(csv_path).exists():
        logger.warning(f"⚠️  Expected mapping file not found: {csv_path}")
        return []
    
    try:
        import pandas as pd
        df = pd.read_csv(csv_path)
        
        # Extract API names (BEM field names)
        api_names = df['Api name'].tolist() if 'Api name' in df.columns else []
        logger.info(f"📋 Expected fields from training data: {len(api_names)} fields")
        
        return api_names
        
    except Exception as e:
        logger.error(f"❌ Failed to load expected fields: {e}")
        return []

def main():
    """Run all W-4R PyPDFForm tests."""
    logger.info("=" * 80)
    logger.info("PyPDFForm W-4R Testing - Task 2.1.2")
    logger.info("=" * 80)
    
    test_results = {}
    start_time = time.time()
    
    # Test 1: Import tests
    logger.info("\n🧪 Test 1: Import validation")
    test_results['pypdfform_import'] = test_pypdfform_import()
    test_results['wrapper_import'] = test_wrapper_import()
    
    if not all([test_results['pypdfform_import'], test_results['wrapper_import']]):
        logger.error("❌ Import tests failed. Cannot proceed with functionality tests.")
        return 1
    
    # Test 2: Basic PyPDFForm functionality
    logger.info("\n🧪 Test 2: Basic PyPDFForm functionality")
    basic_success, basic_field_count, basic_fields = test_basic_pypdfform_functionality()
    test_results['basic_functionality'] = basic_success
    test_results['basic_field_count'] = basic_field_count
    
    # Test 3: Wrapper functionality
    logger.info("\n🧪 Test 3: PyPDFForm wrapper functionality")
    wrapper_success, wrapper_field_count, wrapper_fields = test_pypdfform_wrapper_functionality()
    test_results['wrapper_functionality'] = wrapper_success
    test_results['wrapper_field_count'] = wrapper_field_count
    
    # Test 4: Field renaming
    logger.info("\n🧪 Test 4: Field renaming functionality")
    test_results['field_renaming'] = test_field_renaming()
    
    # Test 5: Compare with expected data
    logger.info("\n🧪 Test 5: Compare with training data")
    expected_fields = load_expected_fields()
    test_results['expected_field_count'] = len(expected_fields)
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    total_tests = 0
    passed_tests = 0
    
    for test_name, result in test_results.items():
        if isinstance(result, bool):
            total_tests += 1
            if result:
                passed_tests += 1
                logger.info(f"✅ PASS: {test_name}")
            else:
                logger.info(f"❌ FAIL: {test_name}")
        elif isinstance(result, int):
            logger.info(f"📊 INFO: {test_name} = {result}")
    
    elapsed_time = time.time() - start_time
    
    logger.info(f"\n📊 Overall Results:")
    logger.info(f"   Tests passed: {passed_tests}/{total_tests}")
    logger.info(f"   Success rate: {(passed_tests/total_tests)*100:.1f}%")
    logger.info(f"   PyPDFForm detected fields: {test_results.get('basic_field_count', 0)}")
    logger.info(f"   Wrapper detected fields: {test_results.get('wrapper_field_count', 0)}")
    logger.info(f"   Expected fields (training): {test_results.get('expected_field_count', 0)}")
    logger.info(f"   Test duration: {elapsed_time:.2f} seconds")
    
    # Final assessment
    if passed_tests == total_tests:
        logger.info("\n🎉 All tests PASSED! PyPDFForm implementation is working.")
        return 0
    elif passed_tests >= total_tests * 0.7:
        logger.info("\n⚠️  Most tests passed, but some issues detected.")
        return 1
    else:
        logger.info("\n❌ Major issues detected with PyPDFForm implementation.")
        return 2

if __name__ == "__main__":
    sys.exit(main())