#!/usr/bin/env python3
"""
Debug script for MCP tools integration testing.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_tools.tools.extract_fields import ExtractFieldsTool

async def test_extract():
    """Test field extraction with a real PDF."""
    
    # Find a PDF file
    pdf_dir = Path("training_data/pdf_csv_pairs")
    pdfs = list(pdf_dir.glob("*.pdf"))
    
    if not pdfs:
        print("❌ No PDF files found")
        return False
    
    test_pdf = pdfs[0]  # Use first available PDF
    print(f"🧪 Testing with: {test_pdf.name}")
    
    # Test extraction
    extract_tool = ExtractFieldsTool()
    
    try:
        result = await extract_tool.execute(
            pdf_path=str(test_pdf),
            context_radius=50,
            output_format="csv"
        )
        
        if result["success"]:
            print(f"✅ Extraction successful!")
            print(f"   - Fields found: {result['extraction_metadata']['field_count']}")
            print(f"   - Pages processed: {result['extraction_metadata']['pages_processed']}")
            
            if result["fields"]:
                first_field = result["fields"][0]
                print(f"   - First field: {first_field.get('Label', 'No label')}")
            
            return True
        else:
            print(f"❌ Extraction failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during extraction: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_full_workflow():
    """Test the complete MCP workflow."""
    
    print("🚀 Testing complete MCP workflow...")
    
    # Import all tools
    from mcp_tools.tools.extract_fields import ExtractFieldsTool
    from mcp_tools.tools.generate_names import GenerateNamesTool
    from mcp_tools.tools.validate_names import ValidateNamesTool
    from mcp_tools.tools.export_mapping import ExportMappingTool
    
    tools = {
        "extract": ExtractFieldsTool(),
        "generate": GenerateNamesTool(),
        "validate": ValidateNamesTool(),
        "export": ExportMappingTool()
    }
    
    # Find PDF
    pdf_dir = Path("training_data/pdf_csv_pairs")
    test_pdf = pdf_dir / "W-4R_parsed.pdf"
    
    if not test_pdf.exists():
        pdfs = list(pdf_dir.glob("*.pdf"))
        if not pdfs:
            print("❌ No PDF files found")
            return False
        test_pdf = pdfs[0]
    
    print(f"📄 Using PDF: {test_pdf.name}")
    
    try:
        # Step 1: Extract
        print("1. Extracting fields...")
        extract_result = await tools["extract"].execute(
            pdf_path=str(test_pdf),
            context_radius=50
        )
        
        if not extract_result["success"]:
            print(f"❌ Extraction failed: {extract_result.get('error')}")
            return False
        
        field_count = extract_result["extraction_metadata"]["field_count"]
        print(f"   ✅ Extracted {field_count} fields")
        
        # Step 2: Generate names
        print("2. Generating names...")
        generate_result = await tools["generate"].execute(
            field_data=extract_result,
            use_training_data=True,
            confidence_threshold=0.0
        )
        
        if not generate_result["success"]:
            print(f"❌ Name generation failed: {generate_result.get('error')}")
            return False
        
        generated_count = generate_result["generation_metadata"]["generated_count"]
        print(f"   ✅ Generated {generated_count} names")
        
        # Show a sample generated name
        if generate_result["generated_names"]:
            sample = generate_result["generated_names"][0]
            print(f"   📝 Sample: {sample['original_name']} → {sample['suggested_name']}")
        
        # Step 3: Validate
        print("3. Validating names...")
        validate_result = await tools["validate"].execute(
            name_data=generate_result,
            check_bem_compliance=True
        )
        
        if not validate_result["success"]:
            print(f"❌ Validation failed: {validate_result.get('error')}")
            return False
        
        valid_count = validate_result["validation_summary"]["valid_names"]
        total_count = validate_result["validation_metadata"]["total_names"]
        print(f"   ✅ Validated {valid_count}/{total_count} names")
        
        # Step 4: Export
        print("4. Exporting mapping...")
        export_result = await tools["export"].execute(
            validated_names=validate_result,
            output_format="json"
        )
        
        if not export_result["success"]:
            print(f"❌ Export failed: {export_result.get('error')}")
            return False
        
        exported_count = export_result["export_metadata"]["exported_fields"]
        print(f"   ✅ Exported {exported_count} field mappings")
        
        print("🎉 Complete workflow successful!")
        return True
        
    except Exception as e:
        print(f"❌ Workflow failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run debug tests."""
    print("🔧 MCP Tools Debug Test\n")
    
    success = True
    
    # Test 1: Basic extraction
    print("=" * 50)
    result = asyncio.run(test_extract())
    if not result:
        success = False
    
    # Test 2: Full workflow
    print("\n" + "=" * 50)
    result = asyncio.run(test_full_workflow())
    if not result:
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())