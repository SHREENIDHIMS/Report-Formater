"""Read-only DOCX to PDF rendering for an isolated document worker."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

from ..document_engine.importing.package_validation import validate_docx_package
from .models import ConversionResult, ConversionStatus

MAX_CONVERSION_SECONDS = 60
MAX_INPUT_BYTES = 50 * 1024 * 1024
MAX_PAGES = 200
TEMP_DIR_PREFIX = "vtu_render_"


def _compute_checksum(filepath: str) -> str:
    digest = hashlib.sha256()
    with open(filepath, "rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _find_libreoffice() -> str | None:
    return shutil.which("libreoffice") or shutil.which("soffice")


def _is_docx_file(filepath: str) -> bool:
    if Path(filepath).suffix.lower() != ".docx":
        return False
    try:
        with open(filepath, "rb") as source:
            return source.read(4) == b"PK\x03\x04"
    except OSError:
        return False


def _inspect_pdf(pdf_path: Path) -> tuple[int, list[list[float]], bool]:
    import fitz

    with fitz.open(pdf_path) as document:
        dimensions: list[list[float]] = []
        has_blank_pages = False
        for page in document:
            dimensions.append(
                [
                    round(page.rect.width * 25.4 / 72, 2),
                    round(page.rect.height * 25.4 / 72, 2),
                ]
            )
            is_empty = (
                not page.get_text("text").strip()
                and not page.get_images(full=True)
                and not page.get_drawings()
            )
            if is_empty:
                has_blank_pages = True
        return len(document), dimensions, has_blank_pages


def convert_docx_to_pdf(
    docx_path: str,
    *,
    timeout_seconds: int = MAX_CONVERSION_SECONDS,
    temp_dir: str | None = None,
) -> ConversionResult:
    """Convert one DOCX in a job-scoped directory.

    An explicit temp_dir is caller-owned and retains the generated PDF. With
    no directory supplied, the private job directory is removed before return.
    """
    result = ConversionResult(job_id=uuid.uuid4().hex, status=ConversionStatus.PENDING)
    started = time.monotonic()
    source = Path(docx_path)
    work_dir: Path | None = None
    caller_owned = temp_dir is not None
    try:
        if not source.is_file():
            raise ValueError("Input file not found")
        result.source_docx_checksum = _compute_checksum(str(source))
        if not _is_docx_file(str(source)):
            raise ValueError("Input file is not a valid DOCX")
        if source.stat().st_size > MAX_INPUT_BYTES:
            raise ValueError(f"Input DOCX exceeds size limit of {MAX_INPUT_BYTES} bytes")
        package = validate_docx_package(source, max_file_bytes=MAX_INPUT_BYTES)
        if not package.valid:
            raise ValueError(f"Unsafe DOCX package: {package.errors[0]}")
        work_dir = (
            Path(temp_dir).resolve() if temp_dir else Path(tempfile.mkdtemp(prefix=TEMP_DIR_PREFIX))
        )
        work_dir.mkdir(parents=True, exist_ok=True)
        input_copy = work_dir / "input.docx"
        shutil.copyfile(source, input_copy)
        libreoffice_profile = work_dir / "lo-profile"
        libreoffice_profile.mkdir(exist_ok=True)
        libreoffice = _find_libreoffice()
        if libreoffice is None:
            raise RuntimeError("LibreOffice is not available; use the isolated rendering worker")
        result.status = ConversionStatus.PROCESSING
        completed = subprocess.run(
            [
                libreoffice,
                "--headless",
                "--nologo",
                "--nodefault",
                "--norestore",
                "--invisible",
                f"-env:UserInstallation={libreoffice_profile.as_uri()}",
                "--convert-to",
                "pdf",
                "--outdir",
                str(work_dir),
                str(input_copy),
            ],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "").strip()[:1000]
            suffix = f": {detail}" if detail else ""
            raise RuntimeError(
                f"LibreOffice conversion failed (exit code {completed.returncode}){suffix}"
            )
        generated = work_dir / "input.pdf"
        if not generated.is_file() or generated.stat().st_size == 0:
            raise RuntimeError("LibreOffice did not produce a non-empty PDF")
        try:
            page_count, dimensions, has_blank_pages = _inspect_pdf(generated)
        except Exception as exc:
            raise RuntimeError(f"Invalid PDF output: {exc}") from exc
        if page_count == 0:
            raise RuntimeError("Rendered PDF contains no pages")
        if page_count > MAX_PAGES:
            raise RuntimeError(f"Rendered PDF exceeds the {MAX_PAGES}-page limit")
        result.status = ConversionStatus.SUCCEEDED
        result.page_count = page_count
        result.page_dimensions_mm = dimensions
        result.has_blank_pages = has_blank_pages
        if caller_owned:
            result.output_pdf_path = str(generated)
    except subprocess.TimeoutExpired:
        result.status = ConversionStatus.FAILED
        result.error = f"Conversion timed out after {timeout_seconds} seconds"
    except (OSError, ValueError, RuntimeError) as exc:
        result.status = ConversionStatus.FAILED
        result.error = str(exc)
    finally:
        result.duration_seconds = round(time.monotonic() - started, 4)
        if work_dir is not None and not caller_owned:
            shutil.rmtree(work_dir, ignore_errors=True)
    return result
