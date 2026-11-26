# Testing and quality plan

## 1. Test pyramid

- Unit: rule evaluation, numbering, document IR validation, entitlement policy, permissions.
- Integration: PostgreSQL repositories, object storage adapter, queue, payment webhook signature/idempotency, document worker.
- Golden-document: import/transform/render comparison on a curated DOCX corpus.
- End-to-end: signup -> create project -> import/manual author -> validate -> checkout -> export -> download.
- Security: malicious archive, ZIP bomb, path traversal, cross-user IDs, webhook replay, expired signed URL.
- Manual usability: student testing on Windows desktop/Chrome and common university report documents.

## 2. Golden document corpus

Create a permissioned, anonymized test corpus (do not commit private student reports to a public repository). Include:
1. Simple Word document with headings and paragraphs.
2. Multiple section breaks and page setup variations.
3. Tables with merged cells and long cell content.
4. Inline images with captions.
5. Floating/anchored images and text wrapping.
6. Headers/footers/page number fields.
7. TOC, cross-references and bookmarks.
8. Bullets and multilevel numbering.
9. Equations/OMML.
10. Hyperlinks and citations.
11. Footnotes/endnotes.
12. Track changes/comments.
13. Charts/SmartArt/text boxes if present in target sample documents.
14. Malformed/oversized/hostile DOCX fixtures.

For each fixture keep source checksum, expected feature inventory, output checksum where deterministic, extracted structure snapshot and rendered page images/PDF text/geometry baseline.

## 3. Document regression tests

A transformation passes only if:
- supported text content is preserved (except explicitly documented placeholder insertions);
- image/media count and relationships are preserved where supported;
- table structure and key cell contents are preserved;
- headers/footers/page fields survive supported paths;
- page setup matches selected rule;
- output opens in LibreOffice and ideally Microsoft Word for manual spot checks;
- output PDF renders without blank/corrupt pages;
- no unexpected clipping/overlap above agreed tolerance;
- all known unsupported features are reported.

Visual comparison should account for small renderer/font differences. Keep reference images and use image-diff thresholds with manual review for high-impact regions.

## 4. Validator tests

- Each rule has positive and negative test cases.
- Missing/ambiguous data yields “not evaluated” or warning, not false pass.
- The finding cites its exact template version/rule/source.
- Auto-fix is tested for idempotency and reversibility.
- Conflicting scheme/college overrides create a conflict state rather than silently overwriting.

## 5. API and security tests

- User A cannot list/read/update/download User B's projects, documents, versions, jobs, validation runs or exports.
- Expired/revoked entitlements block paid export.
- Duplicate payment events create one entitlement.
- Invalid signature never grants entitlement.
- Malformed file fails safely and does not expose traceback.
- Rate limits and size limits are enforced.
- User deletion revokes access and queues purge.

## 6. UI/E2E tests

Core Playwright journeys:
1. New user registers and lands on dashboard.
2. User creates manual report and saves draft.
3. User uploads supported DOCX and reviews import inventory.
4. User accepts a formatting preview and receives a new version.
5. User sees validation errors and fixes one.
6. User pays using gateway sandbox and entitlement activates after webhook fixture.
7. User exports DOCX/PDF and downloads after authorization.
8. User cannot access another user's document by changing URL/API ID.

## 7. Release gates

- No P0 security issue.
- No known silent content loss in supported paths.
- No failing golden-doc regression.
- All P0 requirements have automated or documented manual test evidence.
- Payment idempotency and authorization tests pass.
- Backup/restore has been exercised.
- Privacy/terms/refund and deletion wording is published.
- Template has been human-verified for target cohort and checked date.

## 8. Test data management

Use generated synthetic documents or obtain explicit, informed permission for anonymized student documents. Strip names, USNs, email addresses and unpublished project content before using fixtures. Store sensitive corpora in private test storage, not in source control.
