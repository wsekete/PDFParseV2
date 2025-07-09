#!/usr/bin/env python3
"""
Comprehensive testing with all 14 training PDFs - Task 2.1.4
Test PyPDFForm implementation across entire dataset

This script validates PyPDFForm performance with:
- All 14 PDF/CSV pairs from training data
- Field detection accuracy
- Type classification precision
- Processing performance
- Error handling
"""

import sys
import os
import time
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def get_pdf_csv_pairs():
    """Get all PDF/CSV pairs from training data directory."""
    pairs_dir = Path("training_data/pdf_csv_pairs")
    pdf_files = list(pairs_dir.glob("*_parsed.pdf"))
    
    pdf_csv_pairs = []
    for pdf_file in pdf_files:
        # Skip test output files
        if any(skip in pdf_file.name for skip in ['backup', 'test', 'renamed']):
            continue
            
        # Find corresponding CSV file
        csv_name = pdf_file.name.replace('.pdf', '_correct_mapping.csv')
        csv_file = pairs_dir / csv_name
        
        if csv_file.exists():
            pdf_csv_pairs.append({
                'pdf_path': str(pdf_file),
                'csv_path': str(csv_file),
                'name': pdf_file.stem.replace('_parsed', '')
            })
    
    return sorted(pdf_csv_pairs, key=lambda x: x['name'])

def analyze_expected_fields(csv_path: str) -> Dict[str, Any]:
    """Analyze expected fields from CSV training data."""
    try:
        df = pd.read_csv(csv_path)
        
        # Basic field analysis
        field_analysis = {
            'total_fields': len(df),
            'field_types': df['Type'].value_counts().to_dict(),
            'api_names': df['Api name'].tolist(),
            'field_labels': df['Acrofieldlabel'].tolist(),
            'parent_relationships': []
        }
        
        # Analyze parent-child relationships
        for _, row in df.iterrows():
            if pd.notna(row['Parent ID']) and row['Parent ID'] != 'Delete Parent ID':
                parent_row = df[df['ID'] == row['Parent ID']]
                if len(parent_row) > 0:
                    field_analysis['parent_relationships'].append({
                        'child': row['Api name'],
                        'parent': parent_row['Api name'].iloc[0],
                        'child_type': row['Type'],
                        'parent_type': parent_row['Type'].iloc[0]
                    })
        
        return field_analysis
        
    except Exception as e:
        print(f"❌ Failed to analyze {csv_path}: {e}")
        return {}

def test_pypdfform_basic(pdf_path: str) -> Tuple[bool, Dict[str, Any]]:
    """Test basic PyPDFForm functionality."""
    try:
        from PyPDFForm import PdfWrapper
        
        pdf = PdfWrapper(pdf_path)
        sample_data = pdf.sample_data
        
        if not sample_data:
            return False, {'error': 'No sample_data returned'}
        
        # Analyze field types
        field_types = {}
        for field_name in sample_data.keys():
            if field_name.endswith('--group'):
                field_types[field_name] = 'RadioGroup'
            elif '--' in field_name and not field_name.endswith('--group'):
                field_types[field_name] = 'RadioButton'
            else:
                field_types[field_name] = 'TextField'
        
        # Count field types
        type_counts = {}
        for field_type in field_types.values():
            type_counts[field_type] = type_counts.get(field_type, 0) + 1
        
        return True, {
            'total_fields': len(sample_data),
            'field_names': list(sample_data.keys()),
            'field_types': type_counts,
            'sample_data': sample_data
        }
        
    except Exception as e:
        return False, {'error': str(e)}

def test_pypdfform_wrapper(pdf_path: str) -> Tuple[bool, Dict[str, Any]]:
    """Test PyPDFForm wrapper functionality."""
    try:
        from pdf_modifier.pypdfform_field_renamer import PyPDFFormFieldRenamer
        
        renamer = PyPDFFormFieldRenamer(pdf_path)
        
        if not renamer.load_pdf():
            return False, {'error': 'Failed to load PDF'}
        
        fields = renamer.extract_fields()
        
        if not fields:
            return False, {'error': 'No fields extracted'}
        
        # Analyze field types
        type_counts = {}
        for field in fields:
            field_type = field['type']
            type_counts[field_type] = type_counts.get(field_type, 0) + 1
        
        return True, {
            'total_fields': len(fields),
            'field_names': [f['name'] for f in fields],
            'field_types': type_counts,
            'fields': fields
        }
        
    except Exception as e:
        return False, {'error': str(e)}

