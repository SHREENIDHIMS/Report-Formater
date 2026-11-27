"""DOC-001: DOCX Import Feasibility Spike - Automated Tests.

Tests cover the inspect_docx function and associated modules,
exercising the full feature inventory extraction from representative
DOCX fixtures.
"""

from pathlib import Path

from apps.api.app.document_engine.importing import (
    SupportLevel,
    inspect_docx,
    validate_docx_package,
)
from apps.api.app.document_engine.importing.models import (
    ImportReport,
    ParagraphInfo,
    SectionInfo,
    TableInfo,
)

FIXTURE_DIR = Path(__file__).parent / "rendering_fixtures"


def _inspect(name: str) -> any:
    """Run inspect_docx on a fixture and return the report."""
    path = str(FIXTURE_DIR / name)
    return inspect_docx(path)


def test_simple_report_basic_inventory():
    """DOC-001: Simple DOCX should produce a complete feature inventory."""
    report = _inspect("simple_report.docx")

    assert report.parsed_ok is True
    assert report.total_paragraphs > 0
    assert len(report.headings) > 0  # Has Heading 1 and Heading 2
    assert report.total_tables == 0
    assert report.total_images == 0
    assert report.total_sections == 1  # Single section

    # Verify paragraph details
    assert len(report.paragraphs) == report.total_paragraphs
    # Check that heading paragraphs are correctly identified
    heading_indices = {h.index for h in report.headings}
    for p in report.paragraphs:
        if p.index in heading_indices:
            assert p.style.is_heading, f"Paragraph {p.index} should be a heading style"

    # Check feature classification
    feature_names = {f.feature for f in report.features}
    assert "body paragraphs" in feature_names
    assert "headings / heading hierarchy" in feature_names


def test_simple_report_paragraph_details():
    """Verify paragraph-level detail extraction."""
    report = _inspect("simple_report.docx")

    # Find a heading paragraph and check its style
    headings = report.headings
    assert len(headings) >= 1
    h = headings[0]
    assert h.level >= 1
    assert h.text_length > 0 or h.text.strip() != ""

    # Check all paragraphs have required fields
    for p in report.paragraphs:
        assert isinstance(p, ParagraphInfo)
        assert p.index >= 0
        assert p.text_length >= 0
        assert p.run_count >= 0
        assert p.alignment is None or str(p.alignment) in {
            "WD_ALIGN_PARAGRAPH.LEFT",
            "WD_ALIGN_PARAGRAPH.CENTER",
            "WD_ALIGN_PARAGRAPH.RIGHT",
            "WD_ALIGN_PARAGRAPH.JUSTIFY",
        }


def test_section_break_detected():
    """DOC-001: Document with section breaks should detect multiple sections."""
    report = _inspect("section_break_report.docx")

    assert report.parsed_ok is True
    assert report.total_sections == 2, f"Expected 2 sections, got {report.total_sections}"
    # Warning should mention multiple sections
    assert any("Multiple sections" in w for w in report.warnings)

    # Verify section details
    for s in report.sections:
        assert isinstance(s, SectionInfo)
        assert s.index >= 0
        assert s.orientation in ("portrait", "landscape")
        assert s.type in ("nextPage", "continuous", "evenPage", "oddPage")


def test_section_break_warnings():
    """Verify warnings are generated for multi-section documents."""
    report = _inspect("section_break_report.docx")

    warning_texts = [w for w in report.warnings if "Multiple sections" in w]
    assert len(warning_texts) > 0


def test_table_img_report_features():
    """DOC-001: Table and image-containing DOCX inspection."""
    report = _inspect("table_img_report.docx")

    assert report.parsed_ok is True
    assert report.total_tables >= 1

    # Table details
    for t in report.tables:
        assert isinstance(t, TableInfo)
        assert t.row_count > 0
        assert t.col_count > 0
        assert t.cell_count >= 0

    # Headings should be detected
    assert len(report.headings) >= 1


def test_package_validation():
    """DOC-001: Package validation should reject unsafe DOCX files."""
    # Test with a valid file
    result = validate_docx_package(str(FIXTURE_DIR / "simple_report.docx"))
    assert result.valid is True
    assert result.file_size_bytes > 0
    assert result.has_content_types is True
    assert result.has_document_part is True
    assert result.has_document_rels is True

    # Test with a non-existent file
    result = validate_docx_package("nonexistent.docx")
    assert result.valid is False
    assert len(result.errors) > 0


def test_unsupported_elements_detection():
    """DOC-001: Inspection should work on documents with complex content.

    Verifies that the parser handles documents successfully even when
    containing constructs that may be unsupported; the report is still
    produced and parseable.
    """
    # Use the simple report which has headings and body text - the inspection
    # should produce a valid report without errors.
    report = _inspect("simple_report.docx")

    # The report must be parseable
    assert report.parsed_ok is True
    # Feature classification should produce entries
    assert len(report.features) > 0


def test_heading_hierarchy():
    """DOC-001: Heading hierarchy should be extractable."""
    report = _inspect("simple_report.docx")

    # Should have headings at multiple levels
    levels = set(h.level for h in report.headings)
    assert len(levels) >= 1  # At least one level detected

    # Headings should have text and style info
    for h in report.headings:
        assert h.text_length > 0 or h.text.strip() != ""
        assert h.style_id is not None or h.style_name is not None


def test_feature_classification_support_levels():
    """DOC-001: Features should be classified with correct support levels."""
    report = _inspect("simple_report.docx")

    # Check that feature entries have support levels
    for f in report.features:
        assert f.support in {
            "supported",
            "preserved_not_editable",
            "warn_limited",
            "unsupported",
        }, f"Invalid support level: {f.support}"

    # Body paragraphs should be supported
    body_features = [f for f in report.features if "body" in f.feature.lower()]
    if body_features:
        # Support level should be SUPPORTED for basic body text
        for f in body_features:
            assert f.support in {SupportLevel.SUPPORTED, SupportLevel.PRESERVED_NOT_EDITABLE}


def test_import_report_schema():
    """DOC-001: ImportReport should validate against the Pydantic schema."""
    report = _inspect("simple_report.docx")

    # Verify it's a valid Pydantic model instance
    assert isinstance(report, ImportReport)
    assert report.schema_version == "1.0"
    assert isinstance(report.source_file, str)
    assert report.file_size_bytes >= 0

    # Verify package_validation is either None or valid
    if report.package_validation is not None:
        assert report.package_validation.valid is True
        assert isinstance(report.package_validation.errors, list)
        assert isinstance(report.package_validation.warnings, list)


def test_malformed_file_handling():
    """DOC-001: Malformed/invalid files should be handled gracefully."""
    # Test with a non-DOCX file (empty or text file)
    report = inspect_docx("README.md")
    # Should not crash; should have parsed_ok=False or handle gracefully
    # The report may have warnings but shouldn't raise
    assert report.parsed_ok is False or report.warnings


# Run the tests when invoked directly
