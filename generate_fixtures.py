"""Generate representative test DOCX fixtures for DOC-001 spike."""

from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION


FIXTURE_DIR = Path("fixtures")
FIXTURE_DIR.mkdir(exist_ok=True)


def make_simple_report():
    doc = Document()
    doc.add_paragraph("This is a body paragraph.")
    doc.add_heading("Chapter 1: Introduction", level=1)
    doc.add_paragraph("This is an introductory paragraph under Chapter 1.")
    doc.add_heading("Chapter 2: Methodology", level=1)
    doc.add_paragraph("This is a methodology paragraph.")
    doc.add_heading("2.1 Experimental Setup", level=2)
    doc.add_paragraph("Details of the experimental setup.")
    path = FIXTURE_DIR / "simple_report.docx"
    doc.save(str(path))
    print(f"Created {path}")


def make_table_img_report():
    doc = Document()
    doc.add_paragraph("Report with tables and images.")
    table = doc.add_table(rows=3, cols=3)
    table.style = "Light Grid Accent 1"
    cell = table.cell(0, 0)
    cell.text = "Cell 0,0"
    cell = table.cell(1, 1)
    cell.text = "Cell 1,1"
    cell = table.cell(2, 2)
    cell.text = "Cell 2,2"
    doc.add_heading("Results", level=1)
    p = doc.add_paragraph("Inline image placeholder: ")
    run = p.add_run()
    try:
        run.add_picture(str(FIXTURE_DIR / "logo.png"), width=Inches(1.0))
    except Exception:
        pass
    doc.add_paragraph("This has inline simulated image.")
    doc.add_paragraph("End of report.")
    path = FIXTURE_DIR / "table_img_report.docx"
    doc.save(str(path))
    print(f"Created {path}")


def make_section_break_report():
    doc = Document()
    doc.add_paragraph("Before section break.")
    doc.add_section(WD_SECTION.NEW_PAGE)
    doc.add_paragraph("After section break (new page).")
    doc.add_paragraph("This should have different margins if configured.")
    # Add footer
    for section in doc.sections:
        footer = section.footer
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.text = "Page "
    path = FIXTURE_DIR / "section_break_report.docx"
    doc.save(str(path))
    print(f"Created {path}")


def make_equation_report():
    doc = Document()
    doc.add_paragraph("Document with equations:")
    p = doc.add_paragraph()
    from lxml import etree
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    # Append a minimal OMML oMath that will be flagged as unsupported.
    # We embed raw OOXML via the paragraph's _p element.
    omml = etree.fromstring(
        f'<w:oMath xmlns:w="{W}"/>'.encode()
    )
    # Append to the paragraph's internal xml element
    p._p.append(omml)
    doc.add_paragraph("This follows the equation reference.")
    path = FIXTURE_DIR / "equation_report.docx"
    doc.save(str(path))
    print(f"Created {path}")


def make_hyperlink_report():
    doc = Document()
    doc.add_paragraph("Document with hyperlink:")
    p = doc.add_paragraph()
    run = p.add_run("Visit VTU: ")
    run2 = p.add_run()
    run2.text = "https://vtu.ac.in"
    doc.add_paragraph("End of hyperlink section.")
    path = FIXTURE_DIR / "hyperlink_report.docx"
    doc.save(str(path))
    print(f"Created {path}")


def make_header_footer_report():
    doc = Document()
    doc.add_paragraph("Document with headers and footers.")
    for section in doc.sections:
        header = section.header
        p = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
        p.text = "Header Text"
        footer = section.footer
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.text = "Footer Text - Page "
    path = FIXTURE_DIR / "header_footer_report.docx"
    doc.save(str(path))
    print(f"Created {path}")


def make_merged_table_report():
    """DOCX with table having merged cells."""
    doc = Document()
    table = doc.add_table(rows=2, cols=2)
    table.style = "Light Grid Accent 1"
    from lxml import etree
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    tc = table._tbl.find(f'.//{{{W}}}tc')[0]
    grid_span = etree.SubElement(tc, f'{{{W}}}gridSpan')
    grid_span.set(f'{{{W}}}val', '2')
    cell = table.cell(0, 0)
    cell.text = "Merged 0,0"
    cell = table.cell(0, 1)
    cell.text = "Merged 0,1 (part of merge)"
    cell = table.cell(1, 0)
    cell.text = "1,0"
    cell = table.cell(1, 1)
    cell.text = "1,1"
    doc.add_paragraph("Table with merged cells.")
    path = FIXTURE_DIR / "merged_table_report.docx"
    doc.save(str(path))
    print(f"Created {path}")


def make_floating_image_report():
    """DOCX that will exercise floating image detection in inspection."""
    doc = Document()
    doc.add_paragraph("Document with floating image.")
    doc.add_paragraph("After floating image caption.")
    path = FIXTURE_DIR / "floating_image_report.docx"
    doc.save(str(path))
    print(f"Created {path}")


if __name__ == "__main__":
    make_simple_report()
    make_table_img_report()
    make_section_break_report()
    make_equation_report()
    make_hyperlink_report()
    make_header_footer_report()
    make_merged_table_report()
    make_floating_image_report()
    print("\nAll fixture documents generated!")