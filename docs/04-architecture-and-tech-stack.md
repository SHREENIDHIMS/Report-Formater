# Architecture and recommended technology stack

## 1. Architecture recommendation

Use a modular monolith for the web/API/domain layer with a separate asynchronous document worker. This is simpler to operate than microservices but isolates the riskiest work: parsing and rendering untrusted office documents.

```text
Browser
  └─ Next.js web app (public site, dashboard, editor)
       └─ FastAPI application API
            ├─ PostgreSQL (users, reports, versions, rules, jobs, orders)
            ├─ Redis (job broker/cache; no document truth stored here)
            ├─ Private object storage (originals, working copies, DOCX, PDF)
            └─ Job queue
                 └─ Isolated document worker
                      ├─ DOCX package inspection / OOXML parser
                      ├─ normalization and deterministic formatter
                      ├─ LibreOffice headless rendering
                      ├─ PDF inspection (PyMuPDF)
                      └─ validator + result manifest

External adapters:
  Auth provider (Clerk proposed) | Payment gateway (Razorpay proposed)
  Email provider | Error monitoring
```

## 2. Frontend

### Next.js App Router + React + TypeScript

Why:
- Mature routing and server/client component model.
- Good fit for public marketing pages and authenticated dashboard in one web app.
- TypeScript helps keep UI data contracts predictable.
- Server-side rendering for public template/SEO pages; client-side editor where needed.

Recommended supporting tools:
- Tailwind CSS for design tokens/utilities.
- shadcn/ui or accessible Radix primitives as a starting point (review components for accessible states).
- Lucide icons.
- TanStack Query for API cache/mutations if app complexity warrants it.
- Zod for form/client schema validation where schemas are not generated from API contracts.
- React Hook Form for longer project-detail forms.
- Playwright for full browser journeys.

Pin versions in the lockfile after a fresh compatibility check. Do not chase “latest” versions in mid-sprint.

## 3. Editor recommendation

Use Tiptap/ProseMirror for structured content authoring and document blocks, but do **not** assume the editor itself provides Word-compatible pagination or round-trip fidelity for arbitrary DOCX. The canonical page preview should be produced by the same server-side document pipeline that generates the download.

A practical MVP pattern:
- Editor stores a semantic Document IR (JSON) for documents created in-app.
- A controlled conversion layer maps supported DOCX structures to/from this IR.
- A preview job generates PDF pages through LibreOffice.
- Browser preview displays those rendered pages; content editing may use an editor surface linked to the page/section model.
- For imported features that do not map cleanly, provide a preservation/limited-edit mode or block a destructive transformation.

Before selecting Tiptap paid pagination/conversion add-ons, evaluate costs and licensing. Alternatives such as a third-party office editor require license review. ONLYOFFICE Document Server Community Edition is AGPLv3; do not embed it in a closed SaaS without legal review or a commercial license decision. A simpler MVP may provide structured section editing plus server-rendered page preview instead of embedding a full Word clone.

## 4. Backend

### Python + FastAPI + Pydantic

Why:
- Python ecosystem suits DOCX/PDF processing and document automation.
- FastAPI offers typed request/response models and OpenAPI generation.
- Keep routes thin and move domain logic to services.

Recommended libraries:
- SQLAlchemy 2.x async or sync (choose one approach and use consistently).
- Alembic for migrations.
- Pydantic v2 and pydantic-settings.
- asyncpg for PostgreSQL async driver if using async SQLAlchemy.
- Celery + Redis for background work (or Dramatiq/RQ after an ADR). Job system must support retries/idempotency.
- python-docx for high-level supported edits.
- lxml for OOXML inspection/controlled XML editing.
- docxtpl for filling verified template documents where useful.
- PyMuPDF for PDF pages/text/geometry inspection.
- Pillow for safe image metadata/preprocessing.
- Boto3 for S3-compatible storage.
- pytest, pytest-asyncio, Ruff, mypy.

## 5. Database and storage

