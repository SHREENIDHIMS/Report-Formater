"""DOCX import / inspection sub-package.

Provides package safety validation and a read-only feature inventory for DOCX
files. Never mutates the source package.
"""

from .models import ImportReport, SupportLevel
from .package_validation import (
    PackageValidationResult,
    validate_docx_package,
)
from .parser import inspect_docx

__all__ = [
    "ImportReport",
    "SupportLevel",
    "PackageValidationResult",
    "validate_docx_package",
    "inspect_docx",
]
