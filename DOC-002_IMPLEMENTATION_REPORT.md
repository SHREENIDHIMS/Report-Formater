# DOC-002: DOCX-to-PDF Rendering Feasibility Spike

## Outcome

The rendering spike now has a read-only conversion service, structured PDF
inspection, deterministic tests, and a Docker worker definition for isolated
LibreOffice execution. The host environment does not have LibreOffice
installed, so real binary conversion still needs to be run in Docker.

## Files changed

- apps/api/app/rendering/converter.py
  - Validates DOCX extension, ZIP signature, existence, and 50 MB input limit.
  - Computes a SHA-256 checksum before processing.
  - Copies the source to a job-scoped directory; the source is never opened for writing.
  - Runs LibreOffice headlessly with macro-safe flags and a hard timeout.
  - Rejects missing, empty, corrupt, zero-page, over-limit, or failed PDF output.
  - Extracts page count, page dimensions in millimetres, and a blank-page flag with PyMuPDF.
  - Cleans the private temporary directory by default. A caller-provided directory is retained.
- apps/api/app/rendering/models.py
  - Typed ConversionStatus and ConversionResult models.
- apps/api/tests/test_rendering_spike.py
  - Seven collected tests covering success, metadata, blank pages, timeout, invalid DOCX,
    missing LibreOffice, cleanup, non-zero conversion, and source immutability.
  - LibreOffice is mocked at the subprocess boundary for reliable CI.
- apps/api/worker/rendering/Dockerfile
  - Installs LibreOffice Writer and fonts in a dedicated worker image.
  - Runs as a non-root user with a private writable /work directory.
- apps/api/worker/rendering/entrypoint.py
  - Executes one input/output job and emits structured result JSON.
- apps/api/pyproject.toml
  - Makes both API and repository package roots available to pytest.
- apps/api/tests/test_docx_import_spike.py
  - Makes DOC-001 fixtures independent of the current working directory.

## Test results

From apps/api:

    python -m pytest tests/test_docx_import_spike.py tests/test_rendering_spike.py -q
    18 passed in 0.86s

Ruff passes for the changed rendering module and both affected test files.
The broader repository still contains pre-existing lint findings in DOC-001
modules and the API scaffold.

The full tests suite was attempted. It hangs in the existing
tests/test_health.py while constructing/requesting FastAPI TestClient; that
test is unrelated to this spike and was stopped after the targeted suites
completed. This is recorded as an existing test-environment issue, not a
DOC-002 pass.

## Isolation and security

The production execution contract is the container, not a Windows-host
LibreOffice installation. The worker should be launched with:

- --network=none;
- read-only input mount and private job output mount;
- non-root user;
- Docker CPU, memory, PID, and wall-clock limits;
- no credentials or application secrets in the worker environment.

The converter enforces input size, timeout, page count, source copying, and
cleanup. Docker is required for OS-level memory, CPU, network, and process
isolation controls.

## Rendering limitations

- Layout fidelity depends on LibreOffice version, installed fonts, locale, and
  available fonts; it is not proof of Microsoft Word identity.
- Tables, images, headers, footers, fields, equations, and complex OOXML need
  golden-document comparison after real conversion. DOC-001 warnings remain
  authoritative for unsupported or limited editing.
- Blank-page detection is heuristic.
- Queueing, authorization, signed URLs, object storage, and API endpoints are
  out of scope for this spike.
- Real conversion of the representative corpus must run in Docker before
  claiming end-to-end rendering support.

## Comparison with DOC-001

DOC-001 remains the read-only OOXML and package inspection layer. DOC-002 uses
the same immutable source concept but does not transform the document: it
creates a separate working copy and PDF artifact. DOC-001 identifies
preservation risks before transformation; DOC-002 inspects visual output after
a document version is selected.

## Recommended next milestone

Run the rendering corpus through Docker and capture golden PDF page images,
text, geometry, and source checksums. Then implement DOC-003/Document IR only
after the corpus demonstrates which DOC-001 constructs can safely round-trip.
