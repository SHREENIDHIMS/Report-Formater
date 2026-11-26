# Market, positioning and business model

## 1. Market thesis

The pain is concrete: students must prepare a long, structured report under formatting rules and often correct layout after review. A self-serve formatter removes institutional sales friction and makes the buyer/user the student.

The opportunity is not “no one has made a report generator”. A preliminary market scan found adjacent products that advertise report generation/formatting and low-price per-report or time-pass offers. Therefore, basic formatting and template selection are table stakes.

## 2. Competitive positioning

Products surfaced during preliminary research:
- ReportCraft — advertises report creation/formatting and DOCX/PDF workflows.
- Submitra — advertises university-specific report generation and a low-cost per-report model.
- Paperly — advertises academic report editing and time-limited passes.
- FlowCV — not a direct competitor; a strong UX reference for guided template selection, live preview, autosave and export.

These are research leads, not independently tested competitive benchmarks. Before launch, manually test each current product with the same sample DOCX and record actual fidelity, supported formats, price, export quality and terms. Recheck pricing and claims on the day this document is used.

## 3. Recommended positioning

“VTU-focused report editor and formatter that can work with the report you already wrote.”

Lead with:
1. Import existing DOCX and see detected content/features.
2. Review a clear preview and rule-by-rule errors.
3. Edit without rebuilding the report from scratch.
4. Download DOCX and PDF.

Avoid positioning as:
- an AI that writes a complete final-year project;
- an official VTU service;
- an approval/marks/plagiarism guarantee;
- a universal Word replacement.

## 4. Proposed pricing experiments (not final prices)

Test only after document fidelity is good enough:

| Offer | Price hypothesis | What is purchased |
|---|---:|---|
| Free preview | ₹0 | Create/import, inspect template, limited validation preview; watermark/limits only if clearly disclosed |
| Single report pass | ₹49–₹99 | One report/project, paid DOCX/PDF exports, 30-day editing and re-export window |
| Project season pass | ₹149–₹249 | One report with 90-day revisions/exports; test if buyers value longer access |
| Team project pass | ₹249–₹399 | One shared project, up to five collaborators if collaboration ships |

Test price points with actual student interviews and a landing-page conversion experiment. Do not assume the cheapest competitor's price is profitable.

## 5. Why per-report first

Final-year project formatting is seasonal and the student's need may end after submission. Monthly recurring billing may create churn and customer distrust. A one-time purchase maps naturally to a single report.

A later monthly/semester plan may work only after the product supports several report types, multiple projects, resumes/internship reports or other recurring student document needs. Do not add a subscription merely because it is common SaaS practice.

## 6. Team purchase policy

Treat a team report as one paid project, not five separate charges for each co-author. Model `project_members` separately from billing so the entitlement can authorize one shared project. MVP can initially support one owner and add collaborators later, but pricing copy should not imply sharing is available until implemented.

## 7. Unit economics to measure

- Payment gateway fee and GST/tax treatment (confirm with an accountant/payment provider).
- Storage GB/month per report and retention policy.
- Worker CPU minutes per import/transform/render.
- Retry rate and failed job support cost.
- Refund rate and payment disputes.
- Support time per paid report.
- Paid conversion after preview.
- Contribution margin per order.

No final price or tax treatment is recommended in this document. Confirm current payment provider pricing, applicable Indian tax obligations and consumer/refund requirements before launch.

## 8. Validation plan

1. Interview 15–25 VTU students from different branches/schemes. Ask them to show their real circular and anonymized Word report.
2. Collect 20–30 consented sample DOCX files spanning clean and messy formatting.
3. Offer a concierge formatting pilot: measure actual time saved and correction count.
4. Run a landing-page test with three messages: “format existing DOCX”, “VTU report compliance check”, “build from scratch”.
5. Ask students to pay a small real pilot price rather than relying only on stated willingness.
6. Compare price points (e.g. ₹49, ₹79, ₹99) and report pass duration.
7. Interview supervisors only to understand common formatting corrections; faculty participation is research, not a product dependency.

## 9. North-star metrics

- Successful paid exports per active student/project.
- Percentage of uploads producing a structurally safe, accepted transformation.
- Student-reported reduction in formatting correction rounds.

Guardrails: data-loss incidents (must be zero known), refund rate, unsupported-feature rate, render job failure rate, and privacy/security incidents.
