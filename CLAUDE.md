# PDFParseV2 - Project Documentation

## Project Overview

PDFParseV2 is an automated PDF form field naming system that uses Claude AI and MCP (Model Context Protocol) tools to intelligently rename PDF form fields according to a BEM-like naming convention. The system extracts field metadata, applies intelligent naming using established patterns from training data, and safely modifies PDFs with the new field names.

## Current Status

✅ **Project Setup Complete** (2025-01-24)
- Complete directory structure created
- GitHub repository connected: https://github.com/wsekete/PDFParseV2
- Dependencies configured (requirements.txt, requirements-dev.txt)
- CI/CD pipeline configured (GitHub Actions)
- Testing framework set up (pytest)
- Training data and PDF samples integrated

✅ **Phase 1: PDF Field Extractor - COMPLETE** (2025-01-24)
- ✅ Task 1.1: Dependencies & Basic Setup Complete
- ✅ Task 1.2: PyPDF2 Field Extraction Complete
- ✅ Task 1.3: Real PDF Testing Complete (Validated with training data)
- ✅ Task 1.4: Text Context Extraction Implementation Complete
- ✅ Task 1.5: Combine Field Data with Context Complete
- ✅ Task 1.6: Basic Field Relationship Processing Complete

✅ **Radio Button Detection System - COMPLETE** (2025-01-24)
- ✅ Phase 1: Enhanced PDF Annotation Processing (Real coordinates & field types)
- ✅ Phase 2: RadioGroup Container Detection (Parent-child relationships)
- ✅ Phase 3: Improved Field Relationship Processing (Pattern refinement)
- ✅ Phase 4: Output Structure Enhancement (CSV schema compatibility)

🎯 **Key Achievement**: Radio button detection COMPLETE! Perfect field extraction across all test forms!

## Complete Field Extraction Example

**LIFE-1528-Q Form Analysis** (73 total fields extracted, matching training data exactly):
- **5 RadioGroups**: `dividend--group`, `frequency--group`, `name-change--group`, `name-change_reason--group`, `stop--group`
- **20 RadioButtons**: Complete parent-child relationships with proper grouping
- **46 TextFields**: Form input fields with real coordinates and context
- **2 Signature fields**: Digital signature areas

**FAF-0485AO Form Analysis** (25 total fields extracted, all CheckBox types):
- **25 CheckBoxes**: Customer acknowledgment fields with proper PDF flag detection
- **0 RadioGroups/RadioButtons**: Correctly identified as CheckBox-only form

**Field Types Detected**:
- **RadioGroups**: Container fields with BEM naming (`--group` suffix) and `/Kids` arrays
- **RadioButtons**: Child fields with proper parent ID relationships and PDF flag detection
- **CheckBoxes**: Standalone form controls with PDF flag analysis (no `/Ff` flags = CheckBox)
- **TextFields**: Input fields with coordinate extraction (x, y, width, height)
- **Signature fields**: Digital signature areas for document validation
- **Proper hierarchies**: RadioGroup → RadioButton parent-child relationships preserved

**Sample Field Structure**:
```
address-change_owner (RadioButton)
├── Type: RadioButton  
├── Label: Policy Owner
├── Coordinates: x=35.9, y=430.0
├── Parent: address-change--group
└── Context: surrounding_text, text_above extracted
```

## Design Philosophy

⚠️ **IMPORTANT**: We need to be thorough, flexible, and simple. Avoid hard-coding rule-based solutions. We're going to leverage AI to make this happen.

The system is designed for AI-powered adaptability rather than rigid rule-based processing. This allows the system to:
- Handle new PDF form structures without code changes
- Learn from training data patterns dynamically
- Adapt to different naming conventions and field relationships
- Scale across diverse form types and industries

## Architecture Overview

The system consists of four main components:

