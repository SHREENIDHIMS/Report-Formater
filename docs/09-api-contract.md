# API contract — proposed REST surface

Base path: `/api/v1`. JSON over HTTPS. OpenAPI is generated from FastAPI schemas. Return consistent error shape and request correlation ID. All non-public resources require authenticated, server-side ownership checks.

## 1. Standard responses

Success resources should include stable IDs and timestamps. Error shape:

```json
{
  "error": {
    "code": "DOCUMENT_UNSUPPORTED_FEATURES",
    "message": "This file contains elements that this workflow cannot safely edit.",
    "request_id": "req_...",
    "details": [{"code": "FLOATING_TEXT_BOX", "severity": "warning"}]
  }
}
```

Do not echo file contents, stack traces, secrets or internal object paths.

## 2. Routes (proposed)

### Templates
- `GET /templates?university=VTU&course=BE&report_type=final_year_project`
- `GET /templates/{template_id}/versions/{version_id}`
- `GET /templates/{template_id}/versions/{version_id}/rules`

### Projects and reports
- `POST /projects`
- `GET /projects`
- `GET /projects/{project_id}`
- `PATCH /projects/{project_id}`
- `DELETE /projects/{project_id}`
- `POST /projects/{project_id}/documents`
- `GET /projects/{project_id}/documents`
- `GET /documents/{document_id}`
- `GET /documents/{document_id}/versions`
- `POST /documents/{document_id}/restore/{version_id}`

### Upload and processing
- `POST /uploads/initiate` — create upload session, return short-lived upload URL or multipart instructions.
- `POST /uploads/{upload_id}/complete` — verify object exists, size/checksum, enqueue inspection.
- `GET /jobs/{job_id}` — status/progress/safe failure code.
- `POST /documents/{document_id}/format-previews` — create dry-run transformation plan.
- `POST /format-previews/{preview_id}/apply` — apply accepted changes and create version.

### Editor and versions
- `GET /documents/{document_id}/editor-state`
- `PATCH /documents/{document_id}/editor-state` — optimistic concurrency via version/ETag.
- `POST /documents/{document_id}/checkpoints`

### Validation and export
- `POST /document-versions/{version_id}/validation-runs`
- `GET /validation-runs/{run_id}`
- `GET /validation-runs/{run_id}/findings`
- `POST /document-versions/{version_id}/exports` — enqueue DOCX/PDF generation.
- `GET /exports/{export_id}`
- `GET /exports/{export_id}/download` — authorize, then issue short-lived signed URL.

### Billing
- `POST /checkout/orders`
- `GET /orders/{order_id}`
- `POST /webhooks/razorpay` — raw-body signature verification and idempotent event handling.
- `GET /entitlements`

### Account
- `GET /me`
- `DELETE /me` — start deletion flow.

## 3. Upload initiation example

Request:

```json
{
  "project_id": "uuid",
  "file_name": "project-report.docx",
  "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "size_bytes": 1234567,
  "sha256": "hex-digest"
}
```

Response should include `upload_id`, expiry, upload method and constraints. Never trust client `content_type`/checksum alone; re-check after upload.

## 4. Format preview example

Request:

```json
{
  "document_id": "uuid",
  "input_version_id": "uuid",
  "template_version_id": "uuid",
  "options": {
    "apply_page_setup": true,
    "apply_body_styles": true,
    "normalize_heading_levels": true,
    "add_missing_front_matter_placeholders": false
  }
}
```

Response:

```json
{
  "preview_id": "uuid",
  "status": "ready_for_review",
  "change_summary": {
    "page_setup_changes": 4,
    "paragraphs_restyled": 92,
    "headings_mapped": 14,
    "content_added": 0,
    "unsupported_features": 2
  },
  "warnings": [
    {"code": "FLOATING_IMAGE_ANCHOR", "message": "A floating image could not be safely normalized."}
  ],
  "preview_pdf_available": true,
  "expires_at": "2026-11-26T12:00:00Z"
}
```

## 5. Concurrency and idempotency

- Use ETag/`If-Match` or explicit `expected_version_id` on editor saves.
- Require `Idempotency-Key` for upload completion, job creation, checkout and export jobs.
- Payment webhooks verify raw request body signature before parsing/processing.
- Retryable jobs use bounded retries and terminal error codes.

## 6. Authorization

Never accept `user_id` as authority from client payload. Derive actor from validated auth token. For each requested project/document/version/job/export/order, authorize through its owning project and membership. Use non-enumerating 404 for inaccessible IDs where appropriate.
