#!/usr/bin/env python3
"""Command-line interface for PDF field extraction."""

import click
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any
import json
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdf_parser.field_extractor import PDFFieldExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--quiet', '-q', is_flag=True, help='Suppress output except errors')
def cli(verbose: bool, quiet: bool):
    """PDFParseV2 - AI-powered PDF form field extraction and naming system."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    elif quiet:
        logging.getLogger().setLevel(logging.ERROR)


@cli.command()
@click.argument('pdf_path', type=click.Path(exists=True, dir_okay=False))
@click.option('--output', '-o', type=click.Path(), help='Output file path (auto-detect format by extension)')
@click.option('--format', '-f', type=click.Choice(['json', 'csv']), default='json', help='Output format')
@click.option('--context-radius', '-r', default=50, help='Text context radius in pixels')
@click.option('--pretty', is_flag=True, help='Pretty-print JSON output')
def extract(pdf_path: str, output: str, format: str, context_radius: int, pretty: bool):
    """Extract form fields from a single PDF file."""
    logger.info(f"Starting field extraction: {pdf_path}")
    
    try:
        # Initialize extractor
        extractor = PDFFieldExtractor()
        
        # Extract fields
        result = extractor.extract_fields(
            pdf_path=pdf_path,
            context_radius=context_radius,
            output_format=format
        )
        
        if not result['success']:
            click.echo(f"❌ Extraction failed: {result.get('error', 'Unknown error')}", err=True)
            sys.exit(1)
        
        # Success message
        click.echo(f"✅ Extracted {result['field_count']} fields from {result['pages_processed']} pages")
        
        # Handle output
        if output:
            output_path = Path(output)
            
            # Auto-detect format from extension if not specified
            if output_path.suffix.lower() == '.csv' and format == 'json':
                format = 'csv'
                click.echo("Auto-detected CSV format from file extension")
            elif output_path.suffix.lower() == '.json' and format == 'csv':
                format = 'json'
                click.echo("Auto-detected JSON format from file extension")
            
            if format == 'csv':
                # Export to CSV
                success = extractor.export_to_csv(result['data'], str(output_path))
                if success:
                    click.echo(f"📄 CSV exported to: {output_path}")
                else:
                    click.echo(f"❌ Failed to export CSV to: {output_path}", err=True)
                    sys.exit(1)
            else:
                # Export to JSON
                output_data = {
                    'metadata': {
                        'pdf_path': pdf_path,
                        'field_count': result['field_count'],
                        'pages_processed': result['pages_processed'],
                        'extraction_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'context_radius': context_radius
                    },
                    'fields': result['data']
                }
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    if pretty:
                        json.dump(output_data, f, indent=2, ensure_ascii=False)
                    else:
                        json.dump(output_data, f, ensure_ascii=False)
                
                click.echo(f"📄 JSON exported to: {output_path}")
        else:
            # Print to stdout
            if format == 'csv':
                click.echo("⚠️  CSV format requires --output option", err=True)
                sys.exit(1)
            else:
                output_data = {
                    'metadata': {
                        'pdf_path': pdf_path,
                        'field_count': result['field_count'],
                        'pages_processed': result['pages_processed'],
                        'extraction_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'context_radius': context_radius
                    },
                    'fields': result['data']
                }
                
                if pretty:
                    click.echo(json.dumps(output_data, indent=2, ensure_ascii=False))
                else:
                    click.echo(json.dumps(output_data, ensure_ascii=False))
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        click.echo(f"❌ Unexpected error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_dir', type=click.Path(exists=True, file_okay=False))
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory for results')
@click.option('--format', '-f', type=click.Choice(['json', 'csv']), default='csv', help='Output format')
@click.option('--pattern', '-p', default='*.pdf', help='File pattern to match (e.g., "*.pdf")')
@click.option('--context-radius', '-r', default=50, help='Text context radius in pixels')
@click.option('--parallel', is_flag=True, help='Process files in parallel (experimental)')
@click.option('--continue-on-error', is_flag=True, help='Continue processing even if some files fail')
def batch(input_dir: str, output_dir: str, format: str, pattern: str, context_radius: int, 
          parallel: bool, continue_on_error: bool):
    """Process multiple PDF files in batch mode."""
    input_path = Path(input_dir)
    output_path = Path(output_dir) if output_dir else input_path / 'extracted_fields'
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find PDF files
    pdf_files = list(input_path.glob(pattern))
    pdf_files = [f for f in pdf_files if f.suffix.lower() == '.pdf']
    
    if not pdf_files:
        click.echo(f"❌ No PDF files found matching pattern '{pattern}' in {input_dir}", err=True)
        sys.exit(1)
    
    click.echo(f"📁 Found {len(pdf_files)} PDF files to process")
    click.echo(f"📁 Output directory: {output_path}")
    
    # Initialize extractor
    extractor = PDFFieldExtractor()
    
    # Process files
    results = []
    failed_files = []
    
    with click.progressbar(pdf_files, label='Processing PDFs') as pdf_list:
        for pdf_file in pdf_list:
            try:
                # Extract fields
                result = extractor.extract_fields(
                    pdf_path=str(pdf_file),
                    context_radius=context_radius,
                    output_format=format
                )
                
                if result['success']:
                    # Generate output filename
                    output_filename = pdf_file.stem + f'_extracted_fields.{format}'
                    output_file = output_path / output_filename
                    
                    if format == 'csv':
                        success = extractor.export_to_csv(result['data'], str(output_file))
                        if not success:
                            raise Exception("CSV export failed")
                    else:
                        output_data = {
                            'metadata': {
                                'pdf_path': str(pdf_file),
                                'field_count': result['field_count'],
                                'pages_processed': result['pages_processed'],
                                'extraction_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                                'context_radius': context_radius
                            },
                            'fields': result['data']
                        }
                        
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump(output_data, f, indent=2, ensure_ascii=False)
                    
                    results.append({
                        'pdf_file': str(pdf_file),
                        'output_file': str(output_file),
                        'field_count': result['field_count'],
                        'pages_processed': result['pages_processed'],
                        'success': True
                    })
                else:
                    failed_files.append({
                        'pdf_file': str(pdf_file),
                        'error': result.get('error', 'Unknown error'),
                        'error_type': result.get('error_type', 'Unknown')
                    })
                    
                    if not continue_on_error:
                        click.echo(f"\\n❌ Processing failed for {pdf_file}: {result.get('error')}", err=True)
                        sys.exit(1)
                        
            except Exception as e:
                failed_files.append({
                    'pdf_file': str(pdf_file),
                    'error': str(e),
                    'error_type': type(e).__name__
                })
                
                if not continue_on_error:
                    click.echo(f"\\n❌ Unexpected error processing {pdf_file}: {str(e)}", err=True)
                    sys.exit(1)
    
    # Generate summary report
    summary_file = output_path / 'batch_processing_summary.json'
    summary = {
        'batch_info': {
            'input_directory': str(input_path),
            'output_directory': str(output_path),
            'pattern': pattern,
            'format': format,
            'context_radius': context_radius,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        },
        'results': {
            'total_files': len(pdf_files),
            'successful': len(results),
            'failed': len(failed_files),
            'total_fields_extracted': sum(r['field_count'] for r in results)
        },
        'successful_files': results,
        'failed_files': failed_files
    }
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Print summary
    click.echo(f"\\n📊 Batch Processing Summary:")
    click.echo(f"   ✅ Successful: {len(results)}/{len(pdf_files)} files")
    click.echo(f"   ❌ Failed: {len(failed_files)}/{len(pdf_files)} files")
    click.echo(f"   📄 Total fields extracted: {sum(r['field_count'] for r in results)}")
    click.echo(f"   📄 Summary saved to: {summary_file}")
    
    if failed_files:
        click.echo("\\n❌ Failed files:")
        for failure in failed_files[:5]:  # Show first 5 failures
            click.echo(f"   - {Path(failure['pdf_file']).name}: {failure['error']}")
        if len(failed_files) > 5:
            click.echo(f"   ... and {len(failed_files) - 5} more (see summary file)")


@cli.command()
@click.argument('pdf_path', type=click.Path(exists=True, dir_okay=False))
def info(pdf_path: str):
    """Show information about a PDF file without extracting fields."""
    logger.info(f"Analyzing PDF: {pdf_path}")
    
    try:
        extractor = PDFFieldExtractor()
        
        # Get basic PDF info
        page_count = extractor._get_page_count(pdf_path)
        
        # Try to extract fields for analysis
        result = extractor.extract_fields(pdf_path, output_format='json')
        
        pdf_file = Path(pdf_path)
        file_size = pdf_file.stat().st_size
        
        click.echo(f"📄 PDF Information: {pdf_file.name}")
        click.echo(f"   📁 File size: {file_size:,} bytes ({file_size / 1024 / 1024:.1f} MB)")
        click.echo(f"   📑 Pages: {page_count}")
        
        if result['success']:
            fields = result['data']
            
            # Count field types
            field_types = {}
            for field in fields:
                field_type = field.get('Type', 'Unknown')
                field_types[field_type] = field_types.get(field_type, 0) + 1
            
            click.echo(f"   📝 Total fields: {result['field_count']}")
            click.echo(f"   🔧 Field types:")
            for field_type, count in sorted(field_types.items()):
                click.echo(f"      - {field_type}: {count}")
                
            # Show RadioGroup relationships if present
            radio_groups = [f for f in fields if f.get('Type') == 'RadioGroup']
            radio_buttons = [f for f in fields if f.get('Type') == 'RadioButton']
            
            if radio_groups:
                click.echo(f"   🔘 RadioGroup relationships:")
                for group in radio_groups[:3]:  # Show first 3
                    group_id = group.get('ID')
                    children = [b for b in radio_buttons if b.get('Parent ID') == group_id]
                    click.echo(f"      - {group.get('Api name', 'Unknown')}: {len(children)} buttons")
                
                if len(radio_groups) > 3:
                    click.echo(f"      ... and {len(radio_groups) - 3} more groups")
        else:
            click.echo(f"   ❌ Field extraction failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        click.echo(f"❌ Error analyzing PDF: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
def version():
    """Show version information."""
    click.echo("PDFParseV2 - AI-powered PDF form field extraction")
    click.echo("Version: 1.0.0")
    click.echo("Phase 1: PDF Field Extractor - COMPLETE")


if __name__ == '__main__':
    cli()