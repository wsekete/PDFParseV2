#!/usr/bin/env python3
"""
Fix Claude Desktop Configuration for MCP Server
PDFParseV2 - Claude Desktop Integration Fix

This script fixes the Claude Desktop configuration to point to the correct MCP server path.
"""

import json
import time
from pathlib import Path

def fix_claude_desktop_config():
    """Fix the Claude Desktop configuration."""
    print("🔧 Fixing Claude Desktop configuration...")
    
    config_path = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    project_root = Path(__file__).parent.absolute()
    
    # Check current config
    if config_path.exists():
        print(f"📖 Reading existing config: {config_path}")
        with open(config_path, 'r') as f:
            current_config = json.load(f)
        
        print("Current PDF server config:")
        pdf_server = current_config.get('mcpServers', {}).get('pdf-field-modifier')
        if pdf_server:
            print(f"  Path: {pdf_server.get('args', [''])[0]}")
            print(f"  Command: {pdf_server.get('command', 'N/A')}")
    
    # Create correct configuration
    correct_server_path = project_root / "src/pdf_modifier/mcp_server.py"
    
    new_config = {
        "mcpServers": {
            "pdf-field-modifier": {
                "command": "python3",
                "args": [str(correct_server_path)],
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
    
    # Preserve other MCP servers if they exist
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                existing_config = json.load(f)
            
            # Merge with existing config
            if 'mcpServers' in existing_config:
                for server_name, server_config in existing_config['mcpServers'].items():
                    if server_name != 'pdf-field-modifier':
                        new_config['mcpServers'][server_name] = server_config
            
            # Create backup
            backup_path = config_path.with_suffix(f'.json.backup.{int(time.time())}')\n            with open(backup_path, 'w') as f:
                json.dump(existing_config, f, indent=2)
            print(f"✅ Backup created: {backup_path}")
            
        except Exception as e:
            print(f"⚠️  Could not create backup: {e}")
    
    # Write the corrected configuration
    try:
        with open(config_path, 'w') as f:
            json.dump(new_config, f, indent=2)
        
        print("✅ Claude Desktop configuration updated successfully!")
        print(f"New server path: {correct_server_path}")
        print(f"Project root: {project_root}")
        
        # Verify the server file exists
        if correct_server_path.exists():
            print("✅ MCP server file exists and is accessible")
        else:
            print("❌ WARNING: MCP server file does not exist!")
            
        return True
        
    except Exception as e:
        print(f"❌ Failed to update Claude Desktop config: {e}")
        return False

def show_verification_steps():
    """Show steps to verify the configuration works."""
    print("\n📋 VERIFICATION STEPS:")
    print("1. Restart Claude Desktop completely")
    print("2. In Claude Desktop, try: 'Use the test_connection tool'")
    print("3. If that works, try: 'Use the analyze_pdf_fields tool on training_data/pdf_csv_pairs/W-4R_parsed.pdf'")
    print("4. For field extraction: 'Use the extract_pdf_fields_enhanced tool on training_data/pdf_csv_pairs/W-4R_parsed.pdf'")
    print("\nIf tools don't appear, check:")
    print("- Claude Desktop was fully restarted")
    print("- The MCP server path exists")
    print("- Python dependencies are installed")

if __name__ == "__main__":
    print("=" * 80)
    print("🔧 CLAUDE DESKTOP MCP CONFIGURATION FIX")
    print("=" * 80)
    
    success = fix_claude_desktop_config()
    
    if success:
        show_verification_steps()
        print("\n🎉 Configuration fix completed!")
    else:
        print("\n❌ Configuration fix failed!")
        print("Please check the error messages above.")