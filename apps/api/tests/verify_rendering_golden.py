"""Re-render the corpus and compare semantic and visual golden outputs."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import fitz
from collect_rendering_golden import (
    FIXTURES,
    GOLDEN,
    _normalize_text,
    _run_worker,
    _sha256,
)


def verify(source: Path, expected: dict, work: Path) -> None:
    _run_worker(source, work)
    pdf = work / "input.pdf"
    with fitz.open(pdf) as document:
        assert len(document) == expected["page_count"], source.name
        for index, page in enumerate(document):
            dimensions = [
                round(page.rect.width * 25.4 / 72, 2),
                round(page.rect.height * 25.4 / 72, 2),
            ]
            assert dimensions == expected["page_dimensions_mm"][index], source.name
            assert _normalize_text(page.get_text("text")) == expected[
                "normalized_text_by_page"
            ][index], source.name
            image = work / f"page-{index + 1:03d}.png"
            page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False).save(image)
            assert _sha256(image) == expected["page_image_sha256"][index], source.name


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="vtu-golden-verify-") as root:
        root_path = Path(root)
        for source in sorted(FIXTURES.glob("*.docx")):
            manifest = json.loads(
                (GOLDEN / source.stem / "manifest.json").read_text(encoding="utf-8")
            )
            assert _sha256(source) == manifest["input_sha256"]
            verify(source, manifest, root_path / source.stem)
            print(f"Verified {source.name}")
