#!/usr/bin/env python3
"""
Script to organize the PDFParseV2 project directory structure.
"""

import os
import shutil
from pathlib import Path

def create_directory_structure():
    """Create the organized directory structure."""
    project_root = Path("/Users/wseke/Desktop/PDFParseV2")
    
    # Create new directory structure
    directories = [
        "docs/analysis",
        "docs/guides", 
        "docs/results",
        "scripts",
        "tests/unit",
        "tests/integration", 
        "tests/mcp",
        "examples"
    ]
    
    for dir_path in directories:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {full_path}")

if __name__ == "__main__":
    create_directory_structure()