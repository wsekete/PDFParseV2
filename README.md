# PDFParseV2

Automated PDF form field naming system using Claude and MCP tools.

## Overview

This project automates the process of naming PDF form fields (acrofields) according to a BEM-like naming convention. It extracts field metadata, applies intelligent naming using Claude AI, and modifies PDFs with the new field names.

## Features

- **PDF Field Extraction**: Comprehensive extraction of acrofield metadata with context analysis
- **Intelligent Naming**: AI-powered field naming using established patterns from training data
- **Safe Modification**: Conservative PDF updates that preserve field functionality and relationships
- **Interactive Review**: User control over the naming process through Claude's chat interface
- **MCP Integration**: Built as Model Context Protocol tools for seamless Claude Desktop integration
- **Backup & Recovery**: Automatic backup creation and rollback capabilities
- **Radio Group Handling**: Intelligent detection and naming of radio button groups

## Quick Start

### Installation

```bash
git clone https://github.com/[USERNAME]/PDFParseV2.git
cd PDFParseV2
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### Basic Usage

```python
from pdf_parser import extract_fields, modify_fields

# Extract fields from PDF
fields = extract_fields("input.pdf")

# Generate names using Claude (Interactive process through Claude Desktop)
# Upload PDF to Claude and say: "Process this PDF with intelligent field naming"

# Or use programmatically:
from workflow.orchestrator import PDFFieldNamingOrchestrator

orchestrator = PDFFieldNamingOrchestrator("training_data.csv")
result = await orchestrator.process_pdf_complete_workflow("input.pdf")
```

### Claude Desktop Usage

1. Deploy MCP servers (see deployment section)
2. Upload PDF to Claude Desktop
3. Say: "Process this PDF with intelligent field naming"
4. Review and refine suggestions
5. Download renamed PDF

## Architecture

The system consists of four main components:

### 1. PDF Field Extractor
- Extracts comprehensive field metadata using PyPDF2 and pdfplumber
- Analyzes surrounding text context for each field
- Identifies field relationships and radio button groups
- Outputs structured data compatible with existing workflows

### 2. PDF Field Modifier
- Safely modifies PDF field names while preserving functionality
- Creates automatic backups before modifications
- Validates changes and provides rollback capabilities
- Maintains radio button group relationships

### 3. Intelligent Naming Engine
- Learns patterns from training data using machine learning techniques
- Applies BEM-like naming conventions (Block_Element__Modifier)
- Provides confidence scores and alternative suggestions
- Supports context-aware field categorization

### 4. Workflow Orchestrator
- Coordinates the complete process from extraction to modification
- Integrates with Claude for interactive review and refinement
- Provides comprehensive reporting and error handling
- Supports batch processing of multiple PDFs

## Naming Convention

The system uses a BEM-inspired naming convention:

- **Block**: Form section (e.g., `owner-information`, `beneficiary`)
- **Element**: Field purpose (e.g., `name`, `email`, `account-number`)
- **Modifier**: Field variation (e.g., `monthly`, `gross`, `primary`)
- **Groups**: Radio button groups (e.g., `gender--group`)

### Examples
```
owner-information_name
account-information_routing-number
withdrawal-options_frequency__monthly
beneficiary_relationship
signatures_owner
gender--group
gender_male
gender_female
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run integration tests
pytest --integration

# Run performance tests
pytest --performance
```

### Code Quality

```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/

# Sort imports
isort src/ tests/
```

## Configuration

Copy `.env.example` to `.env` and adjust settings:

```bash
cp .env.example .env
# Edit .env with your preferred settings
```

## License

MIT License - see LICENSE file for details.