def test_field_renaming(pdf_path: str) -> Tuple[bool, Dict[str, Any]]:
    """Test field renaming functionality."""
    try:
        from pdf_modifier.pypdfform_field_renamer import PyPDFFormFieldRenamer
        
        renamer = PyPDFFormFieldRenamer(pdf_path)
        
        if not renamer.load_pdf():
            return False, {'error': 'Failed to load PDF'}
        
        fields = renamer.extract_fields()
        
        if not fields:
            return False, {'error': 'No fields for renaming'}
        
        # Test renaming the first field
        test_field = fields[0]
        test_name = f"test_comprehensive_{test_field['name']}"
        
        test_mappings = {test_field['name']: test_name}
        
        # Validate mappings
        validation = renamer.validate_mappings(test_mappings)
        
        if validation['errors']:
            return False, {'error': f"Validation failed: {validation['errors']}"}
        
        # Perform rename
        results = renamer.rename_fields(test_mappings)
        
        if results and results[0].success:
            return True, {
                'original_name': test_field['name'],
                'new_name': test_name,
                'field_type': test_field['type']
            }
        else:
            error = results[0].error if results else "No results"
            return False, {'error': f"Rename failed: {error}"}
            
    except Exception as e:
        return False, {'error': str(e)}

def test_single_pdf(pdf_info: Dict[str, str]) -> Dict[str, Any]:
    """Test a single PDF with all validation steps."""
    print(f"\n📄 Testing {pdf_info['name']}...")
    
    start_time = time.time()
    results = {
        'name': pdf_info['name'],
        'pdf_path': pdf_info['pdf_path'],
        'csv_path': pdf_info['csv_path'],
        'tests': {},
        'performance': {},
        'success': False
    }
    
    # Step 1: Analyze expected fields
    expected = analyze_expected_fields(pdf_info['csv_path'])
    results['expected'] = expected
    
    if not expected:
        results['tests']['expected_analysis'] = {'success': False, 'error': 'Failed to analyze expected fields'}
        return results
    
    print(f"  📊 Expected: {expected['total_fields']} fields")
    
    # Step 2: Test PyPDFForm basic
    pypdfform_success, pypdfform_data = test_pypdfform_basic(pdf_info['pdf_path'])
    results['tests']['pypdfform_basic'] = {
        'success': pypdfform_success,
        'data': pypdfform_data
    }
    
    if pypdfform_success:
        print(f"  ✅ PyPDFForm: {pypdfform_data['total_fields']} fields detected")
    else:
        print(f"  ❌ PyPDFForm failed: {pypdfform_data.get('error', 'Unknown error')}")
    
    # Step 3: Test PyPDFForm wrapper
    wrapper_success, wrapper_data = test_pypdfform_wrapper(pdf_info['pdf_path'])
    results['tests']['pypdfform_wrapper'] = {
        'success': wrapper_success,
        'data': wrapper_data
    }
    
    if wrapper_success:
        print(f"  ✅ Wrapper: {wrapper_data['total_fields']} fields detected")
    else:
        print(f"  ❌ Wrapper failed: {wrapper_data.get('error', 'Unknown error')}")
    
    # Step 4: Test field renaming
    renaming_success, renaming_data = test_field_renaming(pdf_info['pdf_path'])
    results['tests']['field_renaming'] = {
        'success': renaming_success,
        'data': renaming_data
    }
    
    if renaming_success:
        print(f"  ✅ Renaming: {renaming_data['original_name']} → {renaming_data['new_name']}")
    else:
        print(f"  ❌ Renaming failed: {renaming_data.get('error', 'Unknown error')}")
    
    # Performance metrics
    elapsed_time = time.time() - start_time
    results['performance'] = {
        'processing_time': elapsed_time,
        'fields_per_second': expected['total_fields'] / elapsed_time if elapsed_time > 0 else 0
    }
    
    # Overall success
    results['success'] = all(test['success'] for test in results['tests'].values())
    
    return results

