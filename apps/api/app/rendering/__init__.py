"""Rendering module for DOCX to PDF conversion.

Isolated document rendering worker for converting DOCX files to PDF.
Designed to run in a constrained container/process with strict resource limits.
"""

from .converter import convert_docx_to_pdf
from .models import ConversionResult, ConversionStatus

__all__ = ["convert_docx_to_pdf", "ConversionResult", "ConversionStatus"]
