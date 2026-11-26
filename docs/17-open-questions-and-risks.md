# Open questions, assumptions and risks

## 1. P0 questions before production template publication

1. Which exact VTU scheme and admission/cohort combinations are target users following for the selected project report?
2. Does the 2022 project-work guidance apply to the current target cohort, and are 2025 scheme instructions different or additive?
3. What does the student's own college/department require beyond VTU's published guidance (font family, spacing, certificate wording, cover page, bound-copy rules)?
4. Are there current amendments after the inspected VTU documents?
5. Which requirements are mandatory versus suggested?
6. Which report categories must be supported at launch (Phase 1, Phase 2, major project, internship)?

## 2. P0 technical risks

### R1 — DOCX fidelity
**Risk:** A formatter can destroy tables, floating images, fields, section breaks or page numbering.  
**Mitigation:** DOCX feasibility spike and golden corpus before editor build; feature support matrix; immutable original; explicit warnings; block unsafe transformations.

### R2 — Rendering differences
**Risk:** Word, LibreOffice and browser may paginate differently due to fonts and layout engine differences.  
**Mitigation:** Pin renderer and fonts; render final PDF using the same engine as preview; allow user to inspect output; don't claim identical output across all Word versions.

### R3 — Rule applicability
**Risk:** User selects wrong scheme or a college has an extra circular.  
**Mitigation:** Ask cohort/report details, show source date and version, let user add override, unresolved state blocks “verified” badge.

### R4 — Pricing pressure
**Risk:** Existing tools may offer very low-price or free output.  
**Mitigation:** Differentiate on high-quality import/correction, transparency and editable exports; test willingness to pay before investing in broad features.

### R5 — Cost of document processing
**Risk:** Large documents and repeated conversions consume CPU and storage.  
**Mitigation:** Worker limits, quotas, deduplicated jobs, page limits, queue metrics and price/cost measurement.

### R6 — Academic integrity
**Risk:** Students may misuse AI to fabricate material or references.  
**Mitigation:** No full-report generation in MVP; preserve provided content; label optional assistance; require source verification and student review.

### R7 — Legal/data handling
**Risk:** Student reports contain personal and unpublished data.  
**Mitigation:** Privacy-by-default, clear retention/deletion, no training on reports, private storage and qualified review of Indian privacy/payment obligations.

## 3. Product decisions still open

- Name/brand/domain.
- Free preview depth and watermark policy.
- Exact report price and validity period.
- Whether multiple exports are included or capped.
- Team collaboration and sharing rules.
- Manual editor content model and equations implementation.
- Whether PDF input is accepted only for OCR/extraction or omitted in MVP.
- Auth provider, hosting region and storage provider.
- User-support and refund workflow.

## 4. Assumptions in this starter

- Student can self-serve without college onboarding.
- DOCX is the first editable import format.
- A4 and the formatting details transcribed in the VTU baseline are relevant to the intended initial template, but scheme applicability needs confirmation.
- Document rules can be represented as machine-readable, versioned configs.
- PDF preview can be produced through isolated LibreOffice rendering.
- Per-project purchase is more natural than monthly recurring billing at MVP.

## 5. Stop/go criteria

Pause broad feature development if:
- DOCX spike shows unacceptable preservation for typical student files;
- there is no clear way to identify the correct scheme/cohort requirements;
- students do not value import/correction enough to pay;
- worker/render costs exceed plausible per-report pricing;
- the editor cannot show reliable server-rendered pages.

A smaller, honest product supporting a clear subset is better than an “automatic formatter” that silently damages reports.