def analyze_comprehensive_results(all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze comprehensive test results across all PDFs."""
    print("\n" + "="*80)
    print("COMPREHENSIVE RESULTS ANALYSIS")
    print("="*80)
    
    total_pdfs = len(all_results)
    successful_pdfs = sum(1 for r in all_results if r['success'])
    
    # Field detection analysis
    expected_fields = sum(r['expected']['total_fields'] for r in all_results if r['expected'])
    pypdfform_fields = sum(r['tests']['pypdfform_basic']['data']['total_fields'] 
                          for r in all_results 
                          if r['tests']['pypdfform_basic']['success'])
    wrapper_fields = sum(r['tests']['pypdfform_wrapper']['data']['total_fields'] 
                        for r in all_results 
                        if r['tests']['pypdfform_wrapper']['success'])
    
    # Performance analysis
    total_time = sum(r['performance']['processing_time'] for r in all_results)
    avg_time = total_time / total_pdfs if total_pdfs > 0 else 0
    
    # Field type analysis
    field_type_accuracy = {}
    for result in all_results:
        if result['success'] and result['expected']:
            expected_types = result['expected']['field_types']
            detected_types = result['tests']['pypdfform_wrapper']['data']['field_types']
            
            for field_type, expected_count in expected_types.items():
                detected_count = detected_types.get(field_type, 0)
                if field_type not in field_type_accuracy:
                    field_type_accuracy[field_type] = {'expected': 0, 'detected': 0}
                field_type_accuracy[field_type]['expected'] += expected_count
                field_type_accuracy[field_type]['detected'] += detected_count
    
    analysis = {
        'overall_success_rate': (successful_pdfs / total_pdfs) * 100,
        'field_detection_accuracy': (wrapper_fields / expected_fields) * 100 if expected_fields > 0 else 0,
        'performance': {
            'total_processing_time': total_time,
            'average_time_per_pdf': avg_time,
            'total_fields_processed': expected_fields,
            'fields_per_second': expected_fields / total_time if total_time > 0 else 0
        },
        'field_type_accuracy': field_type_accuracy,
        'summary': {
            'total_pdfs': total_pdfs,
            'successful_pdfs': successful_pdfs,
            'failed_pdfs': total_pdfs - successful_pdfs,
            'expected_fields': expected_fields,
            'pypdfform_fields': pypdfform_fields,
            'wrapper_fields': wrapper_fields
        }
    }
    
    return analysis

def print_comprehensive_summary(analysis: Dict[str, Any]):
    """Print comprehensive test summary."""
    print(f"\n📊 COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*50}")
    
    # Overall metrics
    print(f"📈 Overall Success Rate: {analysis['overall_success_rate']:.1f}%")
    print(f"🎯 Field Detection Accuracy: {analysis['field_detection_accuracy']:.1f}%")
    print(f"⚡ Processing Speed: {analysis['performance']['fields_per_second']:.1f} fields/second")
    
    # PDF processing summary
    summary = analysis['summary']
    print(f"\n📋 Processing Summary:")
    print(f"  Total PDFs: {summary['total_pdfs']}")
    print(f"  Successful: {summary['successful_pdfs']}")
    print(f"  Failed: {summary['failed_pdfs']}")
    print(f"  Expected fields: {summary['expected_fields']}")
    print(f"  Wrapper detected: {summary['wrapper_fields']}")
    
    # Field type accuracy
    if analysis['field_type_accuracy']:
        print(f"\n🔍 Field Type Accuracy:")
        for field_type, counts in analysis['field_type_accuracy'].items():
            accuracy = (counts['detected'] / counts['expected']) * 100 if counts['expected'] > 0 else 0
            print(f"  {field_type}: {accuracy:.1f}% ({counts['detected']}/{counts['expected']})")
    
    # Performance metrics
    perf = analysis['performance']
    print(f"\n⚡ Performance Metrics:")
    print(f"  Total time: {perf['total_processing_time']:.2f}s")
    print(f"  Average per PDF: {perf['average_time_per_pdf']:.2f}s")
    print(f"  Total fields: {perf['total_fields_processed']}")
    print(f"  Processing rate: {perf['fields_per_second']:.1f} fields/second")

def main():
    """Run comprehensive testing with all 14 training PDFs."""
    print("="*80)
    print("COMPREHENSIVE PYPDFFORM TESTING - Task 2.1.4")
    print("Testing with all 14 training PDFs")
    print("="*80)
    
    # Get all PDF/CSV pairs
    pdf_csv_pairs = get_pdf_csv_pairs()
    
    if not pdf_csv_pairs:
        print("❌ No PDF/CSV pairs found in training data")
        return 1
    
    print(f"📋 Found {len(pdf_csv_pairs)} PDF/CSV pairs:")
    for pair in pdf_csv_pairs:
        print(f"  - {pair['name']}")
    
    # Test each PDF
    all_results = []
    start_time = time.time()
    
    for i, pdf_info in enumerate(pdf_csv_pairs, 1):
        print(f"\n[{i}/{len(pdf_csv_pairs)}] Testing {pdf_info['name']}...")
        result = test_single_pdf(pdf_info)
        all_results.append(result)
        
        # Show quick status
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"  {status} - {result['performance']['processing_time']:.2f}s")
    
    # Comprehensive analysis
    total_time = time.time() - start_time
    analysis = analyze_comprehensive_results(all_results)
    
    # Print detailed results
    print("\n" + "="*80)
    print("DETAILED RESULTS")
    print("="*80)
    
    for result in all_results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        expected_count = result['expected']['total_fields'] if result['expected'] else 0
        
        print(f"\n{status} {result['name']}:")
        print(f"  Expected: {expected_count} fields")
        
        if result['tests']['pypdfform_basic']['success']:
            detected = result['tests']['pypdfform_basic']['data']['total_fields']
            print(f"  PyPDFForm: {detected} fields")
        else:
            print(f"  PyPDFForm: FAILED - {result['tests']['pypdfform_basic']['data'].get('error', 'Unknown')}")
        
        if result['tests']['pypdfform_wrapper']['success']:
            detected = result['tests']['pypdfform_wrapper']['data']['total_fields']
            print(f"  Wrapper: {detected} fields")
        else:
            print(f"  Wrapper: FAILED - {result['tests']['pypdfform_wrapper']['data'].get('error', 'Unknown')}")
        
        renaming_status = "✅" if result['tests']['field_renaming']['success'] else "❌"
        print(f"  Renaming: {renaming_status}")
        
        print(f"  Time: {result['performance']['processing_time']:.2f}s")
    
    # Final summary
    print_comprehensive_summary(analysis)
    
    # Determine exit code
    success_rate = analysis['overall_success_rate']
    field_accuracy = analysis['field_detection_accuracy']
    
    print(f"\n🎯 PHASE 2 TARGET ASSESSMENT:")
    print(f"  95%+ Success Rate: {'✅ ACHIEVED' if success_rate >= 95 else '❌ NOT MET'} ({success_rate:.1f}%)")
    print(f"  95%+ Field Accuracy: {'✅ ACHIEVED' if field_accuracy >= 95 else '❌ NOT MET'} ({field_accuracy:.1f}%)")
    
    if success_rate >= 95 and field_accuracy >= 95:
        print(f"\n🎉 COMPREHENSIVE TESTING SUCCESSFUL!")
        print(f"✅ PyPDFForm meets Phase 2 requirements")
        return 0
    elif success_rate >= 80 and field_accuracy >= 80:
        print(f"\n⚠️  MOSTLY SUCCESSFUL - Some optimization needed")
        return 1
    else:
        print(f"\n❌ SIGNIFICANT ISSUES DETECTED")
        return 2

if __name__ == "__main__":
    sys.exit(main())