### 1. PDF Field Extractor (`src/pdf_parser/field_extractor.py`)
- Extracts comprehensive field metadata using PyPDF2 and pdfplumber
- Analyzes surrounding text context for each field
- Identifies field relationships and radio button groups
- Outputs structured data compatible with existing workflows

### 2. Intelligent Naming Engine (`src/naming_engine/`)
- Learns patterns from training data using machine learning techniques
- Applies BEM-like naming conventions (Block_Element__Modifier)
- Provides confidence scores and alternative suggestions
- Supports context-aware field categorization

### 3. PDF Field Modifier (`src/pdf_parser/field_modifier.py`)
- Safely modifies PDF field names while preserving functionality
- Creates automatic backups before modifications
- Validates changes and provides rollback capabilities
- Maintains radio button group relationships

### 4. Workflow Orchestrator (`src/workflow/`)
- Coordinates the complete process from extraction to modification
- Integrates with Claude for interactive review and refinement
- Provides comprehensive reporting and error handling
- Supports batch processing of multiple PDFs

## Training Data Structure

### Primary Training Dataset
**Location**: `training_data/Clean Field Data - Sheet1.csv`

**Schema**: 16 columns
```
id, type, formId, sectionId, parentId, order, label, apiName, custom, uuid, height, page, width, x, y, unifiedFieldId
```

**Sample Data**:
- 836,504+ field records
- TextField types with BEM naming: `contingent-benficiary_address`, `personal-information_city`
- Coordinate data for field positioning
- Section grouping with sectionId

### PDF/CSV Test Pairs
**Location**: `training_data/pdf_csv_pairs/`

**Contents**: 14 PDF/CSV pairs for testing
- AAF-0107AO.22, APO-1222-AX, APO-5309, FAF-0485AO, FAF-0578AO.6
- FAF-0582AO, FAF-0584AO, FAF-0635AO.5, FAFF-0009AO.13, FAFF-0042AO.7
- LAF-0119AO, LAF-0140AO, LIFE-1528-Q, W-4R

**CSV Format**: Extended schema with additional metadata
```
ID, Created at, Updated at, Label, Description, Form ID, Order, Api name, UUID, Type, Parent ID, Delete Parent ID, Acrofieldlabel, Section ID, Excluded, Partial label, Custom, Show group label, Height, Page, Width, X, Y, Unified field ID, Delete, Hidden, Toggle description
```

## BEM Naming Convention

The system uses a BEM-inspired naming convention:

- **Block**: Form section (e.g., `personal-information`, `contingent-benficiary`)
- **Element**: Field purpose (e.g., `name`, `address`, `ssn`)
- **Modifier**: Field variation (e.g., `monthly`, `gross`, `primary`)
- **Groups**: Radio button groups (e.g., `gender--group`)

### Examples from Training Data
```
personal-information_first-name-mi
personal-information_last-name
personal-information_ssn
personal-information_address
personal-information_city
personal-information_state
personal-information_zip
contingent-benficiary_address
contingent-benficiary_dob
sign-here_signature
sign-here_date
```

## Dependencies

### Core Dependencies (requirements.txt)
```
PyPDF2==3.0.1        # PDF form field extraction (NOTE: Updated from PyPDF5)
pdfplumber==0.7.6     # Text context extraction
pandas==2.1.3         # Data processing
mcp==0.2.0           # MCP framework integration
pydantic==2.5.0      # Data validation
click==8.1.7         # CLI interface
loguru==0.7.2        # Logging
```

### Development Dependencies (requirements-dev.txt)
```
pytest==7.4.3        # Testing framework
black==23.11.0       # Code formatting
flake8==6.1.0        # Linting
mypy==1.7.1          # Type checking
```

## Implementation Plan

### Phase 1: PDF Field Extractor (70% COMPLETE)
**Target**: Core field extraction with context analysis

