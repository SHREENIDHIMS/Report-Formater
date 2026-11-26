"""Pydantic schemas for DOCX to PDF conversion results."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class ConversionStatus(StrEnum):
    """Status of a DOCX to PDF conversion job."""

    PENDING = "pending"
    """Job queued, not yet started."""

    PROCESSING = "processing"
    """Conversion in progress."""

    SUCCEEDED = "succeeded"
    """Conversion completed successfully."""

    FAILED = "failed"
    """Conversion failed (see error field)."""

    CANCELLED = "cancelled"
    """Job was cancelled."""


class ConversionResult(BaseModel):
    """Structured result of a DOCX to PDF conversion."""

    job_id: str = Field(description="Unique identifier for this conversion job")
    status: ConversionStatus = Field(description="Current conversion status")
    source_docx_checksum: str = Field(default="", description="SHA-256 checksum of input DOCX")
    output_pdf_path: str | None = Field(default=None, description="Caller-owned PDF path")
    page_count: int | None = Field(default=None, description="Number of rendered pages")
    page_dimensions_mm: list[list[float]] | None = Field(
        default=None, description="Per-page [width_mm, height_mm] dimensions"
    )
    has_blank_pages: bool = Field(
        default=False,
        description="Whether any blank (empty) pages were detected",
    )
    error: str | None = Field(default=None, description="Error message if conversion failed")
    worker_version: str = Field(
        default="0.1.0",
        description="Version of the rendering worker that produced this result",
    )
    duration_seconds: float | None = Field(default=None, description="Elapsed wall time")
