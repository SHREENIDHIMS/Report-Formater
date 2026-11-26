# How to work with a coding agent

## 1. Operating rule

Give the agent one ticket with clear acceptance criteria at a time. Do not ask it to “build the whole SaaS” in one prompt. The repo contains product decisions and constraints to keep the agent grounded.

## 2. First prompt to paste into a coding agent

```text
You are the senior engineer implementing VTU Report Studio.

First read AGENTS.md, README.md, docs/01-product-requirements-document.md,
docs/04-architecture-and-tech-stack.md, docs/05-document-engine-design.md,
docs/06-vtu-guideline-baseline.md, docs/13-roadmap-and-backlog.md and
docs/17-open-questions-and-risks.md.

Do not implement the whole product yet. Start with DOC-001: DOCX import
feasibility spike. Inspect the current repository, identify the smallest
implementation, and produce:
1. an inventory of DOCX features we can detect;
2. a safe parser implementation in an isolated worker-compatible module;
3. a synthetic test corpus covering section breaks, margins, styles, tables,
   images, headers/footers, fields, numbering and unsupported constructs;
4. malformed/oversized archive tests;
5. a report documenting supported, preserved-only, warning and unsupported
   constructs, with explicit limitations.

Never mutate source files. Do not silently drop OOXML parts. Do not invent VTU
rules. Do not implement AI content generation or payment yet. Add tests and
run the checks. End with files changed, commands run, test results, limitations
and recommended next ticket.
```

## 3. Task prompt template

```text
Ticket: [ID and title]
Read first: [relevant docs/files]
User outcome: [one sentence]
Scope: [in-scope behaviours]
Out of scope: [explicit exclusions]
Acceptance criteria:
- [observable behaviour]
- [error/permission case]
- [test evidence]
Constraints:
- Follow AGENTS.md.
- Preserve original files and avoid silent data loss.
- Use existing architecture and add an ADR before changing a major decision.
Deliverables:
- Code and tests.
- Updated docs/API contracts if changed.
- Summary of files, commands, test results, known limitations and next step.
```

## 4. Agent review checklist

Before accepting generated code ask:
- Does this implement a real user workflow or just create abstractions?
- Are ownership and server-side authorization enforced?
- Does it preserve data and create an immutable version?
- Does each rule have source provenance?
- Is the file path safe against path traversal and object-key guessing?
- Is there a retry/idempotency strategy?
- Are errors safe and useful?
- Are tests realistic, including malicious and boundary cases?
- Did the agent claim a feature is complete without verifying it end-to-end?
- Were dependency versions/license implications checked?

## 5. Parallelization

Can parallelize after the core contract is agreed:
- UI prototype and design tokens;
- template source verification;
- database/API scaffolding;
- DOCX corpus preparation.

Do not parallelize multiple agents changing the same document engine or API schema without clear ownership and integration plan.

## 6. Keep decisions in the repository

When changing stack, page editor, renderer, auth, payment, retention or pricing, add/update an ADR. Do not let important decisions live only in chat history.
