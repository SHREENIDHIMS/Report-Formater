"""Deterministic DOC-002 rendering tests; LibreOffice is mocked in-process."""

from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile

import fitz
import pytest
from apps.api.app.rendering import convert_docx_to_pdf, converter
from apps.api.app.rendering.models import ConversionStatus

FIXTURE = Path("tests/rendering_fixtures/simple_report.docx")


def _fake_success(*, blank: bool = False):
    def run(command, **kwargs):
        output_dir = Path(command[command.index("--outdir") + 1])
        with fitz.open() as document:
            page = document.new_page(width=595, height=842)
            if not blank:
                page.insert_text((72, 72), "VTU Report Studio rendering fixture")
            document.save(output_dir / "input.pdf")

        class Completed:
            returncode = 0
            stdout = ""
            stderr = ""

        return Completed()

    return run


def test_success_extracts_metadata_and_preserves_source(monkeypatch, tmp_path):
    source_bytes = FIXTURE.read_bytes()
    monkeypatch.setattr(converter, "_find_libreoffice", lambda: "libreoffice")
    monkeypatch.setattr(converter.subprocess, "run", _fake_success())

    result = convert_docx_to_pdf(str(FIXTURE), temp_dir=str(tmp_path / "job"))

    assert result.status == ConversionStatus.SUCCEEDED
    assert result.page_count == 1
    assert result.page_dimensions_mm is not None
    assert result.page_dimensions_mm[0][0] == pytest.approx(210, abs=0.2)
    assert result.page_dimensions_mm[0][1] == pytest.approx(297, abs=0.2)
    assert result.has_blank_pages is False
    assert result.output_pdf_path is not None
    assert Path(result.output_pdf_path).is_file()
    assert sha256(FIXTURE.read_bytes()).digest() == sha256(source_bytes).digest()


def test_blank_page_is_reported(monkeypatch, tmp_path):
    monkeypatch.setattr(converter, "_find_libreoffice", lambda: "libreoffice")
    monkeypatch.setattr(converter.subprocess, "run", _fake_success(blank=True))

    result = convert_docx_to_pdf(str(FIXTURE), temp_dir=str(tmp_path / "job"))

    assert result.status == ConversionStatus.SUCCEEDED
    assert result.has_blank_pages is True


def test_timeout_is_reported(monkeypatch, tmp_path):
    def timeout(*args, **kwargs):
        raise converter.subprocess.TimeoutExpired("libreoffice", kwargs["timeout"])

    monkeypatch.setattr(converter, "_find_libreoffice", lambda: "libreoffice")
    monkeypatch.setattr(converter.subprocess, "run", timeout)

    result = convert_docx_to_pdf(str(FIXTURE), timeout_seconds=1, temp_dir=str(tmp_path / "job"))

    assert result.status == ConversionStatus.FAILED
    assert "timed out" in (result.error or "")


def test_invalid_docx_and_missing_libreoffice_fail_safely(tmp_path, monkeypatch):
    invalid = tmp_path / "invalid.docx"
    invalid.write_bytes(b"not a zip")
    result = convert_docx_to_pdf(str(invalid), temp_dir=str(tmp_path / "invalid-job"))
    assert result.status == ConversionStatus.FAILED
    assert "valid DOCX" in (result.error or "")

    monkeypatch.setattr(converter, "_find_libreoffice", lambda: None)
    result = convert_docx_to_pdf(str(FIXTURE))
    assert result.status == ConversionStatus.FAILED
    assert "isolated rendering worker" in (result.error or "")


def test_macro_part_is_rejected_before_libreoffice(tmp_path, monkeypatch):
    macro_docx = tmp_path / "macro.docx"
    macro_docx.write_bytes(FIXTURE.read_bytes())
    with ZipFile(macro_docx, "a") as archive:
        archive.writestr("word/vbaProject.bin", b"not executable")

    monkeypatch.setattr(converter, "_find_libreoffice", lambda: "libreoffice")
    result = convert_docx_to_pdf(str(macro_docx), temp_dir=str(tmp_path / "job"))

    assert result.status == ConversionStatus.FAILED
    assert "macro-enabled part rejected" in (result.error or "")


def test_default_job_directory_is_cleaned(monkeypatch):
    monkeypatch.setattr(converter, "_find_libreoffice", lambda: "libreoffice")
    monkeypatch.setattr(converter.subprocess, "run", _fake_success())

    result = convert_docx_to_pdf(str(FIXTURE))

    assert result.status == ConversionStatus.SUCCEEDED
    assert result.output_pdf_path is None


def test_nonzero_converter_is_a_failure(monkeypatch, tmp_path):
    class Failed:
        returncode = 1
        stdout = ""
        stderr = "conversion error"

    monkeypatch.setattr(converter, "_find_libreoffice", lambda: "libreoffice")
    monkeypatch.setattr(converter.subprocess, "run", lambda *args, **kwargs: Failed())
    result = convert_docx_to_pdf(str(FIXTURE), temp_dir=str(tmp_path / "job"))
    assert result.status == ConversionStatus.FAILED
    assert "conversion failed" in (result.error or "")


def test_invalid_pdf_output_is_a_failure(monkeypatch, tmp_path):
    def invalid_pdf(command, **kwargs):
        output_dir = Path(command[command.index("--outdir") + 1])
        (output_dir / "input.pdf").write_bytes(b"not a PDF")

        class Completed:
            returncode = 0
            stdout = ""
            stderr = ""

        return Completed()

    monkeypatch.setattr(converter, "_find_libreoffice", lambda: "libreoffice")
    monkeypatch.setattr(converter.subprocess, "run", invalid_pdf)
    result = convert_docx_to_pdf(str(FIXTURE), temp_dir=str(tmp_path / "job"))
    assert result.status == ConversionStatus.FAILED
    assert "Invalid PDF output" in (result.error or "")
