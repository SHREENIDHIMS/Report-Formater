# Document Engine Design

## 1. Why this is the core risk

A DOCX is not a flat text file. It is a ZIP package of OOXML parts, relationships, styles, numbering definitions, section properties, headers/footers, fields, drawing anchors, media and potentially comments/revisions/embedded objects. A naive parse-and-recreate pipeline can destroy layout or content.

The product's credibility depends on preserving student content and making changes predictably. Build a tested import/transform/render pipeline before building a rich editor around it.

## 2. Pipeline stages

```text
Upload
  -> quarantine storage
  -> file/package security validation
  -> OOXML inventory + feature support profile
  -> semantic extraction / Document IR mapping
  -> import review + unsupported-feature warnings
  -> template rules resolution
  -> transformation plan (dry run)
  -> user approval
  -> new DOCX version generation
  -> reopen/structural validation
  -> isolated LibreOffice PDF rendering
  -> PDF page/layout inspection
  -> template compliance checks
  -> export bundle + manifest
```

Every stage records job ID, input version ID, output version ID (if applicable), worker/pipeline version, status, duration and safe error code.

## 3. Input safety

DOCX/DOCM are ZIP containers. Before parsing:
- enforce upload byte limit;
- validate extension and MIME but do not trust them alone;
- check ZIP magic and archive integrity;
- enforce compressed/uncompressed size, entry count and compression ratio limits;
- reject path traversal entries and suspicious external relationships;
- reject macro-enabled and encrypted/unsupported files in MVP;
- reject embedded OLE/ActiveX or flag as unsupported;
- scan with malware scanner where available;
- parse in isolated worker with no network access and strict resource limits.

PDF uploads are not the initial authoritative editable format. MVP may accept PDF for visual/text inspection only or defer upload entirely until a safe path exists.

## 4. Feature inventory

Classify each construct:
- **Supported** — import/edit/export with regression coverage.
- **Preserved, not editable** — copy original OOXML part/relationship safely while making other changes.
- **Warn/limited** — may survive only under certain transformations; user reviews output.
- **Unsupported** — block destructive transform or ask user to export a supported clean version.

Track at least:
- paragraphs and runs;
- paragraph styles and character styles;
- numbering/bullets;
- tables, merged cells, borders and nested tables;
- inline images and anchored/floating images;
- captions and cross-references;
- hyperlinks and bookmarks;
- headers/footers and page fields;
- section breaks and page setup;
- footnotes/endnotes;
- equations/OMML;
- shapes, text boxes and SmartArt;
- charts and embedded workbooks;
- comments and tracked changes;
- content controls;
- embedded objects/macros;
- external links and custom XML.

Do not promise support for a feature until corpus tests demonstrate fidelity.

## 5. Canonical Document IR

For documents created in-app, use a stable semantic JSON model. It is not intended to represent every OOXML feature.

Top-level concept:
- `schema_version`
- `document_id`, `template_id`, `template_version`
- `metadata` (project title, students, programme, guide, department, year)
- `sections[]` with stable IDs, `kind`, `title`, `required`, `children[]`
- content blocks: paragraph, heading, list, table, image, equation, page_break, reference_entry, caption
- asset references (private object key, checksum, dimensions, alt text)
- provenance for imported blocks (source part/paragraph ID where available)
- user-editable flags and style tokens.

See `docs/examples/document-ir.example.json`.

For imported DOCX, keep the original package and maintain mapping from supported IR elements back to original OOXML elements. Do not flatten all content into plain text.

## 6. Transformation plan

The formatter should first produce a dry-run plan:
- set page dimensions and margins;
- map body paragraphs to body style;
- map detected headings to configured heading styles;
- update paragraph alignment/spacing/indentation;
- apply page/section breaks required by template;
- apply numbering style;
- create/refresh captions where structured references are known;
- add missing front matter placeholders only when student supplies required data;
- refresh TOC/fields where supported by LibreOffice/Word;
- keep original images/tables where safe;
- flag conflicts and ambiguous section detection.

Every operation has a rule ID, target selector, expected change and reversibility information. Operations must be deterministic and idempotent for the same input/template/pipeline version.

## 7. DOCX implementation guidance

- Use `python-docx` for well-supported operations: paragraphs, styles, tables, inline images, sections, page setup, headers/footers basics.
- Use `lxml`/OOXML only for carefully understood operations that python-docx does not expose.
- Preserve package relationships and media correctly when copying parts.
- Build test fixtures with realistic Word-generated files, not only documents generated by your own code.
- Inspect styles.xml, numbering.xml, document.xml, header/footer parts, relationships and section properties.
- Avoid global string replacement of XML. Use namespace-aware parsing and tests.
- Preserve unknown package parts when possible; document cases where editing forces a package rewrite.

## 8. Page rendering and preview

LibreOffice headless in an isolated worker is the initial renderer candidate. Render transformed DOCX to PDF, inspect page count, text blocks, geometry and rasterized page images. The PDF produced by this pipeline is the preview source and final PDF export.

Do not use browser HTML pagination as the truth for final export. Browser previews can differ from Word/LibreOffice due to fonts, line breaking and page layout.

Page inspection checks:
- A4 dimensions and margins where measurable;
- blank pages;
- text outside usable page region;
- clipped/overlapping content;
- tables split or overflowing;
- figures too large or captions orphaned;
- widows/orphans and heading near page bottom (heuristics);
- page-number continuity and Roman/Arabic sequences;
- missing/stale TOC fields.

Geometry checks are heuristic. Surface uncertain findings as warnings, not definitive errors.

## 9. Validation finding model

A finding contains:
- `finding_id`, `rule_id`, `rule_version`;
- severity: `error`, `warning`, `info`;
- category: `page_setup`, `typography`, `structure`, `numbering`, `references`, `rendering`, `content_completeness`;
- observed and expected values;
- location: page, section/block ID, paragraph/table/figure reference;
- source/template provenance;
- fix availability and operation ID;
- confidence and limitations.

Avoid a single score without explanation. If a score is shown, specify its denominator, rules checked, and exclusions.

## 10. Versioning and recovery

- Original upload is immutable.
- Every accepted transformation and meaningful edit creates a version/checkpoint.
- Store parent version ID, operation list, input checksum, output checksum and template version.
- Allow restore by creating a new head pointing to prior content; do not mutate immutable versions.
- Purge binaries only under declared retention/deletion policy.

## 11. Performance and queue

Initial upload target: max 50 MB (configurable); page limits and uncompressed size limits must be tuned from tests. Process large jobs asynchronously. Worker concurrency should be limited according to measured LibreOffice memory. Provide progress states: `uploaded`, `scanning`, `inspecting`, `previewing`, `transforming`, `rendering`, `validating`, `ready`, `failed`.

## 12. DOCX proof-of-concept gate

Before general import support, process at least 30–50 diverse, permissioned sample files and test:
- common Word templates;
- tables with merges/nesting;
- inline and floating images;
- headers/footers and page numbers;
- multiple section orientations/margins;
- section/page/column breaks;
- references, hyperlinks and bookmarks;
- equations;
- tracked changes/comments;
- text boxes/charts where feasible.

Record preservation rate by feature. Make support table public in the upload flow. Do not hide failed cases.

## 13. Critical product rule

The application must never claim that every uploaded DOCX can be fully edited. It should tell users what it can safely handle, what it will preserve without editing, and what must be simplified before applying the formatter.
