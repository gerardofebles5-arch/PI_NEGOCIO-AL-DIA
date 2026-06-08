"""
Main entry point for Python Cloud Functions
"""

import os

# Import the OCR ultra advanced functions
from ocr_ultra import process_document_ultra, extract_with_template, get_ocr_summary

# Export functions for Cloud Functions deployment
__all__ = ['process_document_ultra', 'extract_with_template', 'get_ocr_summary']
