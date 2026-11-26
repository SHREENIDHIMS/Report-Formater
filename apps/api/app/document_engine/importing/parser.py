"""Read-only DOCX inspection and feature inventory.

Uses python-docx for high-level access plus lxml/OOXML for constructs the
high-level API does not expose (floating images, page fields, numbering
resolution, unsupported elements). Nothing here mutates the source package.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from zipfile import ZipFile

from docx import Document
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from lxml import etree

from .models import (
    FeatureEntry,
    HeaderFooterInfo,
    HeadingInfo,
    ImageInfo,
    ImportReport,
    PackageValidationResult,
    ParagraphInfo,
    ParagraphStyleInfo,
    SectionInfo,
    SupportLevel,
    TableInfo,
)
from .package_validation import validate_docx_package

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
OMML = "http://schemas.openxmlformats.org/officeDocument/2006/math"

EMU_PER_MM = 36000.0

_FIELD_NAME_RE = re.compile(r"\b(PAGE|NUMPAGES|SECTION|SECTIONPAGES|DATE|TIME|AUTHOR|TITLE|TOC|CITATION|REF)\b", re.IGNORECASE)


def _tag(local: str) -> str:
    return f"{{{W}}}{local}"


def _safe_text(element: etree._Element | None) -> str:
    if element is None:
        return ""
    return "".join(element.itertext())


def _paragraph_text(p) -> str:
    return "".join(r.text or "" for r in p.runs)


def _paragraph_runs_count(p) -> int:
    return len(p.runs)


def _first_style(p) -> ParagraphStyleInfo:
    style = ParagraphStyleInfo()
    try:
        if p.style is not None:
            style.style_id = p.style.style_id
            style.style_name = p.style.name
            name = (p.style.name or "").lower()
            if name.startswith("heading") or name.startswith("title"):
                style.is_heading = True
                m = re.search(r"(\d+)", name)
                if m:
                    style.heading_level = int(m.group(1))
    except Exception:  # noqa: BLE001 - style access must not break inspection
        pass
    # Fall back to raw pPr/pStyle for custom heading styles not known by name.
    try:
        p_pr = p._p.find(_tag("pPr"))
        if p_pr is not None:
            p_style = p_pr.find(_tag("pStyle"))
            if p_style is not None and p_style.get(qn("w:val")):
                val = p_style.get(qn("w:val"))
                style.style_id = val or style.style_id
                if val and val.lower() in {
                    "heading1", "heading2", "heading3", "heading4", "heading5", "heading6",
                }:
                    style.is_heading = True
                    style.heading_level = int(val.lower().replace("heading", ""))
    except Exception:  # noqa: BLE001
        pass
    return style


def _has_hyperlink(p) -> bool:
    try:
        return p._p.find(f".//{_tag('hyperlink')}") is not None
    except Exception:  # noqa: BLE001
        return False


def _field_types_in_element(element: etree._Element) -> list[str]:
    found: list[str] = []
    try:
        for instr in element.iter(f".//{_tag('instrText')}"):
            text = instr.text or ""
            for m in _FIELD_NAME_RE.finditer(text):
                found.append(m.group(1).upper())
        for fld in element.iter(_tag("fldSimple")):
            instr = fld.get(qn("w:instr")) or ""
            for m in _FIELD_NAME_RE.finditer(instr):
                found.append(m.group(1).upper())
    except Exception:  # noqa: BLE001
        pass
    return sorted(set(found))


def _has_field(p) -> bool:
    try:
        return (
            p._p.find(f".//{_tag('fldChar')}") is not None
            or p._p.find(f".//{_tag('instrText')}") is not None
            or p._p.find(f".//{_tag('fldSimple')}") is not None
        )
    except Exception:  # noqa: BLE001
        return False


@dataclass
class _NumberingContext:
    numbering_root: etree._Element | None = None
    num_id_to_abstract: dict[str, str] = None  # type: ignore[assignment]
    abstract_to_format: dict[str, str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.num_id_to_abstract is None:
            self.num_id_to_abstract = {}
        if self.abstract_to_format is None:
            self.abstract_to_format = {}


def _load_numbering(document: Document) -> _NumberingContext:
    ctx = _NumberingContext()
    try:
        numbering_part = document.part.numbering_part
        if numbering_part is None:
            return ctx
        root = numbering_part.element
        ctx.numbering_root = root
        for num in root.iter(_tag("num")):
            num_id = num.get(qn("w:numId"))
            abst = num.find(_tag("abstractNumId"))
            if num_id is not None and abst is not None and abst.get(qn("w:val")):
                ctx.num_id_to_abstract[num_id] = abst.get(qn("w:val"))
        for abs_num in root.iter(_tag("abstractNum")):
            abs_id = abs_num.get(qn("w:abstractNumId"))
            if abs_id is None:
                continue
            lvl = abs_num.find(_tag("lvl"))
            fmt = "bullet"
            if lvl is not None:
                num_fmt = lvl.find(_tag("numFmt"))
                if num_fmt is not None and num_fmt.get(qn("w:val")):
                    fmt = num_fmt.get(qn("w:val"))
            ctx.abstract_to_format[abs_id] = fmt
    except Exception:  # noqa: BLE001 - numbering is optional
        pass
    return ctx


def _resolve_numbering(p, ctx: _NumberingContext) -> tuple[bool, str | None, int | None, str | None]:
    """Return (has_numbering, num_id, level, format) for a paragraph."""
    try:
        p_pr = p._p.find(_tag("pPr"))
        if p_pr is None:
            return False, None, None, None
        num_id_el = p_pr.find(_tag("numId"))
        ilvl_el = p_pr.find(_tag("ilvl"))
        num_id = num_id_el.get(qn("w:val")) if num_id_el is not None else None
        level = None
        if ilvl_el is not None and ilvl_el.get(qn("w:val")) is not None:
            try:
                level = int(ilvl_el.get(qn("w:val")))
            except (TypeError, ValueError):
                level = None
        fmt = None
        if num_id and ctx.numbering_root is not None:
            abs_id = ctx.num_id_to_abstract.get(num_id)
            if abs_id:
                fmt = ctx.abstract_to_format.get(abs_id)
        return (num_id is not None), num_id, level, fmt
    except Exception:  # noqa: BLE001
        return False, None, None, None


def _is_empty_paragraph(p) -> bool:
    text = _paragraph_text(p).strip()
    if text:
        return False
    try:
        has_any = (
            p._p.find(f".//{_tag('r')}") is not None
            or p._p.find(f".//{_tag('drawing')}") is not None
            or p._p.find(f".//{_tag('pict')}") is not None
        )
    except Exception:  # noqa: BLE001
        has_any = False
    return not has_any


def _collect_paragraphs(document: Document, ctx: _NumberingContext) -> tuple[list[ParagraphInfo], dict[str, Any]]:
    paragraphs: list[ParagraphInfo] = []
    total_runs = 0
    heading_count = 0
    list_paragraphs = 0
    paragraphs_with_hyperlinks = 0
    paragraphs_with_fields = 0
    field_types_found: set[str] = set()
    empty_paragraphs = 0

    for index, p in enumerate(document.paragraphs):
        style = _first_style(p)
        text = _paragraph_text(p)
        run_count = _paragraph_runs_count(p)
        total_runs += run_count
        has_hyperlink = _has_hyperlink(p)
        field_types = _field_types_in_element(p._p)
        has_field = bool(field_types)
        has_numbering, num_id, num_level, num_fmt = _resolve_numbering(p, ctx)

        info = ParagraphInfo(
            index=index,
            style=style,
            text=text,
            text_length=len(text),
            run_count=run_count,
            alignment=str(p.alignment) if p.alignment is not None else None,
            has_hyperlink=has_hyperlink,
            has_field=has_field,
            field_types=field_types,
            has_numbering=has_numbering,
            num_id=num_id,
            num_level=num_level,
            num_format=num_fmt,
            is_empty=_is_empty_paragraph(p),
        )
        paragraphs.append(info)

        if style.is_heading:
            heading_count += 1
        if has_numbering:
            list_paragraphs += 1
        if has_hyperlink:
            paragraphs_with_hyperlinks += 1
        if has_field:
            paragraphs_with_fields += 1
            field_types_found.update(field_types)
        if info.is_empty:
            empty_paragraphs += 1

    summary = {
        "total_paragraphs": len(paragraphs),
        "body_paragraphs": len(paragraphs) - heading_count - list_paragraphs,
        "heading_count": heading_count,
        "list_paragraphs": list_paragraphs,
        "paragraphs_with_hyperlinks": paragraphs_with_hyperlinks,
        "paragraphs_with_fields": paragraphs_with_fields,
        "field_types_found": sorted(field_types_found),
        "empty_paragraphs": empty_paragraphs,
        "total_runs": total_runs,
    }
    return paragraphs, summary


def _collect_headings(paragraphs: list[ParagraphInfo]) -> list[HeadingInfo]:
    headings: list[HeadingInfo] = []
    stack: list[tuple[int, int]] = []  # (level, index) for hierarchy
    for p in paragraphs:
        if not p.style.is_heading or p.style.heading_level is None:
            continue
        level = p.style.heading_level
        while stack and stack[-1][0] >= level:
            stack.pop()
        headings.append(
            HeadingInfo(
                index=p.index,
                level=level,
                style_id=p.style.style_id,
                style_name=p.style.style_name,
                text=p.text,
                text_length=p.text_length,
            )
        )
        stack.append((level, p.index))
    return headings


def _collect_tables(document: Document) -> list[TableInfo]:
    tables: list[TableInfo] = []
    try:
        all_tables = document.element.iter(_tag("tbl"))
    except Exception:  # noqa: BLE001
        return tables

    for index, tbl in enumerate(all_tables):
        rows = tbl.findall(_tag("tr"))
        grid_col_count = 0
        grid = tbl.find(_tag("tblGrid"))
        if grid is not None:
            grid_col_count = len(grid.findall(_tag("gridCol")))
        cell_count = 0
        has_merged = False
        is_nested = False
        has_borders = False
        for row in rows:
            for tc in row.findall(_tag("tc")):
                cell_count += 1
                grid_span = tc.find(_tag("gridSpan"))
                if grid_span is not None:
                    try:
                        val = int(grid_span.get(qn("w:val")) or "1")
                        if val > 1:
                            has_merged = True
                    except (TypeError, ValueError):
                        has_merged = True
                if tc.find(_tag("vMerge")) is not None:
                    has_merged = True
                if tc.find(f".//{_tag('tbl')}") is not None:
                    is_nested = True
        if tbl.find(_tag("tblBorders")) is not None:
            has_borders = True
        tables.append(
            TableInfo(
                index=index,
                row_count=len(rows),
                col_count=grid_col_count,
                cell_count=cell_count,
                has_merged_cells=has_merged,
                is_nested=is_nested,
                has_borders=has_borders,
            )
        )
    return tables


def _content_type_for_target(zf: ZipFile, target: str) -> str | None:
    """Best-effort MIME type for a media target from [Content_Types].xml."""
    try:
        with zf.open("[Content_Types].xml") as fh:
            root = etree.parse(fh).getroot()
        ct_ns = "http://schemas.openxmlformats.org/package/2006/content-types"
        for override in root.iter(f"{{{ct_ns}}}Override"):
            if override.get("PartName") == "/" + target:
                return override.get("ContentType")
        ext = target.rsplit(".", 1)[-1].lower() if "." in target else ""
        for default in root.iter(f"{{{ct_ns}}}Default"):
            if default.get("Extension") == ext:
                return default.get("ContentType")
    except Exception:  # noqa: BLE001
        pass
    return None


def _relationship_target(document: Document, rid: str) -> str | None:
    try:
        return document.part.rels[rid].target  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        return None


def _collect_images(document: Document, zf: ZipFile) -> list[ImageInfo]:
    images: list[ImageInfo] = []
    try:
        body = document.element.body
    except Exception:  # noqa: BLE001
        return images

    for index, drawing in enumerate(body.iter(f".//{_tag('drawing')}")):
        anchor = drawing.find(f".//{{{WP}}}anchor")
        inline = drawing.find(f".//{{{WP}}}inline")
        if anchor is not None:
            extent = anchor.find(f".//{{{WP}}}extent")
            anchor_type = "anchor"
            is_inline, is_floating = False, True
        elif inline is not None:
            extent = inline.find(f".//{{{WP}}}extent")
            anchor_type = "inline"
            is_inline, is_floating = True, False
        else:
            extent = None
            anchor_type = "drawing"
            is_inline = is_floating = False

        width_emu = height_emu = None
        if extent is not None:
            cx = extent.get(qn("w:cx"))
            cy = extent.get(qn("w:cy"))
            if cx is not None:
                try:
                    width_emu = int(cx)
                except (TypeError, ValueError):
                    width_emu = None
            if cy is not None:
                try:
                    height_emu = int(cy)
                except (TypeError, ValueError):
                    height_emu = None

        rid = None
        for blip in drawing.iter(f".//{{{A}}}blip"):
            rid = blip.get(qn("r:embed")) or blip.get(qn("r:link"))
            break

        content_type = None
        rel_target = None
        if rid is not None:
            rel_target = _relationship_target(document, rid)
            if rel_target:
                content_type = _content_type_for_target(zf, rel_target.lstrip("/"))

        images.append(
            ImageInfo(
                index=index,
                relationship_id=rid,
                content_type=content_type,
                width_emu=width_emu,
                height_emu=height_emu,
                is_inline=is_inline,
                is_floating=is_floating,
                anchor_type=anchor_type,
            )
        )
    return images


def _emu_to_mm(emu: int | None) -> float | None:
    if emu is None:
        return None
    return round(emu / EMU_PER_MM, 2)


def _twips_to_mm(twips: int | None) -> float | None:
    if twips is None:
        return None
    return round(twips * 635.0 / EMU_PER_MM, 2)


def _collect_sections(document: Document) -> list[SectionInfo]:
    from docx.enum.section import WD_SECTION as WD_SCT
    sections: list[SectionInfo] = []
    for index, section in enumerate(document.sections):
        try:
            width_emu = int(section.page_width) if section.page_width is not None else None
            height_emu = int(section.page_height) if section.page_height is not None else None

            # Determine orientation from page dimensions
            if width_emu is not None and height_emu is not None:
                orientation = "landscape" if width_emu > height_emu else "portrait"
            else:
                orient_enum = section.orientation
                orientation = orient_enum.name.lower() if orient_enum else "portrait"

            # Determine section type from start_type enum
            start_type_enum = section.start_type
            if start_type_enum is not None:
                type_name = start_type_enum.name  # e.g. "NEW_PAGE"
            else:
                type_name = "nextPage"

            # Map WD_SECTION start type names to SectionInfo type values
            type_map = {
                "NEW_PAGE": "nextPage",
                "CONTINUOUS": "continuous",
                "EVEN_PAGE": "evenPage",
                "ODD_PAGE": "oddPage",
            }
            section_type = type_map.get(type_name, "nextPage")

            info = SectionInfo(
                index=index,
                type=section_type,
                orientation=orientation,
                page_width_emu=width_emu,
                page_height_emu=height_emu,
                page_width_mm=_emu_to_mm(width_emu),
                page_height_mm=_emu_to_mm(height_emu),
                margin_top_twips=int(section.top_margin) if section.top_margin is not None else None,
                margin_bottom_twips=int(section.bottom_margin) if section.bottom_margin is not None else None,
                margin_left_twips=int(section.left_margin) if section.left_margin is not None else None,
                margin_right_twips=int(section.right_margin) if section.right_margin is not None else None,
                margin_top_mm=_twips_to_mm(int(section.top_margin)) if section.top_margin is not None else None,
                margin_bottom_mm=_twips_to_mm(int(section.bottom_margin)) if section.bottom_margin is not None else None,
                margin_left_mm=_twips_to_mm(int(section.left_margin)) if section.left_margin is not None else None,
                margin_right_mm=_twips_to_mm(int(section.right_margin)) if section.right_margin is not None else None,
                title_pg=bool(section.different_first_page_header_footer),
            )
            for attr, field in (
                ("header", "header_reference"),
                ("footer", "footer_reference"),
                ("first_page_header", "first_page_header_reference"),
                ("first_page_footer", "first_page_footer_reference"),
            ):
                try:
                    hf = getattr(section, attr, None)
                    if hf is not None and hf._header is not None:
                        ref = getattr(hf._header, "rId", None) or str(id(hf._header))
                        setattr(info, field, ref)
                except Exception:  # noqa: BLE001
                    pass
            sections.append(info)
        except Exception:  # noqa: BLE001 - one bad section must not abort inspection
            sections.append(SectionInfo(index=index, type="unknown", orientation="unknown"))
    return sections


def _collect_headers_footers(document: Document) -> list[HeaderFooterInfo]:
    results: list[HeaderFooterInfo] = []
    type_order = [
        ("default", "header"),
        ("default", "footer"),
        ("firstPage", "first_page_header"),
        ("firstPage", "first_page_footer"),
        ("evenPage", "even_page_header"),
        ("evenPage", "even_page_footer"),
    ]
    for hf_type, attr in type_order:
        for section_index, section in enumerate(document.sections):
            try:
                hf = getattr(section, attr, None)
                if hf is None:
                    continue
                if getattr(hf, "is_linked_to_previous", False):
                    continue
                paragraphs = list(hf.paragraphs)
                text = "\n".join(_paragraph_text(p) for p in paragraphs).strip()
                page_field_types: list[str] = []
                has_page_field = False
                for p in paragraphs:
                    types = _field_types_in_element(p._p)
                    if types:
                        has_page_field = True
                        page_field_types.extend(types)
                part_target = None
                try:
                    hf_el = hf._header
                    rel_id = getattr(hf_el, "rId", None)
                    if rel_id:
                        part_target = _relationship_target(document, rel_id)
                except Exception:  # noqa: BLE001
                    part_target = None
                results.append(
                    HeaderFooterInfo(
                        type=hf_type,
                        part_target=part_target,
                        paragraph_count=len(paragraphs),
                        has_page_field=has_page_field,
                        page_field_types=sorted(set(page_field_types)),
                        text=text,
                        text_length=len(text),
                    )
                )
            except Exception:  # noqa: BLE001
                continue
    return results


def _detect_unsupported_elements(document: Document) -> tuple[list[str], list[str]]:
    """Scan raw OOXML for constructs python-docx does not fully support.

    Returns (unsupported_element_types, warnings).
    """
    found: set[str] = set()
    warnings: list[str] = []

    def scan(element: etree._Element, source: str) -> None:
        local_names = {etree.QName(e).localname for e in element.iter()}
        namespaces = {etree.QName(e).namespace for e in element.iter() if etree.QName(e).namespace}
        if _tag("commentRangeStart") in local_names or _tag("commentReference") in local_names:
            found.add("comments")
        if _tag("insert") in local_names or _tag("delete") in local_names:
            found.add("tracked_changes")
        if _tag("moveFrom") in local_names or _tag("moveTo") in local_names:
            found.add("moved_text")
        if _tag("txbxContent") in local_names:
            found.add("text_boxes")
        if _tag("sdt") in local_names:
            found.add("content_controls")
        if _tag("footnoteReference") in local_names:
            found.add("footnotes")
        if _tag("endnoteReference") in local_names:
            found.add("endnotes")
        if OMML in namespaces or _tag("oMath") in local_names:
            found.add("equations_omml")
        if _tag("pict") in local_names:
            found.add("legacy_pictures_pict")
        if _tag("embeddedObj") in local_names or _tag("link") in local_names or _tag("ooxml") in local_names:
            found.add("embedded_objects")
        if _tag("hyperlink") in local_names:
            found.add("hyperlinks")
        if _tag("bookmarkStart") in local_names or _tag("bookmarkEnd") in local_names:
            found.add("bookmarks")
        if _tag("fldSimple") in local_names or _tag("instrText") in local_names:
            found.add("fields")

    try:
        scan(document.element.body, "document.xml")
    except Exception:  # noqa: BLE001
        warnings.append("could not scan document.xml for unsupported elements")

    for section in document.sections:
        for attr in (
            "header", "footer", "first_page_header", "first_page_footer",
            "even_page_header", "even_page_footer",
        ):
            hf = getattr(section, attr, None)
            if hf is None:
                continue
            try:
                scan(hf._header.element, f"header/footer part ({attr})")
            except Exception:  # noqa: BLE001
                continue

    return sorted(found), warnings


def _classify_features(
    *,
    paragraphs: list[ParagraphInfo],
    headings: list[HeadingInfo],
    tables: list[TableInfo],
    images: list[ImageInfo],
    sections: list[SectionInfo],
    headers_footers: list[HeaderFooterInfo],
    unsupported: list[str],
) -> list[FeatureEntry]:
    features: list[FeatureEntry] = []

    features.append(
        FeatureEntry(
            feature="body paragraphs",
            count=len(paragraphs),
            support=SupportLevel.SUPPORTED,
            locations=[f"paragraph {p.index}" for p in paragraphs[:5]],
        )
    )
    features.append(
        FeatureEntry(
            feature="headings / heading hierarchy",
            count=len(headings),
            support=SupportLevel.SUPPORTED if headings else SupportLevel.PRESERVED_NOT_EDITABLE,
            notes="Detected via paragraph style (Heading N); custom heading styles resolved from pPr/pStyle.",
            locations=[f"level {h.level} at paragraph {h.index}" for h in headings[:10]],
        )
    )
    features.append(
        FeatureEntry(
            feature="lists / numbering",
            count=sum(1 for p in paragraphs if p.has_numbering),
            support=SupportLevel.SUPPORTED,
            notes="numId/ilvl resolved against word/numbering.xml; format (decimal/bullet) inferred.",
            locations=[f"paragraph {p.index}" for p in paragraphs if p.has_numbering][:10],
        )
    )
    features.append(
        FeatureEntry(
            feature="tables",
            count=len(tables),
            support=SupportLevel.SUPPORTED,
            notes="Simple tables supported; merged cells and nested tables preserved but flagged for review.",
            locations=[f"table {t.index}" for t in tables],
        )
    )
    if any(t.has_merged_cells for t in tables):
        features.append(
            FeatureEntry(
                feature="merged table cells",
                count=sum(1 for t in tables if t.has_merged_cells),
                support=SupportLevel.WARN_LIMITED,
                notes="Preserved; editing support limited until the IR table model handles merges.",
            )
        )
    if any(t.is_nested for t in tables):
        features.append(
            FeatureEntry(
                feature="nested tables",
                count=sum(1 for t in tables if t.is_nested),
                support=SupportLevel.WARN_LIMITED,
                notes="Preserved; nested tables may not map cleanly to the Document IR.",
            )
        )
    features.append(
        FeatureEntry(
            feature="inline images",
            count=sum(1 for i in images if i.is_inline),
            support=SupportLevel.SUPPORTED,
            notes="Relationship target and media content type resolved where possible.",
            locations=[f"image {i.index}" for i in images if i.is_inline][:10],
        )
    )
    floating = [i for i in images if i.is_floating]
    if floating:
        features.append(
            FeatureEntry(
                feature="floating / anchored images",
                count=len(floating),
                support=SupportLevel.PRESERVED_NOT_EDITABLE,
                notes="Detected via wp:anchor; preserved as OOXML, not editable through the IR.",
                locations=[f"image {i.index}" for i in floating][:10],
            )
        )
    features.append(
        FeatureEntry(
            feature="sections / page setup",
            count=len(sections),
            support=SupportLevel.SUPPORTED,
            notes="Page size, orientation and margins read from sectPr; single-section docs are simplest to reformat.",
            locations=[f"section {s.index}" for s in sections],
        )
    )
    if len(sections) > 1:
        features.append(
            FeatureEntry(
                feature="multiple sections / section breaks",
                count=len(sections),
                support=SupportLevel.WARN_LIMITED,
                notes="Multiple orientations/margins supported for inspection; automatic re-layout across sections requires manual review.",
                locations=[f"section {s.index} ({s.type})" for s in sections],
            )
        )
    hf_with_fields = [h for h in headers_footers if h.has_page_field]
    features.append(
        FeatureEntry(
            feature="headers and footers",
            count=len(headers_footers),
            support=SupportLevel.SUPPORTED,
            notes="Paragraphs and page fields detected; linked-to-previous footers skipped to avoid duplicates.",
            locations=[f"{h.type}" for h in headers_footers],
        )
    )
    if hf_with_fields:
        features.append(
            FeatureEntry(
                feature="page-number fields (PAGE / NUMPAGES)",
                count=len(hf_with_fields),
                support=SupportLevel.PRESERVED_NOT_EDITABLE,
                notes="Detected but not recomputed; pagination may shift after transformation.",
                locations=[f"{h.type}: {', '.join(h.page_field_types)}" for h in hf_with_fields],
            )
        )
    features.append(
        FeatureEntry(
            feature="hyperlinks",
            count=sum(1 for p in paragraphs if p.has_hyperlink),
            support=SupportLevel.SUPPORTED,
            notes="Preserved; external targets validated during package scanning.",
            locations=[f"paragraph {p.index}" for p in paragraphs if p.has_hyperlink][:10],
        )
    )

    for element_type in unsupported:
        support = SupportLevel.PRESERVED_NOT_EDITABLE
        notes = "Detected in raw OOXML; preserved only if the package is copied unchanged."
        if element_type in {"embedded_objects", "legacy_pictures_pict"}:
            support = SupportLevel.UNSUPPORTED
            notes = "May block transformation; student must provide a clean supported version."
        elif element_type in {"comments", "tracked_changes", "moved_text", "content_controls"}:
            support = SupportLevel.WARN_LIMITED
            notes = "Review-only; not part of the editable IR."
        features.append(
            FeatureEntry(
                feature=element_type,
                count=1,
                support=support,
                notes=notes,
            )
        )

    return features


def inspect_docx(path: str | Path) -> ImportReport:
    """Inspect a DOCX file and produce a read-only feature inventory.

    The source package is never mutated. Returns an :class:`ImportReport`
    classifying every detected construct. When package validation fails, the
    report is returned with ``parsed_ok=False`` and parsing is skipped.
    """
    path = Path(path)
    report = ImportReport(source_file=str(path))

    # 1. Package safety validation (read-only).
    package_validation = validate_docx_package(path)
    report.package_validation = package_validation
    report.file_size_bytes = package_validation.file_size_bytes
    if not package_validation.valid:
        report.warnings.extend(package_validation.errors)
        return report
    report.warnings.extend(package_validation.warnings)

    # 2. Open with python-docx.
    try:
        document = Document(str(path))
    except Exception as exc:  # noqa: BLE001 - corrupt / non-OOXML
        report.warnings.append(f"failed to open DOCX with python-docx: {exc}")
        return report

    report.parsed_ok = True

    # 3. Paragraphs, runs, headings, numbering.
    numbering_ctx = _load_numbering(document)
    paragraphs, summary = _collect_paragraphs(document, numbering_ctx)
    report.paragraphs = paragraphs
    report.paragraph_summary = summary
    report.total_paragraphs = summary.get("total_paragraphs", 0)
    report.total_runs = summary.get("total_runs", 0)
    report.headings = _collect_headings(paragraphs)

    # 4. Tables.
    report.tables = _collect_tables(document)
    report.total_tables = len(report.tables)

    # 5. Images (inline + floating).
    try:
        with ZipFile(str(path), "r") as zf:
            report.images = _collect_images(document, zf)
    except Exception as exc:  # noqa: BLE001
        report.warnings.append(f"could not inspect images: {exc}")
        report.images = []
    report.total_images = len(report.images)

    # 6. Sections / page setup.
    report.sections = _collect_sections(document)
    report.total_sections = len(report.sections)

    # 7. Headers / footers / page fields.
    report.headers_footers = _collect_headers_footers(document)

    # 8. Unsupported / complex elements (raw OOXML scan).
    unsupported, extra_warnings = _detect_unsupported_elements(document)
    report.unsupported_elements = unsupported
    report.warnings.extend(extra_warnings)

    # 9. Feature classification.
    report.features = _classify_features(
        paragraphs=paragraphs,
        headings=report.headings,
        tables=report.tables,
        images=report.images,
        sections=report.sections,
        headers_footers=report.headers_footers,
        unsupported=unsupported,
    )

    # 10. Roll up human-readable warnings.
    if report.unsupported_elements:
        report.warnings.append(
            "Unsupported/complex elements detected: "
            + ", ".join(report.unsupported_elements)
            + ". These will be preserved or flagged before any transformation."
        )
    if report.total_sections > 1:
        report.warnings.append(
            "Multiple sections detected; page setup varies across the document. Review before applying a single template."
        )
    if any(i.is_floating for i in report.images):
        report.warnings.append(
            "Floating/anchored images are preserved but not editable through the structured editor."
        )
    if any(t.is_nested or t.has_merged_cells for t in report.tables):
        report.warnings.append(
            "Tables with merges or nesting are preserved but have limited edit support."
        )

    return report
