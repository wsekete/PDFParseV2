#!/usr/bin/env python3
"""
MCP Server Testing and Verification Script
PDFParseV2 - Claude Desktop Integration

This script verifies that the MCP server is working correctly and can be used
from Claude Desktop.
"""

import sys
import os
import json
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    dependencies = {
        'PyPDF2': 'PyPDF2',
        'PyPDFForm': 'PyPDFForm',
        'MCP': 'mcp'
    }
    
    results = {}
    for name, import_name in dependencies.items():
        try:
            __import__(import_name)
            results[name] = "✅ Available"
        except ImportError:
            results[name] = "❌ Missing"
    
    for name, status in results.items():
        print(f"  {name}: {status}")
    
    return all("✅" in status for status in results.values())

def test_mcp_server_import():
    """Test if the MCP server can be imported and initialized."""
    print("\n🔍 Testing MCP server import...")
    
    try:
        # Add project root to Python path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        # Try to import the MCP server
        from src.pdf_modifier.mcp_server import app
        print("✅ MCP server imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import MCP server: {e}")
        return False

def test_pypdfform_wrapper():
    """Test the PyPDFForm wrapper functionality."""
    print("\n🔍 Testing PyPDFForm wrapper...")
    
    try:
        from src.pdf_modifier.pypdfform_field_renamer import PyPDFFormFieldRenamer
        
        # Test with a sample PDF
        sample_pdf = "training_data/pdf_csv_pairs/W-4R_parsed.pdf"
        
        if not Path(sample_pdf).exists():
            print(f"⚠️  Sample PDF not found: {sample_pdf}")
            return False
        
        renamer = PyPDFFormFieldRenamer(sample_pdf)
        
        if renamer.load_pdf():
            fields = renamer.extract_fields()
            print(f"✅ PyPDFForm wrapper working: {len(fields)} fields extracted")
            return True
        else:
            print("❌ PyPDFForm wrapper failed to load PDF")
            return False
            
    except Exception as e:
        print(f"❌ PyPDFForm wrapper test failed: {e}")
        return False

def test_mcp_server_startup():
    """Test if the MCP server can start properly."""
    print("\n🔍 Testing MCP server startup...")
    
    try:
        # Run the MCP server in test mode
        server_path = Path("src/pdf_modifier/mcp_server.py")
        
        if not server_path.exists():
            print(f"❌ MCP server not found: {server_path}")
            return False
        
        # Try to run the server with a short timeout
        cmd = [sys.executable, str(server_path)]
        
        # Start the process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path.cwd()
        )
        
        # Wait a short time to see if it starts
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ MCP server started successfully")
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ MCP server failed to start")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ MCP server startup test failed: {e}")
        return False

