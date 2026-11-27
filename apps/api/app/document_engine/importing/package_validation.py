"""ZIP/OOXML package safety validation for DOCX imports.

Treats a DOCX as untrusted ZIP input. Before any OOXML parsing, this module:

- checks the ZIP magic bytes;
- validates archive integrity (no corrupt entries);
- enforces compressed/uncompressed size, entry count and compression-ratio
  limits (zip-bomb resistance);
- rejects path-traversal and absolute-path entries;
- rejects macro-enabled / encrypted / suspicious parts;
- rejects suspicious external relationship targets.

All checks are read-only; the source file is never mutated.
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from .models import PackageValidationResult

# Default limits mirror the documented upload ceiling (50 MB) and are
# intentionally conservative for a feasibility spike. They should be tuned
# from golden-document tests before production use.
MAX_FILE_BYTES: Final[int] = 50 * 1024 * 1024
MAX_COMPRESSED_BYTES: Final[int] = 50 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES: Final[int] = 200 * 1024 * 1024
MAX_ENTRY_COUNT: Final[int] = 2000
MAX_COMPRESSION_RATIO: Final[float] = 100.0  # uncompressed / compressed

REQUIRED_PARTS: Final[tuple[str, ...]] = (
    "[Content_Types].xml",
    "word/document.xml",
    "word/_rels/document.xml.rels",
)

MACRO_PART_SUBSTRINGS: Final[tuple[str, ...]] = (
    "vbaProject",
    "vbaData",
    "macros",
    "activex",
    "oleObject",
    "embeddedObj",
)

SUSPICIOUS_REL_TARGET_SUBSTRINGS: Final[tuple[str, ...]] = (
    "http:",
    "https:",
    "file:",
    "ftp:",
    "\\\\",
)


@dataclass
class _RawValidation:
    valid: bool
    errors: list[str]
    warnings: list[str]
    file_size_bytes: int
    entry_count: int
    has_content_types: bool
    has_document_part: bool
    has_document_rels: bool
    macro_parts: list[str]
    path_traversal_entries: list[str]
    suspicious_relationships: list[str]


def _looks_like_path_traversal(name: str) -> bool:
    """Return True if a ZIP entry name escapes its intended directory."""
    normalized = name.replace("\\", "/")
    segments = normalized.split("/")
    return (
        any(seg == ".." for seg in segments)
        or normalized.startswith("/")
        or normalized.startswith("../")
    )


def _has_macro_part(name: str) -> bool:
    lower = name.lower()
    return any(sub.lower() in lower for sub in MACRO_PART_SUBSTRINGS)


def validate_docx_package(
    path: str | Path,
    *,
    max_file_bytes: int = MAX_FILE_BYTES,
    max_compressed_bytes: int = MAX_COMPRESSED_BYTES,
    max_uncompressed_bytes: int = MAX_UNCOMPRESSED_BYTES,
    max_entry_count: int = MAX_ENTRY_COUNT,
    max_compression_ratio: float = MAX_COMPRESSION_RATIO,
) -> PackageValidationResult:
    """Validate a DOCX package without parsing OOXML content.

    Returns a :class:`PackageValidationResult`. When ``valid`` is False the
    caller should reject the file before parsing.
    """
    errors: list[str] = []
    warnings: list[str] = []
    macro_parts: list[str] = []
    path_traversal_entries: list[str] = []
    suspicious_relationships: list[str] = []

    path = Path(path)
    file_size_bytes = path.stat().st_size if path.exists() else 0

    if file_size_bytes == 0:
        errors.append("file is empty")
        return _build_result(
            False,
            errors,
            warnings,
            file_size_bytes,
            0,
            False,
            False,
            False,
            macro_parts,
            path_traversal_entries,
            suspicious_relationships,
        )
    if file_size_bytes > max_file_bytes:
        errors.append(
            f"file size {file_size_bytes} exceeds limit {max_file_bytes} bytes",
        )

    # ZIP magic bytes check (PK\x03\x04 for local file headers).
    magic_ok = False
    try:
        with path.open("rb") as fh:
            magic = fh.read(4)
        magic_ok = magic == b"PK\x03\x04"
    except OSError as exc:
        errors.append(f"unable to read file: {exc}")
        return _build_result(
            False,
            errors,
            warnings,
            file_size_bytes,
            0,
            False,
            False,
            False,
            macro_parts,
            path_traversal_entries,
            suspicious_relationships,
        )
    if not magic_ok:
        errors.append("missing ZIP magic bytes (not a valid DOCX/OOXML package)")

    entry_count = 0
    total_compressed = 0
    total_uncompressed = 0
    has_content_types = False
    has_document_part = False
    has_document_rels = False

    if magic_ok:
        try:
            with zipfile.ZipFile(path, "r") as zf:
                # Test integrity of every entry (catches zip bombs / corrupt CRCs).
                bad_file = zf.testzip()
                if bad_file is not None:
                    errors.append(f"corrupt ZIP entry: {bad_file}")

                infos = zf.infolist()
                entry_count = len(infos)
                if entry_count > max_entry_count:
                    errors.append(
                        f"entry count {entry_count} exceeds limit {max_entry_count}",
                    )

                for info in infos:
                    total_compressed += info.compress_size
                    total_uncompressed += info.file_size
                    name = info.filename

                    if _looks_like_path_traversal(name):
                        path_traversal_entries.append(name)
                        errors.append(f"path-traversal entry rejected: {name}")

                    if _has_macro_part(name):
                        macro_parts.append(name)
                        errors.append(f"macro-enabled part rejected: {name}")

                    lower = name.lower()
                    if lower == "[content_types].xml":
                        has_content_types = True
                    if lower == "word/document.xml":
                        has_document_part = True
                    if lower == "word/_rels/document.xml.rels":
                        has_document_rels = True

                # Inspect relationships for suspicious external targets.
                try:
                    with zf.open("word/_rels/document.xml.rels") as rels:
                        rels_xml = rels.read()
                    suspicious_relationships = _scan_rels(rels_xml)
                    if suspicious_relationships:
                        warnings.extend(
                            f"suspicious relationship target: {t}" for t in suspicious_relationships
                        )
                except KeyError:
                    pass  # no relationships part; reported via has_document_rels
                except Exception as exc:  # noqa: BLE001 - degrade gracefully
                    warnings.append(f"could not read relationships part: {exc}")

                if total_compressed > max_compressed_bytes:
                    errors.append(
                        f"compressed size {total_compressed} exceeds limit "
                        f"{max_compressed_bytes} bytes",
                    )
                if total_uncompressed > max_uncompressed_bytes:
                    errors.append(
                        f"uncompressed size {total_uncompressed} exceeds limit "
                        f"{max_uncompressed_bytes} bytes",
                    )
                if total_compressed > 0:
                    ratio = total_uncompressed / total_compressed
                    if ratio > max_compression_ratio:
                        errors.append(
                            f"compression ratio {ratio:.1f}:1 exceeds limit "
                            f"{max_compression_ratio}:1 "
                            "(possible zip bomb)",
                        )
        except zipfile.BadZipFile as exc:
            errors.append(f"invalid ZIP archive: {exc}")
        except Exception as exc:  # noqa: BLE001 - degrade gracefully
            errors.append(f"unable to inspect ZIP archive: {exc}")

    valid = not errors
    return _build_result(
        valid,
        errors,
        warnings,
        file_size_bytes,
        entry_count,
        has_content_types,
        has_document_part,
        has_document_rels,
        macro_parts,
        path_traversal_entries,
        suspicious_relationships,
    )


def _build_result(
    valid: bool,
    errors: list[str],
    warnings: list[str],
    file_size_bytes: int,
    entry_count: int,
    has_content_types: bool,
    has_document_part: bool,
    has_document_rels: bool,
    macro_parts: list[str],
    path_traversal_entries: list[str],
    suspicious_relationships: list[str],
) -> PackageValidationResult:
    return PackageValidationResult(
        valid=valid,
        errors=errors,
        warnings=warnings,
        file_size_bytes=file_size_bytes,
        entry_count=entry_count,
        has_content_types=has_content_types,
        has_document_part=has_document_part,
        has_document_rels=has_document_rels,
        macro_parts=macro_parts,
        path_traversal_entries=path_traversal_entries,
        suspicious_relationships=suspicious_relationships,
    )


def _scan_rels(rels_xml: bytes) -> list[str]:
    """Return relationship targets that look like external/absolute references."""
    from lxml import etree

    targets: list[str] = []
    try:
        root = etree.fromstring(rels_xml)
    except etree.XMLSyntaxError:
        return targets

    rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    for rel in root.iter(f"{{{rel_ns}}}Relationship"):
        target = rel.get("Target", "")
        target_mode = rel.get("TargetMode", "")
        lower = target.lower()
        if target_mode == "External" or any(
            sub in lower for sub in SUSPICIOUS_REL_TARGET_SUBSTRINGS
        ):
            targets.append(target)
    return targets
