# VTU Report Studio — Starter Kit

A student-first web application for creating, importing, editing, checking and exporting VTU engineering project reports. This repository is a **coding-agent-ready product specification and technical scaffold**, not a finished SaaS product.

## Product direction

- Independent student-facing SaaS. No college or faculty onboarding is required for the initial release.
- Start with VTU B.E./B.Tech. project reports and a deliberately small set of verified template variants.
- Three creation modes: **Automatic**, **Manual**, and **Hybrid**.
- Primary differentiator: reliable, transparent document transformation and validation—not AI-generated project content.
- Export editable DOCX and print-ready PDF. Preserve source content and never silently discard unsupported Word features.
- Monetize per report/project first. Test a time-limited project pass later; do not assume monthly subscriptions fit seasonal usage.

## Read these first

1. [`AGENTS.md`](AGENTS.md) — rules for any coding agent.
2. [`docs/01-product-requirements-document.md`](docs/01-product-requirements-document.md) — authoritative MVP PRD.
3. [`docs/04-architecture-and-tech-stack.md`](docs/04-architecture-and-tech-stack.md) — system design and stack decisions.
4. [`docs/05-document-engine-design.md`](docs/05-document-engine-design.md) — most technically important subsystem.
5. [`docs/06-vtu-guideline-baseline.md`](docs/06-vtu-guideline-baseline.md) and [`templates/vtu/be-btech-project-report/`](templates/vtu/be-btech-project-report/) — source-aware rule baseline; it is marked `research-draft` until checked against the student’s cohort and any college circular.
6. [`docs/13-roadmap-and-backlog.md`](docs/13-roadmap-and-backlog.md) — phased implementation tickets and acceptance criteria.
7. [`docs/17-open-questions-and-risks.md`](docs/17-open-questions-and-risks.md) — known unknowns and release blockers.

## Repository structure

```text
vtu-report-studio-starter/
├── AGENTS.md                    # agent instructions and guardrails
├── CLAUDE.md                    # Claude Code entrypoint (points to AGENTS.md)
├── README.md
├── .env.example
├── .gitignore
├── .editorconfig
├── compose.yaml                 # local PostgreSQL + Redis
├── Makefile
├── package.json                 # pnpm workspace root
├── pnpm-workspace.yaml
├── apps/
│   ├── web/                     # Next.js App Router starter
│   └── api/                     # FastAPI starter + health test
├── packages/shared/             # reserved for shared API/schema contracts
├── templates/vtu/               # machine-readable, versioned template rules
├── docs/                        # PRD, UX, architecture, data/API/security, plans
├── scripts/                     # local helper scripts
└── .github/workflows/           # CI starter
```

## Prerequisites

- Node.js 22 LTS (or a currently supported Node.js version compatible with the pinned Next.js release).
- pnpm 10.x.
- Python 3.12+ and `uv`.
- Docker Desktop / Docker Engine with Compose.
- Git.
- For DOCX-to-PDF visual verification: LibreOffice installed locally or use the isolated document-worker container described in the architecture document.

## Start the scaffold

### 1. Configure environment

```bash
cp .env.example .env
```

Review all values. The example is for local development only. Never use the example secrets in any shared or production environment.

### 2. Start infrastructure

```bash
docker compose up -d postgres redis
```

### 3. Start the API

```bash
cd apps/api
uv sync --all-groups
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health endpoint: `http://127.0.0.1:8000/api/v1/health`.

### 4. Start the web app

In another terminal:

```bash
pnpm install
pnpm --filter @vtu-report-studio/web dev
```

Open `http://localhost:3000`.

### 5. Run tests and checks

```bash
# API
cd apps/api
uv sync --locked --all-groups
uv run --locked pytest
uv run --locked ruff check .
uv run --locked ruff format --check app tests
uv run mypy app

# Web (from repository root)
pnpm install --frozen-lockfile
pnpm --filter @vtu-report-studio/web lint
pnpm --filter @vtu-report-studio/web typecheck
pnpm --filter @vtu-report-studio/web build
```

The commands are a starting point; the scaffold does not yet contain the complete business modules described in the PRD.

## What is implemented in this starter

- Minimal Next.js landing screen describing the three workflows.
- FastAPI application factory and `/api/v1/health` endpoint.
- Basic API test.
- Local PostgreSQL and Redis Compose services.
- Environment template, workspace metadata, CI skeleton, template manifest/rule draft, and detailed implementation documentation.

## What is not implemented yet

Authentication, user/project persistence, DOCX upload and transformation, paginated document editor, template administration, compliance checking, PDF rendering, payments, entitlement checks, team collaboration, OCR, and production deployment are **specifications/backlog items**, not working features. Do not tell users these features exist until implemented and tested.

## Non-negotiable product principles

1. **Source preservation:** never overwrite the original upload. Transform a copy and keep version history.
2. **No silent data loss:** detect unsupported or risky DOCX structures and report them before export.
3. **Rule transparency:** each validation finding links to the template rule and source/version.
4. **No fabricated academic content:** no invented experiments, results, references, acknowledgements, guide signatures or approvals.
5. **User control:** show a preview and change summary before the student applies formatting or pays.
6. **Privacy by default:** reports are private, scoped to their owner/team, and deletable with documented retention rules.
7. **Template provenance:** never market a draft rule set as “officially approved” or “guaranteed VTU compliant”.

## Research status

The VTU baseline in this repository uses the official VTU Examination Guidelines and the VTU-hosted *Guidelines for the final year project work* PDF linked in the source register. The PDF was hosted under a November 2025 upload path. Applicability to each scheme/cohort and additional college rules must be verified before publishing a template. See [`docs/18-research-sources.md`](docs/18-research-sources.md).

## License

No product license has been selected. Keep this repository private until you choose a license and review third-party package/editor/document-engine licensing. In particular, review AGPL/commercial obligations before embedding a full office suite.
