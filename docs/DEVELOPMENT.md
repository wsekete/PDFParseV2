# Development Guide

## Setup Development Environment

1. Clone repository and create virtual environment
2. Install development dependencies: `pip install -r requirements-dev.txt`
3. Install pre-commit hooks: `pre-commit install`
4. Copy environment file: `cp .env.example .env`

## Project Structure

```
PDFParseV2/
├── src/                          # Source code
│   ├── pdf_parser/              # PDF extraction and modification
│   ├── mcp_tools/               # MCP server implementations
│   ├── naming_engine/           # AI naming logic
│   ├── workflow/                # Orchestration and coordination
│   └── interface/               # User interface components
├── tests/                       # Test suite
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── fixtures/                # Test data
├── docs/                        # Documentation
├── examples/                    # Usage examples
└── scripts/                     # Deployment and utility scripts
```

## Testing Strategy

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Validate performance requirements

## Code Quality Standards

- Black formatting (line length 88)
- Flake8 linting
- MyPy type checking
- 90%+ test coverage
- Comprehensive docstrings