**✅ Completed Implementation**:
1. ✅ Created `PDFFieldExtractor` class in `src/pdf_parser/field_extractor.py`
2. ✅ Implemented PyPDF2-based acrofield extraction using modern API (PdfReader)
3. ✅ Successfully extracts 10 fields from W-4R_parsed.pdf with correct BEM names
4. ✅ Implemented comprehensive text context extraction with pdfplumber
5. ✅ Added field processing with UUID generation and type detection
6. 🚧 Need to combine field metadata with context data (Task 1.5)

**🎯 Key Achievements**:
- **Real PDF Validation**: Successfully extracted fields: `personal-information_first-name-MI`, `personal-information_last-name`, `personal-information_SSN`, etc.
- **BEM Naming**: Training data already contains proper BEM format names
- **Modern API**: Updated to PyPDF2 3.0+ API (PdfReader, get_fields, get_object)
- **Robust Architecture**: Comprehensive error handling and logging

**Testing Results**:
- ✅ W-4R_parsed.pdf: 10 fields extracted, 3 pages processed
- ✅ Field names match training data exactly
- ✅ All field types correctly identified as TextField
- 🚧 Need coordinates from annotation processing for text context

### Phase 2: Consistent Naming Framework
**Target**: AI-powered field naming with training data integration

### Phase 3: Field Relationships & Context
**Target**: Radio button groups and section detection

### Phase 4: PDF Field Modifier
**Target**: Safe field renaming with backup functionality

### Phase 5: MCP Integration
**Target**: Claude Desktop integration

### Phase 6: Testing & Validation
**Target**: Comprehensive test suite and performance validation

## Development Workflow

### Documentation Updates
1. **After Each Phase**: Update this CLAUDE.md with implementation details, test results, and lessons learned
2. **Before Each GitHub Push**: Update CLAUDE.md with current status, completed features, and next steps
3. **Include in Commits**: Always include CLAUDE.md updates in commits for full context

### Testing Standards
- **Real PDF Testing**: Use actual PDF files from `pdf_csv_pairs/` directory
- **Schema Validation**: Ensure output exactly matches training data CSV format
- **Cross-Validation**: Compare generated names with existing correct mappings
- **Performance Testing**: Handle large PDFs efficiently

### Code Quality
- Black formatting (88 character line length)
- Flake8 linting compliance
- MyPy type checking
- Comprehensive docstrings
- 90%+ test coverage target

## Next Steps

### Immediate (Phase 1 - PDF Field Extractor)
1. Create `src/pdf_parser/field_extractor.py` with `PDFFieldExtractor` class
2. Implement `_extract_acrofields()` method using PyPDF2
3. Implement `_extract_text_context()` method using pdfplumber
4. Create data combination and field relationship processing
5. Test with W-4R_parsed.pdf and validate against W-4R_parsed_correct_mapping.csv

### Success Criteria for Phase 1
✅ Extract all form fields with complete metadata
✅ Generate context-aware field information  
✅ Output data matching existing CSV schema exactly
✅ Handle various real PDF types without errors
✅ Pass tests using real PDF samples from project

## Project Structure
```
PDFParseV2/
├── src/
│   ├── pdf_parser/          # PDF extraction and modification
│   ├── mcp_tools/           # MCP server implementations  
│   ├── naming_engine/       # AI naming logic
│   ├── workflow/            # Orchestration and coordination
│   └── interface/           # User interface components
├── training_data/           # Training datasets and PDF samples
│   ├── Clean Field Data - Sheet1.csv
│   └── pdf_csv_pairs/       # 14 PDF/CSV test pairs
├── tests/                   # Test suite with real PDF testing
├── docs/                    # Documentation
└── scripts/                 # Deployment and utility scripts
```

---

**Last Updated**: 2025-01-24  
**Phase**: 1 - PDF Field Extractor Implementation (COMPLETE)
**Status**: Perfect radio button detection and field extraction across all test forms
**Achievement**: All 73 fields from LIFE-1528-Q extracted with proper RadioGroup/RadioButton relationships