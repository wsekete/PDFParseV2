#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

print("Starting basic test...")

# Test 1: PyPDFForm with W-4R (known working)
pdf_path = "training_data/pdf_csv_pairs/W-4R_parsed.pdf"
print(f"Testing {pdf_path}...")

try:
    from PyPDFForm import PdfWrapper
    pdf = PdfWrapper(pdf_path)
    sample_data = pdf.sample_data
    print(f"W-4R: {len(sample_data)} fields detected")
except Exception as e:
    print(f"W-4R failed: {e}")

# Test 2: PyPDFForm with LIFE-1528-Q (complex)
pdf_path = "training_data/pdf_csv_pairs/LIFE-1528-Q__parsed.pdf"
print(f"Testing {pdf_path}...")

try:
    from PyPDFForm import PdfWrapper
    pdf = PdfWrapper(pdf_path)
    sample_data = pdf.sample_data
    print(f"LIFE-1528-Q: {len(sample_data)} fields detected")
except Exception as e:
    print(f"LIFE-1528-Q failed: {e}")

print("Basic test complete.")