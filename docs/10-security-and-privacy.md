# Security and privacy plan

## 1. Data sensitivity

Uploaded reports may contain student names, USNs, phone/email, guide names, unpublished research, source code, diagrams and project IP. Treat all report content as private user data. Payment data should remain with the payment provider; store only IDs/status and minimal redacted metadata.

## 2. Threat model

Key threats:
- malicious DOCX ZIP bombs or crafted OOXML parser payloads;
- malware or macro-enabled documents;
- LibreOffice conversion process compromise;
- cross-user document/object access;
- leaked signed URLs;
- forged/duplicated payment webhooks;
- accidental public storage bucket or static file exposure;
- report content leaking into logs/analytics/errors;
- XSS through imported document content or filename/metadata;
- dependency/supply-chain vulnerabilities;
- denial of service through huge/complex documents or repeated jobs.

## 3. File pipeline controls

- Private quarantine bucket/prefix.
- Validate file extension, MIME, magic bytes and ZIP package.
- Limits: upload bytes, expanded bytes, entry count, compression ratio, page count, image pixels, processing time and memory. Tune after load tests.
- Reject encrypted documents and macro-enabled extensions in MVP.
- Sanitize filenames for display; generate internal random object keys.
- Parse only inside isolated worker; no outbound network; non-root; least privilege.
- Do not load external OOXML relationships/URLs.
- Malware scanning where available.
- Clean temporary files and worker home directories after each job.
- Use separate service account/credentials with access only to job objects.

## 4. Authorization controls

- Authenticate every private API route.
- Verify project owner/member membership for every document, version, job, export and download.
- Object storage bucket stays private; no guessable public URLs.
- Signed download URLs are short-lived and minted only after authorization.
- Revocation/deletion should block new URLs immediately.
- Add tests for User A accessing every resource type owned by User B.

## 5. Web security

- HTTPS in production; secure, HttpOnly, SameSite cookies where cookie sessions are used.
- CSRF protection for cookie-authenticated mutations.
- Strict CORS allowlist.
- Content Security Policy and security headers.
- Rate limit sign-in, upload initiation, processing, validation, checkout and download routes.
- Output-encode filenames and imported text; do not render imported HTML as trusted markup.
- Keep secret keys server-side only; rotate/revoke on exposure.

## 6. Payment security

- Do not trust browser redirect/success screen as proof of payment.
- Verify provider signatures using raw body and server-side secret.
- Store unique provider event IDs and process idempotently.
- Match amount, currency, order, user and expected product.
- Activate entitlements only after the verified success event or a trusted server-side verification call.
- Never store card numbers/CVV.

## 7. Privacy, retention and deletion

Publish plain-language policy before launch. Product decisions to test:
- User documents private by default.
- Abandoned free drafts retained for a clearly stated period (example 30–90 days; choose after cost/support review).
- Paid project files retained for the purchase window plus a disclosed recovery/grace period.
- User-initiated deletion revokes access immediately and queues binary purge.
- Payment/accounting records may have separate legal retention obligations; confirm with an India-qualified advisor.
- Backups age out on a documented cycle; deletion from live object storage may not mean immediate erasure from immutable backups—disclose accurately.

Do not train models on student documents. Do not use content for product analytics or marketing without explicit opt-in and legal review.

## 8. Logs and telemetry

Log: request ID, job ID, actor ID (internal UUID), resource IDs, safe error codes, duration, byte/page counts and pipeline version.
Do not log: report text, full filenames if they reveal identity, USNs, signatures, payment secrets, access tokens, signed URLs or raw document XML.

## 9. Incident readiness

Prepare processes for:
- suspected malicious file;
- cross-user access incident;
- exposed object-store credentials;
- compromised payment webhook secret;
- accidental document deletion/data loss;
- dependency vulnerability.

Keep backups, test restore, rotate keys and document a user notification/escalation path.
