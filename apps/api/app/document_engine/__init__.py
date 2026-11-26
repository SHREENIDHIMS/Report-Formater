"""Document engine package.

Isolated document-processing module for inspecting, importing, transforming,
rendering and validating DOCX documents. Kept separate from the public API
request path so untrusted Office files are handled in a worker-compatible way.
"""

from .importing.parser import ImportReport, inspect_docx

__all__ = ["inspect_docx", "ImportReport"]
