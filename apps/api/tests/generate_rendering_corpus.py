"""Generate the deterministic DOC-002.1 rendering corpus."""

from __future__ import annotations

import base64
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_BREAK
from docx.shared import Inches
from lxml import etree

OUT = Path(__file__).parent / "rendering_fixtures"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
FAMILY = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
    "+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def _page_field(paragraph) -> None:
    run = paragraph.add_run()
    begin = etree.SubElement(run._r, f"{{{W}}}fldChar")
    begin.set(f"{{{W}}}fldCharType", "begin")
    instruction = etree.SubElement(run._r, f"{{{W}}}instrText")
    instruction.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    instruction.text = " PAGE "
    end = etree.SubElement(run._r, f"{{{W}}}fldChar")
    end.set(f"{{{W}}}fldCharType", "end")


def _header_footer(document: Document) -> None:
    for section in document.sections:
        section.header.paragraphs[0].text = "VTU Report Studio — Golden Header"
        footer = section.footer.paragraphs[0]
        footer.text = "Page "
        _page_field(footer)


def _write(name: str, document: Document) -> None:
    document.save(OUT / name)


def make_tables_images() -> None:
    document = Document()
    document.add_heading("Tables and Images", 0)
    document.add_paragraph("A representative table and an embedded image.")
    table = document.add_table(rows=4, cols=3)
    table.style = "Table Grid"
    for row in range(4):
        for column in range(3):
            table.cell(row, column).text = f"Cell {row + 1},{column + 1}"
    image_path = OUT / "fixture-image.png"
    image_path.write_bytes(ONE_PIXEL_PNG)
    document.add_picture(str(image_path), width=Inches(1))
    document.add_paragraph("Figure 1: Embedded image fixture.")
    _write("tables_images_report.docx", document)
    image_path.unlink()


def make_headers_footers() -> None:
    document = Document()
    document.add_heading("Headers and Footers", 0)
    _header_footer(document)
    for index in range(3):
        document.add_paragraph(f"Body content block {index + 1}.")
    _write("headers_footers_report.docx", document)


def make_multi_page() -> None:
    document = Document()
    document.add_heading("Multi-page Report", 0)
    _header_footer(document)
    for index in range(12):
        document.add_heading(f"Section {index + 1}", 1)
        for paragraph in range(8):
            document.add_paragraph(
                f"Page content {index + 1}.{paragraph + 1}: "
                "This repeated sentence provides stable text for golden extraction."
            )
        if index < 11:
            document.add_page_break()
    _write("multi_page_report.docx", document)


def make_complex_breaks() -> None:
    document = Document()
    document.add_heading("Complex Page Breaks", 0)
    document.add_paragraph("Before the first explicit break.")
    document.add_page_break()
    document.add_paragraph("After a manual page break.")
    document.add_section(WD_SECTION.NEW_PAGE)
    document.add_paragraph("After a new-page section break.")
    document.add_section(WD_SECTION.CONTINUOUS)
    document.add_paragraph("After a continuous section break.")
    paragraph = document.add_paragraph("A paragraph with a run break")
    paragraph.add_run().add_break(WD_BREAK.LINE)
    paragraph.add_run("and a second line.")
    _header_footer(document)
    _write("complex_page_breaks_report.docx", document)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    make_tables_images()
    make_headers_footers()
    make_multi_page()
    make_complex_breaks()
