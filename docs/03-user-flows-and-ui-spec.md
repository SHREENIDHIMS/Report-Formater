# User flows and UI specification

## 1. Design direction

Use FlowCV as a reference for simplicity: clear steps, template selection, progressive disclosure, live preview, autosave and obvious export. Do not copy its brand, assets, exact layouts or wording.

Visual direction: calm, confident, academic-professional. Avoid an overly “AI magic” aesthetic. Use a neutral surface, strong typography, a restrained accent colour, clear error/warning/success states and spacious A4 page preview.

## 2. Primary navigation

### Public navigation
- Product
- How it works
- VTU templates
- Pricing
- FAQ
- Sign in
- Primary CTA: Start your report

### Authenticated navigation
- Dashboard
- New report
- Templates
- My reports
- Billing/account

## 3. Key screens

### Screen 1 — Landing page
Hero: “Your project report, correctly formatted.”
Subhead: “Create from scratch or upload your Word file. Choose a VTU format, review corrections and export DOCX/PDF.”
Primary CTA: “Start formatting”. Secondary CTA: “See how it works”.
Below fold: three modes, how it works, example report preview, supported format/status, pricing, privacy/FAQ.
Never use “100% accepted”, “official VTU partner” or unverified claims.

### Screen 2 — Dashboard
- Welcome and create-new CTA.
- Continue editing list with title, last edited, mode, template version and status.
- Report status: Draft / Importing / Needs review / Ready to export / Export failed / Archived.
- Storage and plan usage only if a real quota exists.
- Avoid showing sensitive document contents in dashboard cards.

### Screen 3 — New report mode picker
Three equal cards:
1. Automatic: “I already have a Word report”.
2. Manual: “I want to start a new report”.
3. Hybrid: “Format my report, then edit it”.
Explain file types and limitations before upload.

### Screen 4 — Template picker
Filters: University (VTU), course, scheme/cohort, report category, branch. MVP should show only verified combinations. Card shows template name, status, version, last checked date and what documents it is based on. The student must confirm cohort/scheme. “Not sure?” opens a brief guidance path and does not guess.

### Screen 5 — Project details
Fields may include project title, student names/USNs, guide name/designation, department, college name, academic year, course/branch and project phase. Fields used in certificates are required only when the chosen template requires them. Never fabricate signatures, seals or approval dates. Let students leave values blank and flag missing required data.

### Screen 6 — Upload and import review
- Drag/drop and browse DOCX.
- Show upload limits and file privacy statement.
- Progress states: uploading, checking package, extracting structure, ready.
- Results: paragraphs/headings/tables/images/sections/fields detected; unsupported or risky constructs; page count estimate.
- Student must acknowledge critical warnings before continuing.

### Screen 7 — Transformation preview
- Before/after preview toggle.
- Change summary grouped by page/style/numbering/front matter.
- “Apply all safe changes”, “Review changes”, “Back to settings”.
- No destructive operation on original file.
- Price may be visible, but do not block preview/inspection behind payment unless the user has been told clearly.

### Screen 8 — Editor
Recommended desktop layout:
- Left: document outline and page thumbnails.
- Center: actual page-oriented preview/editor surface.
- Right: selected element controls, template rule info, validation panel.
- Top: save state, undo/redo, preview, validation, export.

Editor interactions:
- Click heading in outline to navigate.
- Add/reorder only sections allowed by template; mandatory sequence is shown.
- Select paragraph to view detected style and applicable rule.
- Insert image/table/caption using guided controls.
- Add page break and section break only with explicit semantics.
- Show unsaved/saving/saved/offline/error states.
- Keep global style settings controlled by template; any override remains visible as a violation.

### Screen 9 — Validation
Group findings by:
- Page setup
- Typography and paragraph styles
- Structure and required sections
- Numbering/captions/references
- Rendering/layout
Each finding: severity, rule label, observed value, expected value, pages/locations, source, fix option and “why this matters”.
Status must say “Checked against [template/version]” rather than “VTU approved”.

### Screen 10 — Export and checkout
Before checkout show:
- Template/version.
- DOCX and PDF deliverables.
- Included revision window.
- Team/collaborator scope.
- Any unresolved warnings.
- Refund/help link.
After payment: export job progress, result, download buttons and validation summary.

## 4. Interaction rules

- Autosave after a short debounce; show explicit status and recover unsaved changes after network interruption.
- Destructive operations require confirmation and soft-delete first.
- Every long-running task has a job ID, progress state, error reason and retry action when safe.
- Never present a spinner without explanatory state for a document job.
- For each automated fix, explain scope and provide undo/version recovery.
- Avoid a WYSIWYG editor that promises pixel-perfect browser/Word parity. The canonical preview must be generated by the server renderer used for the exported PDF.

## 5. Responsive behaviour

- Desktop: full three-panel editor.
- Tablet: collapsible outline/settings panels.
- Mobile: dashboard, upload, project details and page preview supported; editing controls may be simplified. Tell user when best editing experience requires a wider screen.

## 6. Accessibility

- Keyboard-accessible controls and document outline.
- Semantic headings and landmarks.
- Form labels and inline validation.
- WCAG contrast and visible focus.
- Status updates announced to screen readers.
- Do not communicate errors with colour alone.
- Large interactive targets on touch devices.

## 7. Content tone

Helpful and non-judgmental. Replace “Your report is wrong” with “This paragraph uses 11 pt; this template expects 12 pt.” Explain that template rules may need confirmation with the student's department.
