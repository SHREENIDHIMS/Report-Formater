# Product Brief — VTU Report Studio

**Working name:** VTU Report Studio  
**Category:** Student-facing academic document formatting SaaS  
**Initial market:** VTU-affiliated B.E./B.Tech. students preparing project reports  
**Business model:** Pay per report/project; test time-limited project passes after launch  
**Status:** Product proposal / implementation starter, 25 November 2026

## One-sentence description

A web application where a VTU student can create a project report, upload an existing DOCX, or combine both workflows; select a versioned VTU report format; automatically format and validate the document; edit it in a guided browser experience; and export editable DOCX plus PDF.

## Problem

Students often spend hours manually adjusting page margins, fonts, paragraph spacing, front matter, heading hierarchy, chapter and figure numbering, table of contents, captions, page breaks, references and appendices. A document can be technically complete while its layout differs from the applicable university or college instructions. Repeated corrections consume student and supervisor time.

## Solution

Build a reliable formatting and document quality platform with three modes:

1. **Automatic** — import an existing supported DOCX, inspect it, apply selected formatting rules, and produce a proposed corrected version.
2. **Manual** — create a report using structured sections and a controlled editor with the selected template applied from the start.
3. **Hybrid** — import an existing document, automatically apply rules, then review and edit content/sections in the editor.

The core should be deterministic document engineering. Optional AI assistance can be considered later for organizing student-provided material, but must never invent technical facts, experiments, results, references or signatures.

## Product promise

“Your project. Your VTU format. Less time fixing Word.”

Avoid absolute promises such as “100% VTU approved” or “guaranteed acceptance”. State the exact template/version and what was checked.

## Customer and buyer

- Primary user and buyer: an individual student.
- Project teams: one shared report purchase/entitlement can cover a single team report, with invited collaborators as an optional paid tier or included seats.
- Colleges and faculty: not required for initial adoption. A student may upload a department-issued instruction sheet or select an available custom ruleset without any formal relationship.

## Differentiation

1. Import-and-correct focus, not only blank report generation.
2. Transparent validation with rule-by-rule findings and source provenance.
3. Editable DOCX and a rendered PDF, both checked after transformation.
4. Three workflows and a browser-based, page-oriented editing experience.
5. Versioned template rules for scheme/cohort and user-provided college addenda.
6. Source preservation and explicit warnings for unsupported Word features.

## First release scope

- VTU B.E./B.Tech. project report only.
- One carefully validated baseline template with configurable scheme/cohort and college-specific overrides.
- Student auth, dashboard, report workspace and autosave.
- Manual authoring using a structured section model.
- DOCX upload and an import-feasibility-supported subset.
- Automatic/hybrid transformation with preview and a change report.
- Basic formatting validator.
- DOCX/PDF export and one-time payment/entitlement.

## Success metric

Primary: percentage of imported documents that can be transformed and exported without loss of supported content, with no critical layout regression in golden-document tests.

Business: paid conversion from preview, report completion/export rate, repeat/referral purchase and refund rate.

Student outcome: fewer formatting-related corrections reported by pilot users. Do not equate the product's formatting score with academic evaluation or acceptance.
