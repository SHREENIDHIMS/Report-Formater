# Architecture Decision Records

## ADR-001 — Student-first independent SaaS
**Status:** Accepted for MVP.  
**Decision:** Students can register and use the product without college/faculty onboarding.  
**Reason:** Direct student value and lower go-to-market friction.  
**Consequence:** Templates need source provenance and clear status; user-supplied college addenda may be needed. This is not a claim of institutional approval.

## ADR-002 — VTU-first scope
**Status:** Accepted for MVP.  
**Decision:** Start with VTU B.E./B.Tech. project reports; expand only after validation.  
**Reason:** Focus and ability to verify a narrow format set.  
**Consequence:** Scheme/cohort and college differences must be resolved before template publication.

## ADR-003 — Deterministic formatting engine
**Status:** Accepted.  
**Decision:** Layout comes from structured rules; AI does not determine margins/font/numbering.  
**Reason:** Reproducibility, explainability and reduced hallucination risk.  
**Consequence:** More upfront document engineering, but testable output.

## ADR-004 — Immutable original and versioned transformations
**Status:** Accepted.  
**Decision:** Original upload stays immutable; every transformation creates a new document version and operation/change report.  
**Reason:** Avoid data loss and enable undo/audit.

## ADR-005 — Server-rendered PDF preview
**Status:** Proposed, must validate in spike.  
**Decision:** Use isolated LibreOffice rendering as canonical preview/export path.  
**Reason:** Browser CSS pagination does not reliably match Word/office output.  
**Consequence:** Rendering is asynchronous and resource intensive; fonts and LibreOffice version must be pinned.

## ADR-006 — Structured editor plus controlled DOCX bridge
**Status:** Proposed.  
**Decision:** Use Tiptap/ProseMirror for structured authoring, not as a universal DOCX round-trip engine.  
**Reason:** Rich editing and semantic content model are valuable, but arbitrary Office features exceed a browser editor's native model.  
**Consequence:** Import capability is explicitly scoped and feature-tested.

## ADR-007 — Modular monolith plus isolated document worker
**Status:** Accepted for initial architecture.  
**Decision:** FastAPI modular monolith; separate worker for document parsing/rendering.  
**Reason:** Simpler than microservices while isolating untrusted CPU-heavy document processing.

## ADR-008 — Per-report monetization first
**Status:** Accepted for pricing experiments.  
**Decision:** Start with one-time report/project purchase; test 30/90-day revision window.  
**Reason:** Academic report use is seasonal; monthly recurrence is unproven.

## ADR-009 — No college portal in MVP
**Status:** Accepted.  
**Decision:** Do not build institutional onboarding or approval workflow initially.  
**Reason:** Direct-to-student product scope.  
**Consequence:** A future template curation process can be internal/admin-only and does not require public college accounts.
