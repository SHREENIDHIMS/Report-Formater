# Product Requirements Document (PRD)

**Product:** VTU Report Studio  
**Version:** 0.1 — implementation baseline  
**Date:** 25 November 2026  
**Audience:** Founder, product designer, coding agent, QA  
**Status:** Draft for implementation; VTU rule applicability must be verified before public claims.

---

## 1. Product vision

Make academic report formatting predictable and accessible. A student should focus on their own project work; the application should handle document structure, repeatable layout rules, numbering, validation and export.

The product is a self-serve web app. It does not depend on a college administrator, faculty member or institutional contract to create an account or prepare a report.

## 2. Problem statement

A student may have a completed project and a partially written 40–100 page report, but still need to:
- interpret a university or college formatting circular;
- manually configure page size, margins, typography, line spacing and alignment;
- create title/certificate/declaration pages;
- maintain heading and page numbering conventions;
- number figures, tables and equations;
- regenerate a table of contents and lists;
- ensure figures/tables do not overflow or split badly;
- correct the same formatting issue across many pages;
- export both an editable Word document and a print-ready PDF.

Manual formatting is slow and error-prone. Existing simple generators may not preserve the complexity of an already-written DOCX. The product must prove that it can preserve content before marketing automatic correction as universal.

## 3. Goals

### G1 — Reduce repetitive formatting effort
A student can choose a verified template and apply its deterministic rules to supported documents.

### G2 — Preserve student work
Original uploads remain unchanged. Transformations are versioned and reversible. Unsupported content is reported rather than silently removed.

### G3 — Make requirements understandable
Every validation result explains the observed value, expected rule, severity, source/version and available fix.

### G4 — Let users finish online
Students can create, edit, preview, validate and export from a browser without needing a university account.

### G5 — Monetize fairly
Students can inspect the template and a useful preview before payment. Payment purchases a defined report/project entitlement, not a vague unlimited service.

## 4. Non-goals for MVP

- College/faculty portal, grading or approval workflows.
- Official university integration or claims of VTU endorsement.
- AI-generated full project reports.
- Plagiarism detection, AI detection or guaranteed similarity score.
- Automatic validation of technical correctness or research quality.
- Automatic creation of experimental results, code outputs, citations or reference metadata.
- Universal conversion of every possible DOCX/PDF.
- Native mobile apps.
- Support for every Indian university or every course.
- Collaborative real-time editing in the first thin slice (design data model to allow it later).

## 5. Target users and jobs-to-be-done

### Persona A — Final-year engineering student (primary)
Has a project and a partial/full Word document. Wants the report to follow the correct VTU/college format, wants fewer corrections, and needs DOCX for final edits plus PDF for printing/submission.

**Job:** “When my report content is ready, help me apply the correct format and identify errors before I submit.”

### Persona B — Student starting from scratch
Has project details, but no structured report document. Wants a checklist and guided chapter editor.

**Job:** “Help me build the report in the right order without forgetting mandatory sections.”

### Persona C — Project team coordinator
Owns one shared report with multiple student names and certificate details. Needs one source of truth and team review.

**Job:** “Help our team maintain one consistent report and produce each required team/student version.”

### Persona D — Student with college-specific rules
Has a VTU baseline plus a local department sample or instruction sheet. Wants to supply the extra constraints without waiting for college integration.

**Job:** “Let me add the instructions my department gave us and validate against both sets.”

## 6. Product principles

1. The template engine, not AI, determines layout.
2. A template is structured, versioned rules plus assets and section definitions—not only a DOCX file.
3. Preserve uploaded source files. Make every transformation inspectable.
4. Never infer an institution, scheme or academic year when ambiguous.
5. Validation is scoped to the exact selected template version.
6. Show a report-specific preview/change summary before paid export.
7. Students own their uploaded content. Private by default.
8. Export must be re-opened/rendered and validated after generation.
9. User override is possible where sensible, but violations remain visible.
10. Avoid fabricating academic material, signatures, seals and citations.

## 7. Core workflows

### 7.1 Automatic mode
1. Student signs in.
2. Selects “Format an existing report”.
3. Selects university (VTU for MVP), course, scheme/cohort, report type and available template version.
4. Uploads DOCX. (PDF import is later and must not be represented as full editable conversion.)
5. Server checks file safety, size and format.
6. Import worker inspects OOXML package and extracts a document inventory.
7. Student reviews detected sections and import warnings.
8. System generates a transformation preview and change summary.
9. Student chooses apply / change options / cancel.
10. System creates a new version; original stays available.
11. Student reviews paginated preview and validation issues.
12. Student purchases entitlement if required for final export.
13. System renders DOCX to PDF, validates the output, and makes both files available.

