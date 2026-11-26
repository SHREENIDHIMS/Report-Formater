# Template schema and rule model

## 1. Core concept

A template is a versioned package containing:
- identity and applicability (university, course, scheme, cohort, report type, branch/optional scope);
- source documents and verification record;
- ordered section definitions;
- page setup and style tokens;
- numbering/caption/reference policies;
- required assets and placeholders;
- machine-checkable rules and advisory rules;
- status and lifecycle dates.

A DOCX sample can be included as an asset, but it is not the only source of truth.

## 2. Template lifecycle

`draft -> research_review -> verified -> published -> deprecated`

A published template version is immutable. Fixing a mistake creates a new version. Existing reports stay pinned to their original version until a user explicitly migrates them.

## 3. Rule types

- `page_setup`: paper size, margins, orientation.
- `style`: font family/size, bold, alignment, paragraph spacing, line spacing.
- `structure`: mandatory section, ordering, allowed count.
- `numbering`: page, heading, figure, table, equation and reference sequence.
- `caption`: pattern and chapter association.
- `content_constraint`: word count or placeholder presence.
- `rendering`: page overflow/blank page/clipping heuristics.
- `advisory`: guidelines that cannot be reliably machine-validated.

Each rule should define `rule_id`, `label`, `category`, `selector`, `expected`, `severity`, `auto_fix`, `source_refs`, `status`, `confidence`, `applicability`, and optional `explanation`.

## 4. Example structure

```yaml
schema_version: 1
id: vtu-be-btech-project-report
version: 0.1.0
status: research-draft
scope:
  university: Visvesvaraya Technological University
  courses: [BE, BTech]
  scheme: null
  academic_cohort: null
  report_type: final_year_project
  branches: [CSE, ISE, ECE, EEE, ME, CV, OTHER]
applicability_note: >-
  Must be confirmed against the student's cohort and the applicable current
  college/department instructions before publishing as a verified template.
page_setup:
  paper: A4
  width_mm: 210
  height_mm: 297
  margins_mm: {left: 31.75, right: 25.4, top: 19.05, bottom: 19.05}
styles:
  body: {font_family: null, font_size_pt: 12, alignment: justify}
```

See `templates/vtu/be-btech-project-report/manifest.yaml` and `rules.yaml` for the full starter version.

## 5. Conflict handling

Resolve rules in explicit precedence order:
1. Applicable university/scheme rule (immutable baseline).
2. User-selected college/department addendum (only when student confirms it applies).
3. Student override (allowed only for noncritical settings or explicit confirmation).

When two authoritative sources conflict, do not silently choose. Show conflict and require student review/clarification. Keep both source references.

## 6. Rule engine behaviour

- Deterministic: same doc version + template version + pipeline version => same result.
- Explainable: every warning/error maps to a rule.
- Idempotent: applying the same rules repeatedly does not compound changes.
- Reversible: a transformation produces a new version with a recorded operation list.
- Conservative: uncertain detection produces warning or manual review, not a destructive guess.
- Version-aware: never update old reports in place when a template is changed.

## 7. Automatic fix safety

Rules should declare one of:
- `safe_auto`: deterministic and content-preserving (e.g. page margin change if section intent is clear).
- `preview_required`: likely safe but can alter pagination/layout (font/spacing/section breaks).
- `manual_only`: ambiguous or semantic (section mapping, citations, title/abstract meaning).
- `no_fix`: informational or not machine-actionable.

Do not auto-fill guide signatures, official seals, approval dates, university registration numbers or results.
