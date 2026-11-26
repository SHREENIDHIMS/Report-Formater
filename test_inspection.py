"""Test script for DOCX inspection module."""

import sys
import os

# Add the api app to path so we can import the document engine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "api"))

# Use the venv Python's site-packages - but we'll just import directly
from apps.api.app.document_engine.importing import inspect_docx

report = inspect_docx("fixtures/simple_report.docx")

print("=== Simple Report Inspection Results ===")
print(f"Schema version: {report.schema_version}")
print(f"Parsed OK: {report.parsed_ok}")
print(f"File size: {report.file_size_bytes} bytes")
print(f"Total paragraphs: {report.total_paragraphs}")
print(f"Total runs: {report.total_runs}")
print(f"Total tables: {report.total_tables}")
print(f"Total images: {report.total_images}")
print(f"Total sections: {report.total_sections}")
print(f"Headings: {len(report.headings)}")
print(f"Unsupported elements: {report.unsupported_elements}")
print(f"Warnings: {report.warnings}")
print()

# Print paragraph summary
ps = report.paragraph_summary
for k, v in ps.items():
    print(f"  {k}: {v}")

print()
# Print headings
print("Headings:")
for h in report.headings:
    print(f"  Level {h.level}: paragraph {h.index} - \"{h.text[:60]}\"")

print()
# Print tables
print(f"Tables: {len(report.tables)}")
for t in report.tables:
    print(f"  Table {t.index}: {t.row_count}x{t.col_count}, merged={t.has_merged_cells}, nested={t.is_nested}, borders={t.has_borders}")

print()
# Print images
print(f"Images: {len(report.images)}")
for i in report.images:
    print(f"  Image {i.index}: inline={i.is_inline}, floating={i.is_floating}, type={i.content_type}, anchor={i.anchor_type}")

print()
# Print sections
print(f"Sections: {len(report.sections)}")
for s in report.sections:
    print(f"  Section {s.index}: type={s.type}, orientation={s.orientation}, margins=({s.margin_left_mm}, {s.margin_right_mm}, {s.margin_top_mm}, {s.margin_bottom_mm})")