- PostgreSQL: canonical metadata, users, project ownership, documents, versions, templates, rules, findings, jobs, payments and entitlements.
- Redis: transient queue/broker and short-lived cache only.
- Object storage: private S3-compatible bucket for originals, transformed DOCX, rendered PDF and image assets. In local development use a private filesystem folder outside the web static directory.
- Use UUID/ULID IDs; never expose sequential database IDs as authorization tokens.
- Store checksum, MIME, size, page count, import profile, template version and pipeline version for each document version.

## 6. Document worker

Run separately from web/API. It handles untrusted Office/PDF inputs.
- Run non-root.
- No outbound network access by default.
- Read/write only a job-scoped temporary directory and object storage through controlled credentials.
- CPU/memory/time/file-size limits.
- Remove temporary files after completion.
- Avoid macro execution. Reject macro-enabled formats in MVP (.docm, .dotm, .xlsm).
- Use LibreOffice in headless isolated process/container; enforce timeout and process cleanup.
- Never mount credentials or Docker socket into a conversion container.

## 7. Authentication and payments

Proposed MVP vendors:
- Clerk for hosted authentication (confirm pricing, regional/data-processing terms and secure backend JWT verification).
- Razorpay for Indian one-time payments (confirm current product, webhook and settlement requirements).

Do not couple business domain to vendor-specific objects. Define `AuthProvider` and `PaymentGateway` adapters. Verify signatures server-side, persist raw event metadata without unnecessary personal/payment secrets, and process idempotently.

## 8. Deployment

- Web: managed Next.js hosting or container deployment.
- API: container service.
- Worker: separate container service with CPU/memory limits and autoscaling by queue depth.
- PostgreSQL: managed database with automated backups/PITR.
- Redis: managed/secured service.
- Storage: private S3-compatible bucket in an appropriate India region where available and suitable.
- CDN only for public assets; private document downloads must be authorized and short-lived.

Do not deploy LibreOffice into a typical serverless function unless its runtime/time/resource characteristics are explicitly validated.

## 9. Why not start with microservices?

At MVP scale, multiple independent services increase operational overhead. Keep bounded modules inside one API codebase: identity, projects, templates, documents, validation, billing. Separate only the document worker because its security and resource profile are materially different.

## 10. Proposed repository module boundaries

```text
apps/api/app/
  api/v1/                 # HTTP routers and dependencies
  core/                   # config, logging, errors, auth context
  domain/                 # value objects, enums, domain policies
  models/                 # SQLAlchemy ORM
  schemas/                # Pydantic request/response
  services/               # use cases
  repositories/           # persistence queries
  jobs/                   # enqueue/dispatch/background job contracts
  document_engine/        # inspect, import, IR, transform, render, validate
  integrations/            # auth, payment, object storage, email
  migrations/             # Alembic (location can be app/alembic)
  tests/
apps/web/src/
  app/ components/ features/ lib/ styles/
```

## 11. Tech-stack decision summary

| Layer | Recommendation | Reason |
|---|---|---|
| Web | Next.js + React + TypeScript | product site + dashboard/editor |
| UI | Tailwind + accessible primitives | consistent fast UI work |
| Structured editing | Tiptap/ProseMirror (after spike) | semantic editor blocks; not pagination guarantee |
| API | FastAPI + Pydantic | Python document ecosystem and typed APIs |
| DB | PostgreSQL + SQLAlchemy + Alembic | transactional metadata and migrations |
| Jobs | Redis + Celery | asynchronous document tasks |
| DOCX | python-docx + lxml/OOXML | high-level operations + explicit package handling |
| PDF | LibreOffice + PyMuPDF | render actual DOCX and inspect pages |
| Storage | private S3-compatible object store | scalable private binary storage |
| Auth | Clerk adapter (proposed) | managed login while keeping domain decoupled |
| Payments | Razorpay adapter (proposed) | Indian one-time payment support |
| Testing | pytest, Vitest, Playwright | unit/integration/e2e coverage |
| Monitoring | Sentry + structured logs/metrics | detect processing failures |

## 12. Version policy

This starter records sensible major-version choices, not a promise that every package remains latest. Before implementation, run a compatibility check, pin exact versions, commit lockfiles, and record the checked date. Upgrade deliberately with regression tests—especially for Next.js, React, Tiptap, python-docx, LibreOffice and payment SDKs.