### 7.2 Manual mode
1. Student selects template and report type.
2. Completes project/team details.
3. Application creates a structured report with required section placeholders.
4. Student fills sections in a guided editor.
5. Student adds images, tables, captions and references.
6. Template engine controls global formatting.
7. Preview, validation, pay and export.

### 7.3 Hybrid mode
1. Student uploads an existing supported DOCX.
2. Importer maps existing headings/paragraphs into a document model.
3. Student reviews section mapping and warnings.
4. Automatic formatting applies to a new version.
5. Student uses editor to correct content, add missing mandatory sections or reorder permitted sections.
6. Validate, pay and export.

## 8. Functional requirements

Priority scale: P0 = release blocker, P1 = important first release, P2 = later.

### Account and workspace
- **FR-001 (P0):** User can register, sign in and sign out.
- **FR-002 (P0):** User can see only their own reports and invited team reports.
- **FR-003 (P1):** User can create, rename, archive and delete a project/report.
- **FR-004 (P1):** Autosave persists document changes and exposes save state.
- **FR-005 (P1):** User can recover earlier document versions.

### Template selection
- **FR-010 (P0):** User can select VTU B.E./B.Tech. report template by scheme/cohort and report type where verified.
- **FR-011 (P0):** Template details show status, version, effective period, source documents and last verification date.
- **FR-012 (P1):** User can add a private college-specific override/rule preset from a sample or instruction sheet.
- **FR-013 (P1):** A document remains associated with the selected template version; publishing a new version does not silently change existing reports.

### Import
- **FR-020 (P0):** DOCX upload is checked for extension, MIME, ZIP signature, entry count, compressed/uncompressed size and unsafe/malformed structure.
- **FR-021 (P0):** Original upload is retained immutably and receives a checksum.
- **FR-022 (P0):** Import report lists recognized constructs and unsupported/risky constructs.
- **FR-023 (P0):** No unsupported feature is silently discarded.
- **FR-024 (P1):** System can import supported paragraph, heading, table, image, hyperlink and common section-break structures.
- **FR-025 (P2):** PDF text extraction and OCR-assisted reconstruction.

### Manual editor
- **FR-030 (P1):** Student can create a document from an ordered report outline.
- **FR-031 (P1):** Editor supports paragraphs, headings, lists, tables, images, captions, hyperlinks, equations (display/LaTeX or image depending on MVP decision), page breaks and references.
- **FR-032 (P1):** Editor displays outline/navigation and a paginated preview.
- **FR-033 (P1):** Template-defined global styles are protected; permitted local formatting can be edited.
- **FR-034 (P1):** Autosave and undo/redo are available.

### Automatic formatting and hybrid editing
- **FR-040 (P0):** Applying a template creates a new immutable version, never overwrites the source.
- **FR-041 (P0):** Application generates a human-readable change report.
- **FR-042 (P0):** Student can preview before accepting changes.
- **FR-043 (P1):** Student can apply fixes individually or in safe groups.
- **FR-044 (P1):** Student can preserve selected original paragraph/character formatting where compatible.
- **FR-045 (P1):** Student can edit imported content after formatting.

### Validation
- **FR-050 (P0):** Validator checks page size, margins, font size where detectable, paragraph alignment, spacing, required sections and basic numbering.
- **FR-051 (P0):** Every finding contains rule ID, severity, observed value, expected value, source/template version and suggested action.
- **FR-052 (P1):** Validator checks figure/table captions and chapterwise number sequences.
- **FR-053 (P1):** Validator checks TOC/field freshness and rendered pagination.
- **FR-054 (P1):** Layout checks detect likely overflow, clipping, blank pages and broken table/image placement from rendered pages.
- **FR-055 (P2):** Reference citation-format checks beyond basic numbering.

### Export
- **FR-060 (P0):** Student can export editable DOCX.
- **FR-061 (P0):** Student can export PDF generated from the final DOCX using the approved rendering worker.
- **FR-062 (P0):** Export output is re-opened and revalidated; errors are surfaced.
- **FR-063 (P1):** Student can download a validation report/change summary.
- **FR-064 (P1):** Export filenames include project and version but avoid unnecessary personal data.

