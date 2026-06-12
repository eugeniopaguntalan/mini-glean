"""
Script to create a sample PDF for testing
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

# Create fixtures directory if it doesn't exist
os.makedirs('tests/fixtures', exist_ok=True)

# Create a simple PDF
pdf_path = 'tests/fixtures/sample.pdf'
c = canvas.Canvas(pdf_path, pagesize=letter)

# Add some text content
c.drawString(100, 750, 'Sample PDF Document')
c.drawString(100, 730, '')
c.drawString(100, 710, 'This is a test PDF for MiniGlean.')
c.drawString(100, 690, '')
c.drawString(100, 670, 'It contains some sample text that will be extracted,')
c.drawString(100, 650, 'chunked, and embedded during the ingestion process.')
c.drawString(100, 630, '')
c.drawString(100, 610, 'This document is used for testing the PDF parsing')
c.drawString(100, 590, 'functionality in the document ingestion pipeline.')
c.drawString(100, 570, '')
c.drawString(100, 550, 'The content here should be extractable by pdfplumber')
c.drawString(100, 530, 'and processable by the chunking and embedding services.')

c.save()
print(f'Created {pdf_path}')
