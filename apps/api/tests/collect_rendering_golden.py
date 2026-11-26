"""Run the isolated worker and capture DOC-002.1 golden artifacts."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

import fitz

FIXTURES = Path(__file__).parent / "rendering_fixtures"
GOLDEN = Path(__file__).parent / "rendering_golden"
IMAGE = "vtu-report-studio-renderer:doc0021"
IMAGE_ID = "sha256:77f3ed444ba9988d1069013acb7081a2e7e9997c120d994d4e8dcd3295d1c561"
LO_VERSION = "4:25.2.3-2+deb13u12"
BASE_DIGEST = "sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run_worker(source: Path, job_dir: Path) -> dict:
    job_dir.mkdir(parents=True, exist_ok=True)
    command = [
        "docker", "run", "--rm", "--network=none", "--read-only",
        "--tmpfs", "/tmp:rw,nosuid,nodev,noexec,size=64m",
        "--cap-drop=ALL", "--security-opt=no-new-privileges",
        "--memory=512m", "--cpus=1", "--pids-limit=128",
        "-v", f"{source.resolve()}:/input/input.docx:ro",
        "-v", f"{job_dir.resolve()}:/work/job:rw",
        IMAGE, "/input/input.docx", "/work/job",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            f"Worker failed for {source.name}: "
            f"{completed.stdout.strip()} {completed.stderr.strip()}"
        )
    return json.loads(completed.stdout.strip().splitlines()[-1])


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def collect(source: Path) -> None:
    name = source.stem
    target = GOLDEN / name
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    result = _run_worker(source, target)
    generated = target / "input.pdf"
    if not generated.is_file():
        raise RuntimeError(f"Worker did not produce PDF for {source.name}")
    rendered = target / "rendered.pdf"
    generated.replace(rendered)

    with fitz.open(rendered) as document:
        pages = []
        dimensions = []
        page_image_sha256 = []
        blank = False
        for index, page in enumerate(document, start=1):
            dimensions.append([
                round(page.rect.width * 25.4 / 72, 2),
                round(page.rect.height * 25.4 / 72, 2),
            ])
            text = _normalize_text(page.get_text("text"))
            pages.append(text)
            is_blank = not text and not page.get_images(full=True) and not page.get_drawings()
            blank = blank or is_blank
            image_path = target / f"page-{index:03d}.png"
            page.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False).save(image_path)
            page_image_sha256.append(_sha256(image_path))

    manifest = {
        "fixture": source.name,
        "input_sha256": _sha256(source),
        "output_pdf_sha256": _sha256(rendered),
        "page_count": len(pages),
        "page_dimensions_mm": dimensions,
        "page_image_sha256": page_image_sha256,
        "normalized_text_by_page": pages,
        "has_blank_pages": blank,
        "worker_result": result,
        "image": IMAGE,
        "image_id": IMAGE_ID,
        "libreoffice_package_version": LO_VERSION,
        "base_image_digest": BASE_DIGEST,
        "security_flags": {
            "network": "none",
            "read_only_root": True,
            "input_mount": "read-only",
            "capabilities_dropped": "ALL",
            "no_new_privileges": True,
            "memory": "512m",
            "cpus": 1,
            "pids_limit": 128,
            "private_tmpfs": "64m",
        },
    }
    (target / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    input_copy = target / "input.docx"
    if input_copy.exists():
        input_copy.unlink()
    profile = target / "lo-profile"
    if profile.exists():
        shutil.rmtree(profile)


if __name__ == "__main__":
    GOLDEN.mkdir(parents=True, exist_ok=True)
    for fixture in sorted(FIXTURES.glob("*.docx")):
        collect(fixture)
        print(f"Captured {fixture.name}")
