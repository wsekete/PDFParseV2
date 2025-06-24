#!/bin/bash
# scripts/initialize_project.sh

echo "🚀 Initializing PDFParseV2 project..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements-dev.txt
pip install -e .

# Setup pre-commit
echo "🔧 Setting up pre-commit hooks..."
pre-commit install

# Create environment file
echo "⚙️ Creating environment file..."
cp .env.example .env

# Run initial tests
echo "🧪 Running initial tests..."
pytest tests/test_basic_imports.py -v

# Check code quality
echo "🎨 Checking code quality..."
black --check src/ tests/ || echo "Run 'black src/ tests/' to format code"
flake8 src/ tests/ || echo "Fix flake8 issues before committing"

echo "✅ Project initialization complete!"
echo "Next steps:"
echo "1. Review and update .env file"
echo "2. Add training data to training_data/ directory"
echo "3. Start implementing components following the detailed plans"