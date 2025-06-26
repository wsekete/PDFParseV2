#!/usr/bin/env python3
"""
Test script for MCP server setup and configuration.
Verifies that all components are properly configured for Claude Desktop integration.
"""

import json
import sys
from pathlib import Path

def test_mcp_server_import():
    """Test that the MCP server can be imported and initialized."""
    print("🧪 Testing MCP server import...")
    
    try:
        sys.path.append('src')
        from mcp_tools.pdf_naming_server import PDFNamingServer
        print("  ✅ MCP server imports successfully")
        
        server = PDFNamingServer()
        print("  ✅ MCP server initializes successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_tool_imports():
    """Test that all tool classes can be imported."""
    print("\n🧪 Testing tool imports...")
    
    # Add src to path for imports
    sys.path.insert(0, 'src')
    
    tools = {
        'ExtractFieldsTool': 'mcp_tools.tools.extract_fields',
        'GenerateNamesTool': 'mcp_tools.tools.generate_names',
        'ValidateNamesTool': 'mcp_tools.tools.validate_names',
        'ExportMappingTool': 'mcp_tools.tools.export_mapping'
    }
    
    success = True
    for tool_name, module_path in tools.items():
        try:
            module = __import__(module_path, fromlist=[tool_name])
            tool_class = getattr(module, tool_name)
            tool_instance = tool_class()
            print(f"  ✅ {tool_name} loads successfully")
        except Exception as e:
            print(f"  ❌ {tool_name} failed: {e}")
            success = False
    
    return success

def test_configuration_files():
    """Test that configuration files exist and are valid."""
    print("\n🧪 Testing configuration files...")
    
    config_files = [
        'claude_desktop_config.json',
        'src/mcp_tools/config/claude_desktop_config.json'
    ]
    
    success = True
    for config_file in config_files:
        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                print(f"  ✅ {config_file} exists and is valid JSON")
                
                # Check for required MCP server configuration
                if 'mcpServers' in config and 'pdf-naming' in config['mcpServers']:
                    print(f"  ✅ {config_file} contains pdf-naming server config")
                else:
                    print(f"  ⚠️  {config_file} missing pdf-naming server config")
                    
            except json.JSONDecodeError as e:
                print(f"  ❌ {config_file} invalid JSON: {e}")
                success = False
        else:
            print(f"  ❌ {config_file} not found")
            success = False
    
    return success

def test_dependencies():
    """Test that required dependencies are available."""
    print("\n🧪 Testing dependencies...")
    
    required_modules = [
        'mcp',
        'PyPDF2', 
        'pdfplumber',
        'pandas',
        'pydantic',
        'click',
        'loguru'
    ]
    
    success = True
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module} is available")
        except ImportError:
            print(f"  ❌ {module} not found - run: pip install {module}")
            success = False
    
    return success

def test_training_data():
    """Test that training data files exist."""
    print("\n🧪 Testing training data...")
    
    training_files = [
        'training_data/Clean Field Data - Sheet1.csv',
        'training_data/pdf_csv_pairs/'
    ]
    
    success = True
    for file_path in training_files:
        path = Path(file_path)
        if path.exists():
            if path.is_file():
                print(f"  ✅ {file_path} exists ({path.stat().st_size} bytes)")
            else:
                file_count = len(list(path.glob('*'))) if path.is_dir() else 0
                print(f"  ✅ {file_path} exists ({file_count} files)")
        else:
            print(f"  ❌ {file_path} not found")
            success = False
    
    return success

def main():
    """Run all tests and report results."""
    print("🚀 PDFParseV2 MCP Setup Test\n")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Training Data", test_training_data),
        ("Tool Imports", test_tool_imports),
        ("MCP Server", test_mcp_server_import),
        ("Configuration Files", test_configuration_files)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! MCP setup is ready for Claude Desktop.")
        print("\nNext steps:")
        print("1. Follow CLAUDE_DESKTOP_SETUP.md to configure Claude Desktop")
        print("2. Restart Claude Desktop")
        print("3. Test the tools with a sample PDF")
    else:
        print("⚠️  Some tests failed. Please fix the issues before proceeding.")
        print("\nSee CLAUDE_DESKTOP_SETUP.md for troubleshooting tips.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())