### Billing
- **FR-070 (P0):** Free preview is available within defined limits.
- **FR-071 (P0):** User can buy one report/project entitlement using an India-supported payment gateway.
- **FR-072 (P0):** Entitlement activates only after verified server-side payment confirmation/webhook.
- **FR-073 (P0):** Duplicate webhooks are idempotent and cannot grant duplicate unintended credits.
- **FR-074 (P1):** Refund/cancellation and failed-payment states are visible.
- **FR-075 (P1):** Purchase covers a clearly defined report, collaborators (if supported), and a revision/export validity window.

### Privacy and operations
- **FR-080 (P0):** Files are private by default and access is authorized server-side.
- **FR-081 (P0):** User can delete a report and request account deletion.
- **FR-082 (P0):** Sensitive document contents and credentials do not appear in application logs.
- **FR-083 (P1):** System has configurable retention for abandoned drafts and deleted-file purge.

## 9. Non-functional requirements

- **Performance:** dashboard API p95 < 500 ms at pilot scale; document processing target < 60 s for a 50-page supported DOCX, measured on defined worker resources. These are targets to validate, not guaranteed SLAs.
- **Availability:** pilot target 99.5% monthly after production launch; no public SLA initially.
- **Reliability:** processing jobs are durable, retryable and idempotent; job states are visible.
- **Scalability:** web/API and document workers can scale independently.
- **Security:** TLS, private object storage, signed short-lived downloads, secure cookies/JWT verification, RBAC/ownership checks, rate limits, upload scanning and dependency updates.
- **Accessibility:** keyboard operation, visible focus, semantic labels, screen-reader-friendly status/error messages; target WCAG 2.2 AA for core flows.
- **Compatibility:** current Chrome/Edge/Firefox desktop; responsive mobile for dashboard and preview. Full editing on narrow screens may be limited in MVP.
- **Maintainability:** typed API contracts, migration-based schema, test fixtures, source-attributed template rules, ADRs.

## 10. User stories and acceptance criteria

### Story A — Format my Word report
As a student, I want to upload my DOCX and apply a VTU template so I can reduce repetitive manual formatting.

Acceptance:
- Original file is not mutated.
- User selects exact template/version and sees status/source.
- System returns a structure inventory and warnings before transformation.
- Preview is available before accepting.
- The final document has a new version ID and a change report.
- Unsupported constructs are visibly reported; no silent loss.

### Story B — Build from scratch
As a student, I want an outline and an editor so I can fill sections in an order appropriate to my selected report format.

Acceptance:
- Mandatory sections are shown as required/optional according to template.
- Empty required sections are visible in validation.
- Heading styles and global layout derive from template rules.
- Autosave reports success or failure.

### Story C — Fix a specific issue
As a student, I want a finding such as “right margin differs” to explain the issue and let me apply a fix.

Acceptance:
- Finding displays observed and expected values and rule provenance.
- Fix preview shows affected document areas.
- User can apply or dismiss where allowed.
- Fix creates a new version and is reversible.

### Story D — Export after purchase
As a student, I want to pay once for my team report and get DOCX and PDF.

Acceptance:
- Checkout describes exactly what is included and its validity window.
- Payment status is verified on server via signed webhook or server confirmation.
- Repeated events do not create duplicate entitlements.
- Download authorization is checked for every request.
- Export is revalidated after rendering.

## 11. Information architecture

Public: Home, How it works, Templates, Pricing, FAQ, Privacy, Terms, Contact.  
Authenticated: Dashboard, New Report, Template Picker, Import Review, Editor, Validation, Export/Checkout, Report History, Account/Billing.

## 12. MVP release gate

Do not launch paid automatic formatting until:
1. Scheme/template applicability has been documented for target users.
2. A gold corpus contains representative DOCX documents with tables, images, section breaks, headers/footers and page fields.
3. Original and transformed documents are compared structurally and visually.
4. Unsupported constructs block or warn appropriately.
5. DOCX and PDF output survive reopen/render checks.
6. Payment/webhook and ownership-isolation tests pass.
7. Pricing and validity language are explicit.
8. Privacy, terms, refund and deletion policies are published.

## 13. Analytics events (privacy-conscious)

Track event metadata only, not report text or filenames containing student data:
- `signup_completed`
- `report_created`
- `template_selected` (template ID/version)
- `docx_upload_started`, `docx_upload_succeeded`, `docx_import_warning`
- `format_preview_generated`, `format_applied`
- `validation_completed` (counts by rule category, not text)
- `export_previewed`, `checkout_started`, `payment_succeeded`, `export_completed`
- `report_deleted`, `refund_requested`

## 14. Open product decisions

See `docs/17-open-questions-and-risks.md`. Highest priority: cohort/scheme mapping, exact template coverage, supported DOCX feature set, page-editor approach, team entitlement semantics, price and revision window.
