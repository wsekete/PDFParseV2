# PDFParseV2 - Organized Project Structure

## 📁 Directory Structure

```
PDFParseV2/
├── src/                          # Source code
│   └── pdf_modifier/
│       ├── __init__.py
│       ├── mcp_server.py         # Main MCP server
│       └── pypdfform_field_renamer.py  # PyPDFForm wrapper
├── docs/                         # Documentation
│   ├── analysis/                 # Analysis documents
│   │   ├── CLEANUP_SUMMARY.md
│   │   ├── LIFE_1528Q_STRUCTURE_ANALYSIS.md
│   │   └── PYPDFFORM_ANALYSIS.md
│   ├── guides/                   # Setup and usage guides
│   │   ├── CLAUDE_DESKTOP_INSTRUCTIONS.md
│   │   ├── CLAUDE_DESKTOP_QUICK_SETUP.md
│   │   └── MCP_VERIFICATION_GUIDE.md
│   └── results/                  # Task results and validation reports
│       ├── PHASE1_VALIDATION_SUMMARY.md
│       └── TASK_2_1_*_RESULTS.md
├── scripts/                      # Utility scripts
│   ├── basic_test.py
│   ├── setup_claude_desktop.py
│   └── validate_*.py
├── tests/                        # Test files
│   ├── unit/                     # Unit tests
│   │   ├── test_mcp_server.py
│   │   └── test_pypdfform_*.py
│   ├── integration/              # Integration tests
│   │   └── test_life_1528q_enhanced.py
│   └── mcp/                      # MCP-specific tests
│       └── test_mcp_enhanced_tools.py
├── examples/                     # Example usage scripts
├── training_data/                # Training datasets and PDF samples
│   ├── Clean Field Data - Sheet1.csv
│   └── pdf_csv_pairs/
├── backups/                      # Backup files
├── venv/                        # Virtual environment (ignored)
├── .gitignore                   # Git ignore rules
├── claude_desktop_config.json   # Claude Desktop configuration
├── requirements.txt             # Python dependencies
├── CLAUDE.md                    # Main project documentation
└── README.md                    # Project overview
```

## 🎯 Key Files

### Essential Files (Root Directory)
- `CLAUDE.md` - Main project documentation
- `README.md` - Project overview and quick start
- `claude_desktop_config.json` - Claude Desktop MCP configuration
- `requirements.txt` - Python dependencies
- `pyproject.toml` - Project metadata

### Core Source Code
- `src/pdf_modifier/mcp_server.py` - Main MCP server with 3 tools
- `src/pdf_modifier/pypdfform_field_renamer.py` - PyPDFForm wrapper

### Documentation
- `docs/guides/` - Setup and usage instructions
- `docs/analysis/` - Technical analysis and cleanup summaries
- `docs/results/` - Task results and validation reports

### Development
- `scripts/` - Utility scripts for testing and setup
- `tests/` - Organized test suite (unit, integration, mcp)
- `examples/` - Example usage scripts

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Claude Desktop**:
   ```bash
   python scripts/setup_claude_desktop.py
   ```

3. **Test the setup**:
   ```bash
   python scripts/basic_test.py
   ```

4. **Read the documentation**:
   - Start with `CLAUDE.md` for full project overview
   - Check `docs/guides/CLAUDE_DESKTOP_INSTRUCTIONS.md` for setup

## 📦 Dependencies

See `requirements.txt` for the complete list. Key dependencies:
- `PyPDFForm==3.1.2` - PDF field modification
- `mcp==0.2.0` - Claude Desktop integration
- `pdfplumber==0.7.6` - PDF text extraction

## 🔧 Development

### Running Tests
```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests  
python -m pytest tests/integration/

# MCP tests
python -m pytest tests/mcp/
```

### Adding New Features
1. Add source code to `src/pdf_modifier/`
2. Add tests to appropriate `tests/` subdirectory
3. Update documentation in `docs/`
4. Add utility scripts to `scripts/` if needed

## 📝 File Organization Rules

### What Goes Where
- **Root directory**: Only essential files (README, CLAUDE.md, config files)
- **`src/`**: All source code
- **`docs/`**: All documentation, organized by type
- **`scripts/`**: Utility scripts and tools
- **`tests/`**: All test files, organized by type
- **`examples/`**: Example usage scripts
- **`training_data/`**: Training datasets (preserved)

### File Naming
- Documentation: `UPPERCASE_WITH_UNDERSCORES.md`
- Scripts: `lowercase_with_underscores.py`
- Tests: `test_*.py`
- Source: `lowercase_with_underscores.py`

## 🎉 Benefits of Organization

### For Developers
- **Clear structure**: Easy to find files
- **Logical grouping**: Related files together
- **Clean root**: No clutter in main directory
- **Scalable**: Easy to add new files in right place

### For Users
- **Simple navigation**: Clear directory purpose
- **Better documentation**: Organized guides and analysis
- **Easy setup**: Scripts in dedicated directory
- **Clean workflow**: Logical file organization

## 📊 Before/After

### Before (Unorganized)
- 25+ files in root directory
- Mixed documentation, scripts, and tests
- Hard to find specific files
- Cluttered and confusing

### After (Organized)
- 5 essential files in root
- Clear directory structure
- Logical file grouping
- Professional project layout

---

**Last Updated**: 2025-07-08  
**Status**: Project structure organized and clean  
**Next**: Continue with development using organized structure