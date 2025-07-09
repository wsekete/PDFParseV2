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

def organize_files():
    """Organize files into appropriate directories."""
    project_root = Path("/Users/wseke/Desktop/PDFParseV2")
    
    # Documentation files to move to docs/guides
    doc_files = [
        "CLAUDE_DESKTOP_INSTRUCTIONS.md",
        "CLAUDE_DESKTOP_QUICK_SETUP.md", 
        "CLAUDE_DESKTOP_SETUP.md",
        "CLAUDE_DESKTOP_VERIFICATION_GUIDE.md",
        "MCP_VERIFICATION_GUIDE.md"
    ]
    
    for file_name in doc_files:
        src = project_root / file_name
        dst = project_root / "docs" / "guides" / file_name
        if src.exists():
            shutil.move(str(src), str(dst))
            print(f"Moved {file_name} to docs/guides/")
    
    # Analysis files to move to docs/analysis
    analysis_files = [
        "LIFE_1528Q_STRUCTURE_ANALYSIS.md",
        "PYPDFFORM_ANALYSIS.md",
        "CLEANUP_SUMMARY.md",
        "PROJECT_CLEANUP_SUMMARY.md",
        "IMPLEMENTATION_COMPLETE.md",
        "WRAPPER_FIX_SUMMARY.md"
    ]
    
    for file_name in analysis_files:
        src = project_root / file_name
        dst = project_root / "docs" / "analysis" / file_name
        if src.exists():
            shutil.move(str(src), str(dst))
            print(f"Moved {file_name} to docs/analysis/")
    
    # Results files to move to docs/results
    results_files = [
        "PHASE1_VALIDATION_SUMMARY.md",
        "TASK_2_1_2_RESULTS.md",
        "TASK_2_1_3_RESULTS.md", 
        "TASK_2_1_4_RESULTS.md"
    ]
    
    for file_name in results_files:
        src = project_root / file_name
        dst = project_root / "docs" / "results" / file_name
        if src.exists():
            shutil.move(str(src), str(dst))
            print(f"Moved {file_name} to docs/results/")
    
    # Script files to move to scripts/
    script_files = [
        "basic_test.py",
        "direct_test.py",
        "examine_w4r_fields.py",
        "fix_claude_desktop_config.py",
        "quick_test_all_pdfs.py",
        "quick_wrapper_test.py",
        "setup_claude_desktop.py",
        "simple_pypdfform_test.py",
        "validate_fix.py",
        "validate_phase1.py",
        "commit_changes.sh",
        "organize_structure.py",
        "organize_project.py"
    ]
    
    for file_name in script_files:
        src = project_root / file_name
        dst = project_root / "scripts" / file_name
        if src.exists():
            shutil.move(str(src), str(dst))
            print(f"Moved {file_name} to scripts/")
    
    # Test files to move to tests/
    test_files = [
        "test_complex_life_1528q.py",
        "test_comprehensive_all_pdfs.py",
        "test_enhanced_wrapper.py",
        "test_life_1528q_simple.py",
        "test_mcp_server.py",
        "test_mcp_server_basic.py",
        "test_mcp_setup.py",
        "test_pypdfform_w4r.py",
        "test_wrapper_fix.py"
    ]
    
    for file_name in test_files:
        src = project_root / file_name
        dst = project_root / "tests" / "unit" / file_name
        if src.exists():
            shutil.move(str(src), str(dst))
            print(f"Moved {file_name} to tests/unit/")
    
    # Move existing test files to proper structure
    existing_integration_tests = project_root / "tests" / "integration"
    existing_mcp_tests = project_root / "tests" / "mcp"
    
    if existing_integration_tests.exists():
        for file_path in existing_integration_tests.glob("*.py"):
            print(f"Integration test already in place: {file_path.name}")
    
    if existing_mcp_tests.exists():
        for file_path in existing_mcp_tests.glob("*.py"):
            print(f"MCP test already in place: {file_path.name}")

def cleanup_temp_and_backup():
    """Clean up temporary and backup files."""
    project_root = Path("/Users/wseke/Desktop/PDFParseV2")
    
    # Remove temp directory if it exists
    temp_dir = project_root / "temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        print("Removed temp/ directory")
    
    # Move backups to a single backups directory
    backup_dir = project_root / "backups"
    if backup_dir.exists():
        print(f"Backups directory already exists with {len(list(backup_dir.iterdir()))} items")

def main():
    """Main function to organize the project."""
    print("=== PDFParseV2 Project Organization ===")
    print("Step 1: Creating directory structure...")
    create_directory_structure()
    
    print("\nStep 2: Organizing files...")
    organize_files()
    
    print("\nStep 3: Cleaning up temporary files...")
    cleanup_temp_and_backup()
    
    print("\n=== Organization Complete ===")
    print("Project structure has been organized.")

if __name__ == "__main__":
    main()