#!/usr/bin/env python3
"""
Claude Desktop Setup Script
PDFParseV2 - Automated Claude Desktop Integration Setup

This script automatically configures Claude Desktop for MCP integration.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

def get_claude_desktop_config_path() -> Optional[Path]:
    """Get the Claude Desktop configuration file path for the current platform."""
    
    if sys.platform == "darwin":  # macOS
        config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "win32":  # Windows
        config_path = Path(os.environ["APPDATA"]) / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        config_path = Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
    
    return config_path

def ensure_directory_exists(path: Path) -> bool:
    """Ensure the directory exists, creating it if necessary."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"❌ Error creating directory {path.parent}: {e}")
        return False

def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "mcp",
        "PyPDF2", 
        "PyPDFForm",
        "pdfplumber",
        "pandas",
        "pydantic",
        "loguru"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def create_mcp_config() -> Dict[str, Any]:
    """Create the MCP server configuration."""
    
    project_root = Path("/Users/wseke/Desktop/PDFParseV2")
    
    config = {
        "mcpServers": {
            "pdf-field-modifier": {
                "command": "python3",
                "args": [
                    str(project_root / "src" / "pdf_modifier" / "mcp_server.py")
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
    
    return config

def backup_existing_config(config_path: Path) -> Optional[Path]:
    """Backup existing configuration if it exists."""
    if config_path.exists():
        backup_path = config_path.with_suffix(".json.backup")
        try:
            shutil.copy2(config_path, backup_path)
            print(f"✅ Backed up existing config to: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Error backing up config: {e}")
            return None
    return None

def install_config(config: Dict[str, Any], config_path: Path) -> bool:
    """Install the configuration file."""
    try:
        # Ensure directory exists
        if not ensure_directory_exists(config_path):
            return False
        
        # Write configuration
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration installed to: {config_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error installing configuration: {e}")
        return False

def verify_mcp_server() -> bool:
    """Verify the MCP server file exists and is valid."""
    project_root = Path("/Users/wseke/Desktop/PDFParseV2")
    server_path = project_root / "src" / "pdf_modifier" / "mcp_server.py"
    
    if not server_path.exists():
        print(f"❌ MCP server file not found: {server_path}")
        return False
    
    try:
        with open(server_path, 'r') as f:
            content = f.read()
            if "Server" in content and "MCP" in content:
                print(f"✅ MCP server file verified: {server_path}")
                return True
            else:
                print(f"❌ MCP server file doesn't contain expected content")
                return False
    except Exception as e:
        print(f"❌ Error reading MCP server file: {e}")
        return False

def test_mcp_server() -> bool:
    """Test the MCP server by trying to import it."""
    print("🧪 Testing MCP server...")
    
    try:
        project_root = Path("/Users/wseke/Desktop/PDFParseV2")
        sys.path.insert(0, str(project_root))
        
        # Try to import the server
        from src.pdf_modifier import mcp_server
        
        # Check if the server has the expected structure
        if hasattr(mcp_server, 'app') and hasattr(mcp_server, 'test_connection'):
            print("✅ MCP server test passed")
            return True
        else:
            print("❌ MCP server missing expected components")
            return False
            
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Claude Desktop MCP Setup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Setup failed: Missing dependencies")
        print("Please install dependencies first: pip install -r requirements.txt")
        return False
    
    # Verify MCP server
    if not verify_mcp_server():
        print("\n❌ Setup failed: MCP server issues")
        return False
    
    # Test MCP server
    if not test_mcp_server():
        print("\n❌ Setup failed: MCP server test failed")
        return False
    
    # Get configuration path
    config_path = get_claude_desktop_config_path()
    if not config_path:
        print("\n❌ Setup failed: Unable to determine Claude Desktop config path")
        return False
    
    print(f"\n📍 Claude Desktop config path: {config_path}")
    
    # Backup existing config
    backup_path = backup_existing_config(config_path)
    
    # Create MCP configuration
    config = create_mcp_config()
    
    # Install configuration
    if not install_config(config, config_path):
        print("\n❌ Setup failed: Unable to install configuration")
        return False
    
    # Success
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Restart Claude Desktop")
    print("2. Test MCP tools in Claude Desktop:")
    print("   - test_connection")
    print("   - analyze_pdf_fields")
    print("   - modify_pdf_fields")
    print("3. Upload a PDF and try the workflow")
    
    if backup_path:
        print(f"\nNote: Your previous config was backed up to: {backup_path}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)