"""Basic import tests to verify package structure."""


def test_import_pdf_parser():
    """Test that pdf_parser module can be imported."""
    try:
        import src.pdf_parser

        assert True
    except ImportError:
        assert False, "Failed to import src.pdf_parser"


def test_import_mcp_tools():
    """Test that mcp_tools module can be imported."""
    try:
        import src.mcp_tools

        assert True
    except ImportError:
        assert False, "Failed to import src.mcp_tools"


def test_import_naming_engine():
    """Test that naming_engine module can be imported."""
    try:
        import src.naming_engine

        assert True
    except ImportError:
        assert False, "Failed to import src.naming_engine"


def test_import_workflow():
    """Test that workflow module can be imported."""
    try:
        import src.workflow

        assert True
    except ImportError:
        assert False, "Failed to import src.workflow"


def test_python_version():
    """Test that Python version is 3.8+."""
    import sys

    assert sys.version_info >= (3, 8), f"Python 3.8+ required, got {sys.version_info}"
