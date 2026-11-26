# VTU Guideline Baseline — Research Draft

**Status:** `research-draft` — not an official product certification.  
**Checked:** 25 November 2026.  
**Target:** VTU B.E./B.Tech. final-year project report.  
**Critical caveat:** confirm the selected student's scheme/cohort and any applicable college/department circular before publishing or applying a template.

## 1. Sources inspected

1. VTU official Examination Guidelines page, which includes the B.E./B.Tech. project report preparation instructions.
2. VTU-hosted *Guidelines for the final year project work* PDF, available from the official VTU site under a November 2025 upload path. The PDF contains suggested report flow and references the project-report preparation guidelines.
3. VTU B.E./B.Tech. scheme page, which lists multiple schemes (including 2022 and 2025 material) and links final-year project work guidance for the 2022 scheme.

Exact URLs and access notes are in `docs/18-research-sources.md`.

## 2. Suggested report sequence

The VTU-hosted project-work guidance presents a suggested report flow broadly comprising:
1. Cover page.
2. Inside title page.
3. Certificate signed by project guide/supervisor, with the applicable institutional process.
4. Student declaration.
5. Acknowledgements.
6. Abstract.
7. Table of contents.
8. List of figures.
9. List of tables.
10. Abbreviations/nomenclature, where used.
11. Main report chapters.
12. References.
13. Appendices.
14. Supplementary/non-paper material, where applicable.

Treat this as a suggested baseline and verify exact required ordering/wording against the current scheme and local instructions.

## 3. Formatting baseline transcribed from VTU B.E./B.Tech. report guidance

| Item | Baseline in source | Product interpretation |
|---|---|---|
| Paper | A4 (210 × 297 mm) | Set A4 page size |
| Printing | Single-sided print is stated | Information/warning for print prep |
| Left margin | 1.25 inches | 31.75 mm |
| Right margin | 1 inch | 25.4 mm |
| Top margin | 0.75 inch | 19.05 mm |
| Bottom margin | 0.75 inch | 19.05 mm |
| Line spacing | 1.5 or double | Template choice; verify local preference |
| Chapter label | 16 pt is stated | Exact alignment wording needs interpretation/confirmation |
| Chapter title | 18 pt, centered | Apply to chapter title paragraph |
| Section heading | 16 pt, left | Apply to level-1 heading |
| Subsection heading | 14 pt, left | Apply to level-2 heading |
| Main text | 12 pt, justified | Apply to body paragraphs |
| Abstract | Maximum 100 words is stated | Count words and warn/block per selected template |
| Preliminary pages | Usually Roman numerals | Mark as “usually”; verify exact page where numbering begins |
| Main chapters | Arabic numerals | Start numbering per selected cover/front-matter convention |
| Headings | Decimal numbering style | Example 1, 1.1, 1.1.1 where applicable |
| Figures/tables | Chapter-wise numbering | Example Figure 2.1, Table 3.1 |
| References | Number in order of appearance; square-bracket references | Basic numbering/citation checks |
| Units | SI units | Advisory check only; semantic unit validation is difficult |
| Equations | Decimal numbering, aligned to right in described format | Structural check only where equation is recognized |
| Final chapter | Summary/contributions/future work are described | Configurable chapter structure |

### Important typography note

The cited formatting passage specifies sizes and alignments but does **not** establish one universal font family. Therefore `font_family` is intentionally `null` in `rules.yaml`. Do not automatically set Times New Roman (or any other family) and call it an official VTU rule unless a verified applicable source/college addendum says so.

### Ambiguous details to verify

- Exact chapter label placement/alignment wording in the guideline.
- Whether the student’s scheme/cohort applies to the 2022 project-work guidance or another instruction.
- Exact title-page/cover text, front-matter numbering start page, certificate text and signature layout.
- Whether the local college has a different font family, spacing, binding, hard-copy or submission rule.
- Any current amendments after the date of the inspected source.

## 4. Rule provenance requirements

Each rule in the machine-readable file should include:
- source title and canonical URL;
- section/page or passage reference;
- date last checked;
- scheme applicability;
- status: `verified_source_fact`, `needs_cohort_verification`, `college_override`, `product_default`;
- whether it can be automatically validated;
- severity and confidence.

Do not remove this provenance in the UI. Show the source and template version when a student inspects a rule.

## 5. Template publishing policy

A template can be public only when:
1. scheme and effective cohort are stated;
2. all mandatory rules have been checked by a human;
3. source documents and checked date are stored;
4. golden DOCX/PDF documents pass visual regression;
5. any unsupported or ambiguous rule is labeled;
6. marketing copy describes scope accurately.

## 6. Student-provided college addendum

MVP can let students attach a local instruction PDF/DOCX and optionally configure a private override manually. Do not infer rules from the uploaded document without user review. Treat any extracted rule suggestions as drafts. Preserve the original university rule and the override separately, displaying conflicts.
