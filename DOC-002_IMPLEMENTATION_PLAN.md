# DOC-002: DOCX to PDF Rendering Feasibility Spike — Implementation Plan

## Objective
Establish a reliable pipeline to render uploaded DOCX documents into PDFs without modifying the original. The rendering engine must be isolated, resource-constrained, and produce structured metadata about the rendered output.

## Scope
This spike focuses on the document processing worker's rendering capability. It does NOT include:
- Full SaaS implementation
- User authentication
- Payment/entitlement checks
- Template rule application
- Editor integration

## Architecture

```
Browser/Worker
│
├─ API Process (FastAPI)
│   └─ Renders requests, enqueues jobs, stores metadata
│
├─ Document Worker Container (Docker)
│   └─ Isolated, no-network, resource-limited
│       ├─ Receives: DOCX file path
│       ├─ Produces: PDF file path + metadata JSON
│       └─ Cleanup: temp files removed on completion
│
└─ API Process
    └─ Reads metadata, serves PDF via signed URL
```

## Core Requirements

### 1. Isolation
- Docker container or separate process with no outbound network
- Read-only access to input DOCX
- Write access only to job-scoped temporary directory
- No macro execution
- No credential/env exposure

### 2. Resource Limits
- **Timeout**: Max 60 seconds per DOCX→PDF conversion (configurable)
- **Memory**: Max 512 MB RAM (configurable)
- **File size**: Max 50 MB input DOCX (same as upload limit)
- **Output PDF**: No explicit size limit, but practical page count cap (e.g., 200 pages)

### 3. Output Metadata
Structured result containing:
- `job_id`
- `input_docx_checksum` (SHA-256)
- `output_pdf_path` (temporary, signed URL later)
- `page_count`
- `page_size` (A4, Letter, etc.)
- `page_dimensions_mm` [[width, height], ...]
- `has_blank_pages` (boolean)
- `error` (if conversion failed)
- `worker_version`
- `duration_seconds`

### 4. Failure Modes Handled
- Invalid/non-DOCX input
- LibreOffice not available
- Conversion timeout
- Corrupt PDF output
- Excessive page count (>200)
- Missing output file

## Implementation Plan

### Phase 1: Worker Module (this spike)
Build the isolated rendering module that:
- Accepts DOCX file path as input
- Invokes LibreOffice headless conversion
- Captures PDF metadata (page count, dimensions)
- Detects blank pages
- Returns structured result
- Cleans up temporary files
- Handles all error cases gracefully

### Phase 2: API Integration
- POST /api/v1/docx-to-pdf endpoint
- Enqueues job to worker via Redis/Celery
- Returns job ID immediately
- GET /api/v1/docx-to-pdf/{job_id} status endpoint
- signed URL for PDF download after completion

### Phase 3: Test Corpus
Curated DOCX fixtures covering:
- Simple 1-page report
- Multi-section report with page numbering
- Report with tables and images
- Report with headers/footers
- Multi-page report (>10 pages)
- Invalid/non-DOCX input
- Document with equations/OMML

## Security Checklist
- [ ] Never modify original DOCX
- [ ] Never execute document macros
- [ ] Disable network access for rendering workers
- [ ] Apply memory, CPU and time limits
- [ ] Clean up temporary files after completion
- [ ] Do not expose arbitrary filesystem access
- [ ] Validate input MIME type and extension before processing
- [ ] Reject .docm, .dotm (macro-enabled) in MVP

## Test Fixtures Needed
Same 3+ fixtures from DOC-001 plus:
- Multi-page report (10+ pages)
- Report with equations
- Report with floating images
- Invalid DOCX (corrupt ZIP, non-DOCX file)

## Deliverables for This Spike
1. Rendering worker module (`apps/api/app/rendering/`)
2. Docker worker configuration (Dockerfile, entrypoint)
3. Structured result models (Pydantic schemas)
4. Test corpus of DOCX→PDF conversions
5. 8+ automated tests covering success, failure, and edge cases
6. Documentation of rendering limitations

## Success Criteria
- [ ] DOCX→PDF conversion works for simple reports
- [ ] PDF metadata (page count, dimensions) extracted correctly
- [ ] Blank pages detected and reported
- [ ] Invalid inputs handled without crashing
- [ ] Timeout enforced (no infinite hangs)
- [ ] Temporary files cleaned up
- [ ] Security boundaries respected (no network, no macros)
- [ ] All test fixtures produce valid PDF output

## Next Steps After Spike
1. DOC-003: Document IR v1 (stable schema for manual authoring)
2. DOC-004: Template rule model and validation
3. Integration with document import flow
4. PDF download via signed, authorized URLs
5. Entitlement check before export

## Dependencies
- LibreOffice headless (installation in worker container)
- PyMuPDF (for PDF metadata inspection)
- python-docx (for pre-conversion inspection)
- Redis + Celery (for job queuing, optional for spike)
- Docker (for worker isolation)