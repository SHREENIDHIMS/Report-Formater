# Documentation index

| Document | Purpose |
|---|---|
| `00-product-brief.md` | Concise product definition and positioning |
| `01-product-requirements-document.md` | Product requirements, personas, scope, acceptance criteria |
| `02-market-and-business-model.md` | Competition, positioning, pricing experiments, economics |
| `03-user-flows-and-ui-spec.md` | Pages, interaction flows, editor UX and accessibility |
| `04-architecture-and-tech-stack.md` | Recommended architecture and implementation stack |
| `05-document-engine-design.md` | Import, normalize, transform, render and validate DOCX/PDF |
| `06-vtu-guideline-baseline.md` | Evidence-based VTU rule baseline and verification caveats |
| `07-template-schema-and-rule-model.md` | Versioned template config and rule schema |
| `08-data-model.md` | Proposed entities and key constraints |
| `09-api-contract.md` | Initial REST API resource map and sample contracts |
| `10-security-and-privacy.md` | Threat model, file security, privacy and retention |
| `11-payments-and-entitlements.md` | Per-report purchase model and payment workflow |
| `12-testing-and-quality-plan.md` | Test strategy, golden docs and release gates |
| `13-roadmap-and-backlog.md` | Ordered implementation tickets and acceptance criteria |
| `14-agent-implementation-plan.md` | How to delegate work to a coding agent |
| `15-architecture-decision-records.md` | Initial ADRs and decision log |
| `16-deployment-and-operations.md` | Environments, deployment, observability and backups |
| `17-open-questions-and-risks.md` | Risks, unknowns and pre-launch decisions |
| `18-research-sources.md` | Source register, accessed date and interpretation |

## Reading order

Start with 00, 01, 04, 05, 06, 13, 17. Use 09, 10, 11 and 12 when implementing the respective subsystem.

## Status labels

- **Verified source fact**: directly stated in an identified authoritative source.
- **Product decision**: recommendation made for this product; can be revisited through an ADR.
- **Proposed**: implementation design that still needs technical validation.
- **Open**: not yet established; do not hardcode as fact.
