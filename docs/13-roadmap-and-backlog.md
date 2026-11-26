# Roadmap and implementation backlog

Order is intentionally document-engine-first. Finish a narrow end-to-end slice before adding numerous features.

## Phase 0 — Product and feasibility (must precede paid claims)

### DISC-001 — Confirm VTU scope and cohort mapping
**Deliverable:** evidence table mapping target student cohort/scheme/report type to current official and college-provided requirements.
**Acceptance:** identify which official guide applies; store source URLs/pages and checked date; list unresolved conflicts; no template labeled verified without sign-off.

### DOC-001 — DOCX import feasibility spike (first coding-agent task)
**Deliverable:** feature inventory importer and short report from representative DOCX corpus.
**Acceptance:** classify paragraphs, styles, tables, images, headers/footers, section breaks, numbering, fields, equations, floating objects, tracked changes/comments; safely handle malformed/oversized files; document unsupported features; create golden fixtures.

### DOC-002 — DOCX to PDF render spike
**Deliverable:** isolated LibreOffice worker command/container with timeout and resource caps.
**Acceptance:** render corpus; collect page count, text blocks and page images; prove cleanup and no network; document font dependencies and render consistency.

### UX-001 — Interactive prototype
**Deliverable:** click-through or coded prototype for landing, dashboard, modes, template picker, import review, editor, validation, checkout.
**Acceptance:** 5–8 students can complete a moderated task and identify what is paid/what is checked.

## Phase 1 — Application foundation

### PLAT-001 — Monorepo and local dev environment
- Next.js web, FastAPI API, PostgreSQL, Redis, local private storage.
- `.env.example`, Compose, CI, lint/type/test commands.
- Health checks and structured request IDs.

### AUTH-001 — Authentication adapter
- Sign-in/out and session/JWT verification.
- Backend derives user identity from verified token.
- Tests for expired/invalid token.

### DB-001 — Core schema and migrations
- User, Project, Template, TemplateVersion, Document, DocumentVersion, ProcessingJob, Order/Entitlement skeleton.
- Ownership constraints and repositories.

### PROJ-001 — Project workspace
- Create/list/rename/archive/delete project.
- Report detail and version list.
- Owner-isolation tests.

### TPL-001 — Versioned template registry
- Read YAML/JSON template package into DB or deploy-time registry.
- Expose list/detail/rules endpoints.
- Template status/source/version shown in UI.

## Phase 2 — Document import and transformation

### UPLOAD-001 — Safe upload service
- Initiate/complete upload.
- Private object storage.
- ZIP/OOXML validation and configured limits.
- Quarantine and malware scan adapter.

### DOC-003 — Document inventory worker
- Parse DOCX package and build feature inventory.
- Produce support profile, warnings, checksum and import report.

### DOC-004 — Document IR v1
- Stable schema for manual authoring and supported imported structures.
- Mapping tests for paragraphs/headings/lists/tables/images.
- Preserve source provenance.

### FMT-001 — Deterministic formatting plan
- Convert template rules into dry-run operations.
- Make plan deterministic/idempotent.
- No file mutation until user accepts.

### FMT-002 — DOCX transformation v1
- Page setup, core paragraph styles, headings, simple page breaks and front-matter placeholders where data is provided.
- New immutable DocumentVersion.
- Change report and undo/restore.

### RENDER-001 — PDF render and page inspection
- Isolated LibreOffice job.
- Re-open/export checks, page count, page geometry and thumbnails.

### VAL-001 — Rule validator v1
- Page size/margins, supported typography, mandatory section presence, basic numbering.
- Finding model with rule provenance and observed/expected values.

## Phase 3 — Student experience

### WEB-001 — Landing and onboarding
- Product messaging, pricing placeholder, FAQs and login.

### WEB-002 — Student dashboard and project creation
- Recent documents and job status.

### WEB-003 — Mode selection and template picker
- Automatic/manual/hybrid workflows, applicability confirmation.

### WEB-004 — Upload/import review UI
- Progress, supported feature inventory and warnings.

### WEB-005 — Transformation preview UI
- Before/after, change summary and apply/cancel.

### EDIT-001 — Structured manual editor
- Section outline and paragraph/heading/list/table/image/caption blocks.
- Autosave and optimistic concurrency.
- Template-driven styles.

### EDIT-002 — Hybrid edit workflow
- Edit supported imported content; unsupported features remain preserved or block operation.

### WEB-006 — Validation dashboard and issue navigation
- Navigate from finding to page/block; safe fixes.

### EXP-001 — DOCX/PDF export bundle
- Finalize DOCX, render PDF, validate, store manifest.

## Phase 4 — Monetization and launch

### PAY-001 — Pricing catalogue and checkout
- Server-side product/price catalogue; amount in paise.
- Sandbox payment.

### PAY-002 — Webhook and entitlement
- Signature verification, event idempotency, reconciliation and refund state.

### PAY-003 — Export authorization
- Entitlement check for final export and re-export window.

### OPS-001 — Production deployment and observability
- Managed DB/storage, worker limits, backups, alerts, error tracking.

### LEGAL-001 — Policies and terms review
- Privacy, retention, deletion, refund, IP, disclaimer and consumer terms reviewed by qualified advisor.

### PILOT-001 — VTU student pilot
- 20–30 permissioned test reports and 15–25 student interviews.
- Measure document fidelity, time saved, correction rounds, conversion and support effort.

## Phase 5 — Expansion after signal

- Project team collaboration.
- PDF/OCR-assisted import.
- Additional VTU report types/branches after rule verification.
- Other Karnataka universities only after separate source research.
- Dissertation/internship/MBA formats after product-market evidence.
- Optional content organization assistance; no fabricated technical content.

## Recommended sequence for the first 10 agent sessions

1. Read product docs; summarize architecture and unknowns.
2. Complete DOCX import feasibility spike.
3. Complete isolated DOCX-to-PDF rendering spike.
4. Build a golden-document corpus and test harness.
5. Implement template rule model and validation unit tests.
6. Implement core database schema and project CRUD.
7. Implement safe upload + processing job flow.
8. Implement format dry-run and immutable transformation versions.
9. Implement validation findings and export pipeline.
10. Build the student UI around the proven APIs.

This order intentionally prioritizes high-risk technical proof before visual polish.