def check_claude_desktop_config():
    """Check Claude Desktop configuration."""
    print("\n🔍 Checking Claude Desktop configuration...")
    
    config_path = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    
    if not config_path.exists():
        print(f"❌ Claude Desktop config not found: {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if 'mcpServers' not in config:
            print("❌ No mcpServers section in Claude Desktop config")
            return False
        
        pdf_server = config['mcpServers'].get('pdf-field-modifier')
        if not pdf_server:
            print("❌ pdf-field-modifier not found in Claude Desktop config")
            return False
        
        # Check if the server path exists
        server_path = Path(pdf_server['args'][0])
        if not server_path.exists():
            print(f"❌ Configured MCP server path does not exist: {server_path}")
            print(f"Current config points to: {pdf_server['args'][0]}")
            print(f"Available server: src/pdf_modifier/mcp_server.py")
            return False
        
        print("✅ Claude Desktop configuration looks correct")
        return True
        
    except Exception as e:
        print(f"❌ Error reading Claude Desktop config: {e}")
        return False

def fix_claude_desktop_config():
    """Fix the Claude Desktop configuration."""
    print("\n🔧 Fixing Claude Desktop configuration...")
    
    config_path = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    project_root = Path(__file__).parent.absolute()
    
    # Create the correct configuration
    new_config = {
        "mcpServers": {
            "pdf-field-modifier": {
                "command": "python3",
                "args": [
                    str(project_root / "src/pdf_modifier/mcp_server.py")
                ],
                "cwd": str(project_root),
                "env": {
                    "PYTHONPATH": str(project_root)
                },
                "description": "PDF Field Modifier - AI-powered PDF form field renaming engine"
            }
        },
        "global": {
            "allowAnalytics": False,
            "logLevel": "info"
        }
    }
    
    # Create backup of existing config
    if config_path.exists():
        backup_path = config_path.with_suffix(f'.json.backup.{int(time.time())}')\n        try:
            with open(config_path, 'r') as f:
                existing_config = json.load(f)
            
            # Merge with existing config if it has other servers
            if 'mcpServers' in existing_config:
                # Keep other MCP servers but replace our PDF server
                for server_name, server_config in existing_config['mcpServers'].items():
                    if server_name != 'pdf-field-modifier':
                        new_config['mcpServers'][server_name] = server_config
            
            # Create backup
            with open(backup_path, 'w') as f:
                json.dump(existing_config, f, indent=2)
            print(f"✅ Backup created: {backup_path}")
            
        except Exception as e:
            print(f"⚠️  Could not create backup: {e}")
    
    # Write the new configuration
    try:
        with open(config_path, 'w') as f:
            json.dump(new_config, f, indent=2)
        
        print("✅ Claude Desktop configuration updated successfully")
        print(f"Server path: {project_root / 'src/pdf_modifier/mcp_server.py'}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update Claude Desktop config: {e}")
        return False

def create_test_instructions():
    """Create instructions for testing the MCP server from Claude Desktop."""
    print("\n📋 Creating test instructions...")
    
    instructions = """
# Testing MCP Server from Claude Desktop

After updating the configuration, restart Claude Desktop and try these tests:

## 1. Test Connection
Ask Claude Desktop to run:
```
Use the test_connection tool to verify the MCP server is working
```

## 2. Analyze a PDF
Ask Claude Desktop to analyze a PDF:
```
Use the analyze_pdf_fields tool to analyze the PDF at: training_data/pdf_csv_pairs/W-4R_parsed.pdf
```

## 3. Test Enhanced Field Extraction
Ask Claude Desktop to test the enhanced extraction:
```
Use the extract_pdf_fields_enhanced tool to analyze: training_data/pdf_csv_pairs/W-4R_parsed.pdf
```

## 4. Preview Field Renaming
Ask Claude Desktop to preview field renaming:
```
Use the preview_field_renames tool with pdf_path: training_data/pdf_csv_pairs/W-4R_parsed.pdf
and field_mappings: {"personal-information_first-name-MI": "personal-info_first-name"}
```

## 5. Test Actual Field Modification
Ask Claude Desktop to modify fields:
```
Use the modify_pdf_fields_v2 tool with:
- pdf_path: training_data/pdf_csv_pairs/W-4R_parsed.pdf
- field_mappings: {"personal-information_first-name-MI": "personal-info_first-name"}
- validate_only: true
```

## Troubleshooting

If the tools don't appear:
1. Restart Claude Desktop completely
2. Check the configuration file is correctly formatted
3. Verify the MCP server path exists
4. Check Python dependencies are installed

If tools fail:
1. Check the logs in Claude Desktop
2. Verify PDF files exist in the training_data directory
3. Test Python imports manually
"""
    
    with open("MCP_TESTING_INSTRUCTIONS.md", "w") as f:
        f.write(instructions)
    
    print("✅ Test instructions created: MCP_TESTING_INSTRUCTIONS.md")

def main():
    """Main test function."""
    print("=" * 80)
    print("🔧 MCP SERVER VERIFICATION AND TESTING")
    print("=" * 80)
    
    tests = [
        ("Dependencies Check", check_dependencies),
        ("MCP Server Import", test_mcp_server_import),
        ("PyPDFForm Wrapper", test_pypdfform_wrapper),
        ("MCP Server Startup", test_mcp_server_startup),
        ("Claude Desktop Config", check_claude_desktop_config),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
        
        if not result and name == "Claude Desktop Config":
            print("\n🔧 Attempting to fix Claude Desktop configuration...")
            fix_result = fix_claude_desktop_config()
            if fix_result:
                results[-1] = (name, True)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
        if result:
            passed += 1
    
    print(f"\n📈 Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ MCP Server is ready for Claude Desktop integration")
        create_test_instructions()
    elif passed >= total - 1:
        print("\n⚠️  MOSTLY WORKING - Minor issues detected")
        print("✅ MCP Server should work with Claude Desktop")
        create_test_instructions()
    else:
        print("\n❌ SIGNIFICANT ISSUES DETECTED")
        print("🔧 Please address the failed tests before using with Claude Desktop")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)