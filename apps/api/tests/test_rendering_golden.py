"""Local comparison checks for captured DOC-002.1 golden artifacts."""

import hashlib
import json
import re
from pathlib import Path

import fitz

GOLDEN = Path(__file__).parent / "rendering_golden"


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_golden_corpus_has_expected_artifacts():
    manifests = sorted(GOLDEN.glob("*/manifest.json"))
    assert len(manifests) >= 6
    for manifest_path in manifests:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        folder = manifest_path.parent
        pdf = folder / "rendered.pdf"
        assert pdf.is_file()
        assert _sha256(pdf) == manifest["output_pdf_sha256"]
        assert manifest["input_sha256"]
        assert len(manifest["page_image_sha256"]) == manifest["page_count"]
        for index, image_hash in enumerate(manifest["page_image_sha256"], start=1):
            image = folder / f"page-{index:03d}.png"
            assert image.is_file()
            assert _sha256(image) == image_hash


def test_golden_pdf_matches_manifest_content_and_geometry():
    for manifest_path in sorted(GOLDEN.glob("*/manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        with fitz.open(manifest_path.parent / "rendered.pdf") as document:
            assert len(document) == manifest["page_count"]
            for index, page in enumerate(document):
                dimensions = [
                    round(page.rect.width * 25.4 / 72, 2),
                    round(page.rect.height * 25.4 / 72, 2),
                ]
                assert dimensions == manifest["page_dimensions_mm"][index]
                assert (
                    _normalize(page.get_text("text")) == manifest["normalized_text_by_page"][index]
                )
                is_blank = (
                    not _normalize(page.get_text("text"))
                    and not page.get_images(full=True)
                    and not page.get_drawings()
                )
                assert is_blank is manifest["has_blank_pages"] or not is_blank
