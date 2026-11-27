"""Typed schemas for the DOCX import feasibility spike.

These models describe a read-only feature inventory produced by inspecting a
DOCX package. They classify each detected OOXML construct as supported,
preserved (not editable), warn/limited, or unsupported, following the
feature-inventory categories in docs/05-document-engine-design.md.

The original file is never mutated by anything in this module.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class SupportLevel(StrEnum):
    """Classification of a detected OOXML construct for import purposes."""

    SUPPORTED = "supported"
    """Can be imported, edited and exported with regression coverage."""

    PRESERVED_NOT_EDITABLE = "preserved_not_editable"
    """Original OOXML is copied safely; not editable through the IR."""

    WARN_LIMITED = "warn_limited"
    """May survive only under certain transforms; user reviews output."""

    UNSUPPORTED = "unsupported"
    """Blocks destructive transform or requires a clean supported version."""


class ParagraphStyleInfo(BaseModel):
    style_id: str | None = Field(default=None, description="w:styleId of the paragraph style")
    style_name: str | None = Field(default=None, description="Localized style name")
    is_heading: bool = Field(default=False, description="Style indicates a heading level")
    heading_level: int | None = Field(
        default=None, description="1-based heading level when a heading"
    )


class ParagraphInfo(BaseModel):
    index: int = Field(description="Zero-based paragraph index in document order")
    style: ParagraphStyleInfo = Field(default_factory=ParagraphStyleInfo)
    text: str = Field(default="", description="Extracted text content")
    text_length: int = Field(default=0)
    run_count: int = Field(default=0)
    alignment: str | None = Field(default=None)
    has_hyperlink: bool = Field(default=False)
    has_field: bool = Field(default=False)
    field_types: list[str] = Field(default_factory=list)
    has_numbering: bool = Field(default=False)
    num_id: str | None = Field(default=None)
    num_level: int | None = Field(default=None)
    num_format: str | None = Field(
        default=None, description="Resolved numbering format (decimal, bullet, ...)"
    )
    is_empty: bool = Field(default=False)


class HeadingInfo(BaseModel):
    index: int = Field(description="Paragraph index of the heading")
    level: int = Field(description="Heading level (1-based)")
    style_id: str | None = Field(default=None)
    style_name: str | None = Field(default=None)
    text: str = Field(default="")
    text_length: int = Field(default=0)


class TableCellInfo(BaseModel):
    row_index: int
    col_index: int
    is_merged_start: bool = Field(default=False)
    is_merged_continuation: bool = Field(default=False)
    text: str = Field(default="")


class TableInfo(BaseModel):
    index: int = Field(description="Zero-based table index in document order")
    row_count: int = Field(default=0)
    col_count: int = Field(default=0)
    cell_count: int = Field(default=0)
    has_merged_cells: bool = Field(default=False)
    is_nested: bool = Field(default=False)
    has_borders: bool = Field(default=False)


class ImageInfo(BaseModel):
    index: int = Field(description="Zero-based image index")
    relationship_id: str | None = Field(default=None, description="r:embed / r:link target")
    content_type: str | None = Field(
        default=None, description="MIME type from [Content_Types].xml / target extension"
    )
    width_emu: int | None = Field(default=None)
    height_emu: int | None = Field(default=None)
    is_inline: bool = Field(default=False)
    is_floating: bool = Field(default=False)
    anchor_type: str | None = Field(default=None, description="inline, anchor, frame, etc.")


class SectionInfo(BaseModel):
    index: int = Field(description="Zero-based section index")
    type: str = Field(default="nextPage", description="nextPage, continuous, evenPage, oddPage")
    orientation: str = Field(default="portrait", description="portrait or landscape")
    page_width_emu: int | None = Field(default=None)
    page_height_emu: int | None = Field(default=None)
    page_width_mm: float | None = Field(default=None)
    page_height_mm: float | None = Field(default=None)
    margin_top_twips: int | None = Field(default=None)
    margin_bottom_twips: int | None = Field(default=None)
    margin_left_twips: int | None = Field(default=None)
    margin_right_twips: int | None = Field(default=None)
    margin_top_mm: float | None = Field(default=None)
    margin_bottom_mm: float | None = Field(default=None)
    margin_left_mm: float | None = Field(default=None)
    margin_right_mm: float | None = Field(default=None)
    header_reference: str | None = Field(default=None)
    footer_reference: str | None = Field(default=None)
    first_page_header_reference: str | None = Field(default=None)
    first_page_footer_reference: str | None = Field(default=None)
    title_pg: bool = Field(default=False, description="Section uses a different first page")


class HeaderFooterInfo(BaseModel):
    type: str = Field(description="default, firstPage, evenPage")
    part_target: str | None = Field(
        default=None, description="Relationship target of the header/footer part"
    )
    paragraph_count: int = Field(default=0)
    has_page_field: bool = Field(default=False)
    page_field_types: list[str] = Field(default_factory=list, description="e.g. PAGE, NUMPAGES")
    text: str = Field(default="")
    text_length: int = Field(default=0)


class FeatureEntry(BaseModel):
    feature: str = Field(description="Human-readable feature name")
    count: int = Field(default=0, description="Number of occurrences detected")
    support: SupportLevel = Field(description="Import support classification")
    notes: str | None = Field(default=None, description="Preservation / limitation notes")
    locations: list[str] = Field(
        default_factory=list, description="Where detected (paragraph/section indices, parts)"
    )


class PackageValidationResult(BaseModel):
    valid: bool = Field(description="Whether the package passed all safety checks")
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    file_size_bytes: int = Field(default=0)
    entry_count: int = Field(default=0)
    has_content_types: bool = Field(default=False)
    has_document_part: bool = Field(default=False)
    has_document_rels: bool = Field(default=False)
    macro_parts: list[str] = Field(
        default_factory=list, description="vbaProject / macro-related parts found"
    )
    path_traversal_entries: list[str] = Field(default_factory=list)
    suspicious_relationships: list[str] = Field(default_factory=list)


class ImportReport(BaseModel):
    """Read-only DOCX import feasibility report.

    Produced without mutating the source package. Use this to decide whether a
    document can be imported, what must be preserved as-is, and what must be
    flagged to the student before any transformation.
    """

    schema_version: str = Field(default="1.0")
    source_file: str = Field(description="Path of the inspected DOCX")
    file_size_bytes: int = Field(default=0)
    parsed_ok: bool = Field(default=False)

    # Package safety validation - optional; populated after validation
    package_validation: PackageValidationResult | None = Field(
        default=None, description="Read-only package safety validation result"
    )

    # Document structure
    paragraphs: list[ParagraphInfo] = Field(default_factory=list)
    paragraph_summary: dict[str, Any] = Field(default_factory=dict)
    headings: list[HeadingInfo] = Field(
        default_factory=list, description="Heading hierarchy (flattened)"
    )
    tables: list[TableInfo] = Field(default_factory=list)
    images: list[ImageInfo] = Field(default_factory=list)
    sections: list[SectionInfo] = Field(default_factory=list)
    headers_footers: list[HeaderFooterInfo] = Field(default_factory=list)

    # Feature classification
    features: list[FeatureEntry] = Field(default_factory=list)
    unsupported_elements: list[str] = Field(
        default_factory=list,
        description="Raw unsupported OOXML element types detected",
    )
    warnings: list[str] = Field(default_factory=list, description="Human-readable import warnings")

    # Totals
    total_runs: int = Field(default=0)
    total_paragraphs: int = Field(default=0)
    total_tables: int = Field(default=0)
    total_images: int = Field(default=0)
    total_sections: int = Field(default=0)
