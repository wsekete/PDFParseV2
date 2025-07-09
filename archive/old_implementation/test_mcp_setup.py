#!/usr/bin/env python3
"""
MCP Server Setup Test Script
PDFParseV2 - Claude Desktop Integration Verification

This script tests the MCP server setup and verifies all dependencies are working correctly.
"""

import sys
import os
import json
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, Any, List

def test_python_version():
    """Test Python version compatibility."""
    print("🐍 Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def test_dependency(package_name: str, import_name: str = None) -> bool:
    """Test if a Python package is installed and importable."""
    if import_name is None:
        import_name = package_name
    
    try:
        spec = importlib.util.find_spec(import_name)
        if spec is not None:
            print(f"✅ {package_name} - Installed and importable")
            return True
        else:
            print(f"❌ {package_name} - Not found")
            return False
    except Exception as e:
        print(f"❌ {package_name} - Error: {str(e)}")
        return False

def test_mcp_dependencies():
    """Test MCP framework dependencies."""
    print("\n📦 Testing MCP Framework Dependencies...")
    
    dependencies = [
        ("mcp", "mcp"),
        ("PyPDF2", "PyPDF2"),
        ("PyPDFForm", "PyPDFForm"),
        ("pdfplumber", "pdfplumber"),
        ("pandas", "pandas"),
        ("pydantic", "pydantic"),
        ("loguru", "loguru"),
        ("click", "click"),
    ]
    
    results = []
    for package_name, import_name in dependencies:
        result = test_dependency(package_name, import_name)
        results.append(result)
    
    return all(results)

def test_mcp_server_file():
    """Test if MCP server file exists and is readable."""
    print("\n🔍 Testing MCP Server File...")
    
    project_root = Path("/Users/wseke/Desktop/PDFParseV2")
    server_path = project_root / "src" / "pdf_modifier" / "mcp_server.py"
    
    if server_path.exists():
        print(f"✅ MCP server file exists: {server_path}")
        try:
            with open(server_path, 'r') as f:
                content = f.read()
                if "Server" in content and "MCP" in content:
                    print("✅ MCP server file appears to be valid")
                    return True
                else:
                    print("❌ MCP server file doesn't contain expected MCP code")
                    return False
        except Exception as e:
            print(f"❌ Error reading MCP server file: {str(e)}")
            return False
    else:
        print(f"❌ MCP server file not found: {server_path}")
        return False

def test_claude_desktop_config():
    """Test Claude Desktop configuration."""
    print("\n⚙️ Testing Claude Desktop Configuration...")
    
    # Check project config file
    project_config = Path("/Users/wseke/Desktop/PDFParseV2/claude_desktop_config.json")
    if project_config.exists():
        print(f"✅ Project config file exists: {project_config}")
        try:
            with open(project_config, 'r') as f:
                config = json.load(f)
                if "mcpServers" in config:
                    print("✅ Project config has mcpServers section")
                    return True
                else:
                    print("❌ Project config missing mcpServers section")
                    return False
        except Exception as e:
            print(f"❌ Error reading project config: {str(e)}")
            return False
    else:
        print(f"❌ Project config file not found: {project_config}")
        return False

def test_claude_desktop_installation():
    """Test if Claude Desktop is installed."""
    print("\n🖥️ Testing Claude Desktop Installation...")
    
    # Check common Claude Desktop locations
    possible_locations = [
        Path.home() / "Library" / "Application Support" / "Claude",
        Path.home() / "Library" / "Application Support" / "claude",
        Path.home() / ".config" / "Claude",
        Path.home() / ".config" / "claude",
    ]
    
    for location in possible_locations:
        if location.exists():
            print(f"✅ Claude Desktop directory found: {location}")
            
            # Check for config file
            config_file = location / "claude_desktop_config.json"
            if config_file.exists():
                print(f"✅ Claude Desktop config file exists: {config_file}")
                return True
            else:
                print(f"⚠️  Claude Desktop config file not found: {config_file}")
    
    print("❌ Claude Desktop installation not found")
    return False

def test_pdf_samples():
    """Test if PDF samples are available for testing."""
    print("\n📄 Testing PDF Samples...")
    
    pdf_dir = Path("/Users/wseke/Desktop/PDFParseV2/training_data/pdf_csv_pairs")
    
    if pdf_dir.exists():
        pdf_files = list(pdf_dir.glob("*.pdf"))
        if pdf_files:
            print(f"✅ Found {len(pdf_files)} PDF samples for testing")
            print(f"   Sample: {pdf_files[0].name}")
            return True
        else:
            print("❌ No PDF samples found")
            return False
    else:
        print(f"❌ PDF samples directory not found: {pdf_dir}")
        return False

def create_test_config():
    """Create a test configuration file."""
    print("\n🛠️ Creating Test Configuration...")
    
    config = {
        "mcpServers": {
            "pdf-field-modifier": {
                "command": "python3",
                "args": [
                    "/Users/wseke/Desktop/PDFParseV2/src/pdf_modifier/mcp_server.py"
                ],
                "cwd": "/Users/wseke/Desktop/PDFParseV2",
                "env": {
                    "PYTHONPATH": "/Users/wseke/Desktop/PDFParseV2"
                },
                "description": "PDF Field Modifier - AI-powered PDF form field renaming engine"
            }
        },
        "global": {
            "allowAnalytics": False,
            "logLevel": "info"
        }
    }
    
    output_path = Path("/Users/wseke/Desktop/PDFParseV2/claude_desktop_config_test.json")
    
    try:
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Test configuration created: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating test configuration: {str(e)}")
        return False

def test_mcp_server_startup():
    """Test MCP server startup (basic syntax check)."""
    print("\n🚀 Testing MCP Server Startup...")
    
    try:
        # Test basic syntax by importing the module
        sys.path.insert(0, "/Users/wseke/Desktop/PDFParseV2/src/pdf_modifier")
        
        # Try to import the server module
        spec = importlib.util.spec_from_file_location(
            "mcp_server", 
            "/Users/wseke/Desktop/PDFParseV2/src/pdf_modifier/mcp_server.py"
        )
        
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print("✅ MCP server module loaded successfully")
            return True
        else:
            print("❌ Failed to load MCP server module")
            return False
            
    except Exception as e:
        print(f"❌ MCP server startup test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🔧 PDFParseV2 MCP Setup Verification")
    print("=" * 50)
    
    tests = [
        ("Python Version", test_python_version),
        ("MCP Dependencies", test_mcp_dependencies),
        ("MCP Server File", test_mcp_server_file),
        ("Claude Desktop Config", test_claude_desktop_config),
        ("Claude Desktop Installation", test_claude_desktop_installation),
        ("PDF Samples", test_pdf_samples),
        ("MCP Server Startup", test_mcp_server_startup),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} - Exception: {str(e)}")
            results.append((test_name, False))
    
    # Create test configuration regardless of other results
    create_test_config()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MCP setup is ready.")
    else:
        print("⚠️  Some tests failed. Check individual results above.")
        
    print("\n📋 Next Steps:")
    print("1. Fix any failed tests above")
    print("2. Copy claude_desktop_config_test.json to Claude Desktop's config directory")
    print("3. Restart Claude Desktop")
    print("4. Test MCP tools in Claude Desktop")

if __name__ == "__main__":
    main()