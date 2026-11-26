# Coding Agent Instructions — VTU Report Studio

Read this file and the relevant `docs/` pages before changing code. The PRD is the product source of truth; architecture decisions (ADRs) govern implementation trade-offs. When documents conflict, do not guess: identify the conflict and propose an ADR/update.

## Mission
Build a reliable, student-first VTU report formatting web app. The product imports or creates student-authored report content, applies a selected versioned format, lets students review/edit the result, validates document rules, and exports DOCX/PDF.

## Start every task by
1. Read `docs/01-product-requirements-document.md` and the relevant subsystem specification.
2. Identify user-visible behaviour, data mutations, security boundaries, and test cases.
3. Inspect existing code and patterns before creating new abstractions.
4. State assumptions and any requirement that cannot be proven from current VTU source material.
5. Implement the smallest end-to-end vertical slice; do not scaffold unrelated features.

## Product guardrails
- No college portal or faculty onboarding in MVP. A future template-contribution flow must not block student self-service.
- Support three workflows: `automatic`, `manual`, `hybrid`.
- Free users can inspect a limited preview/validation before purchase; paid entitlement controls the agreed final export/revision window. Entitlements must be enforced server-side.
- The original uploaded file is immutable. All transformations create a new document version and audit record.
- Never silently drop text, images, equations, tables, hyperlinks, headers/footers, bookmarks, comments, fields, section breaks or other OOXML content. If a feature cannot be preserved, disclose it and block or ask for explicit approval.
- Do not generate or alter a student's technical results, claims, citations, data, experiment outcomes, or signatures. No AI-writing functionality in the MVP.
- Do not describe a score as university approval. Validation means “checked against this selected template version”.
- Do not put secrets, uploaded document content, payment data or personally identifying student information into logs.

## VTU rule source discipline
- `templates/vtu/be-btech-project-report/rules.yaml` is a `research-draft`, not a blanket official standard.
- Store provenance for every rule: source title, URL, section/page if available, checked date, scheme applicability, confidence/status.
- Do not hardcode a font family unless a verified applicable source specifies it. The current source baseline specifies several font sizes and alignments, but does not establish one universal family in the cited formatting passage.
- Do not silently infer scheme applicability. The official site lists multiple B.E./B.Tech. schemes; cohort applicability is an open verification item.
- College-specific overrides are user-supplied custom rules in MVP; they do not imply a partnership or endorsement.

## Architecture guardrails
- Keep the document-processing worker isolated from the public web/API process. LibreOffice conversion must run in a constrained container/process with time, memory, file-size and network limits.
- Use asynchronous background jobs for import, structural analysis, transformation, PDF rendering and validation.
- Store file metadata and object keys in PostgreSQL; store binaries in private object storage/local private volume. Use short-lived signed download URLs only after authorization.
- Use idempotency keys for upload finalization, payment webhooks, transformation jobs and export requests.
- Use database migrations (Alembic). Never alter production schema manually.
- Validate MIME type, extension, magic bytes, ZIP/OOXML structure, compressed/uncompressed size and archive entry count. Treat DOCX as untrusted ZIP input.
- Avoid loading whole large documents into the web request process. Enforce upload and page limits.
- API responses use typed Pydantic schemas; API routes do not contain document manipulation logic.
- Use decimal/integer minor units for money; never use floating point to calculate charges.

## Stack defaults
- Web: Next.js App Router, React, TypeScript, Tailwind CSS, accessible component primitives.
- API: Python + FastAPI + Pydantic.
- Data: PostgreSQL, SQLAlchemy 2, Alembic.
- Jobs: Redis + Celery (or a documented replacement ADR).
- DOCX: python-docx for supported high-level operations plus lxml/OOXML package inspection and carefully isolated low-level OOXML transformations.
- Rendering: LibreOffice headless in worker container; PyMuPDF for PDF inspection. Browser editor is structured-authoring UI, not the canonical DOCX renderer.
- Auth/payments: provider adapters; Clerk/Razorpay are proposed MVP choices, not coupled into domain logic.

## Quality gates
For each change:
- Add/adjust unit tests and integration tests.
- Test authorization with owner A attempting to access owner B's records/files.
- Test malformed/malicious DOCX and oversized files where relevant.
- For document changes, run golden-document tests and compare both extracted structure and rendered pages.
- Run format/lint/type checks for affected packages.
- Add API examples and update docs when contracts change.
- No flaky sleep-based async tests; use deterministic job fakes/fixtures.
- Never mark an item complete because code compiles alone.

## Required definition of done
A task is done only when:
1. Acceptance criteria in the backlog are met.
2. Tests cover success, validation failure and authorization/error paths.
3. Relevant docs/schema/API contracts are updated.
4. No known data-loss regression is hidden.
5. UI has loading, empty, error and success states where applicable.
6. The agent summarizes files changed, commands/tests run, results, known limits and next ticket.

## Git workflow
- Use short feature branches and small commits.
- Avoid broad refactors while implementing a vertical slice.
- Never commit `.env`, secrets, student documents, generated reports, payment credentials, or local database volumes.
- Do not change dependency versions casually; explain changes in an ADR or PR summary.

## Suggested first coding-agent task
Implement `DOC-001: DOCX import feasibility spike` from `docs/13-roadmap-and-backlog.md` before building the editor. Use a deliberately varied corpus (paragraphs, section breaks, headers/footers, tables, figures, captions, equations, hyperlinks, page fields). Write down what is preserved, normalized, unsupported and how the user is warned. Do not claim general DOCX support until this spike passes.
