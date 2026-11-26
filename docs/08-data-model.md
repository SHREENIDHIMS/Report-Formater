# Proposed data model

This is a domain model proposal. Convert it into SQLAlchemy models and Alembic migrations in a later ticket. Use UUID primary keys and timezone-aware timestamps.

## 1. Entities

### User
- `id`, `auth_provider_subject`, `email`, `display_name`, `status`, `created_at`, `updated_at`, `deleted_at`.
- Unique auth subject; normalized email index if needed.

### Project
- `id`, `owner_user_id`, `title`, `university_code`, `course_code`, `branch_code`, `scheme_code`, `academic_year`, `report_type`, `status`, timestamps.
- Represents one student/team project and its working report.

### ProjectMember (future MVP+)
- `project_id`, `user_id`, `role` (`owner`, `editor`, `viewer`), invite status and timestamps.
- Team members are scoped to project, not global access.

### Template
- `id`, `university_code`, `template_key`, `display_name`, `description`, `created_at`.

### TemplateVersion
- `id`, `template_id`, `version`, `status`, `scope_json`, `manifest_json`, `rules_json`, `source_refs_json`, `published_at`, `verified_at`, `verified_by`, `effective_from`, `effective_to`.
- Unique `(template_id, version)`. Published content immutable.

### Document
- `id`, `project_id`, `created_by_user_id`, `title`, `mode`, `head_version_id`, timestamps, `deleted_at`.

### DocumentVersion
- `id`, `document_id`, `parent_version_id`, `version_number`, `source_kind` (`upload`, `manual`, `transform`, `edit`, `restore`), `template_version_id`, `object_key`, `mime_type`, `size_bytes`, `sha256`, `page_count`, `pipeline_version`, `import_profile_json`, `created_by_user_id`, `created_at`.
- Immutable after creation. Unique `(document_id, version_number)`.

### DocumentAsset
- `id`, `document_version_id`, `asset_kind`, `object_key`, `sha256`, `mime_type`, `size_bytes`, `metadata_json`.

### ProcessingJob
- `id`, `project_id`, `document_id`, `input_version_id`, `output_version_id`, `job_type`, `status`, `progress_percent`, `idempotency_key`, `attempt`, `error_code`, `safe_error_message`, `started_at`, `finished_at`, `created_at`.
- Unique idempotency key within operation scope.

### ValidationRun
- `id`, `document_version_id`, `template_version_id`, `pipeline_version`, `status`, `summary_json`, `created_at`.

### ValidationFinding
- `id`, `validation_run_id`, `rule_id`, `severity`, `category`, `observed_json`, `expected_json`, `location_json`, `confidence`, `fix_status`, `created_at`.

### Order / Payment
- `id`, `user_id`, `project_id`, `document_id`, `product_code`, `amount_minor`, `currency`, `status`, `gateway`, `gateway_order_id`, `idempotency_key`, timestamps.
- Store amount in integer minor units (paise), not float.

### PaymentEvent
- `id`, `gateway`, `gateway_event_id`, `order_id`, `event_type`, `signature_verified`, `processed_at`, `payload_redacted_json`.
- Unique gateway event ID to ensure webhook idempotency.

### Entitlement
- `id`, `order_id`, `user_id`, `project_id`, `entitlement_type`, `max_exports`, `exports_used`, `starts_at`, `expires_at`, `status`, timestamps.
- Rules for team sharing/revisions are explicit and server enforced.

### AuditEvent
- `id`, `actor_user_id`, `project_id`, `resource_type`, `resource_id`, `action`, `metadata_redacted_json`, `created_at`.
- Never store full report text or secrets in audit metadata.

## 2. Relationship overview

```text
User 1---N Project (owner)
Project 1---N ProjectMember ---N User
Project 1---N Document
Document 1---N DocumentVersion
DocumentVersion 1---N DocumentAsset
DocumentVersion 1---N ValidationRun 1---N ValidationFinding
Template 1---N TemplateVersion
DocumentVersion N---1 TemplateVersion
Project/Document 1---N ProcessingJob
User/Project 1---N Order 1---N PaymentEvent
Order 1---N Entitlement
User/Project 1---N AuditEvent
```

## 3. Important constraints

- All project/document queries must include an authorization scope check, not only a guessed user ID from request body.
- Enforce project owner/member access in repository/service layer and tests.
- `head_version_id` must refer to a version belonging to that document.
- Do not cascade-delete immutable versions until retention/deletion policy runs.
- Keep document binaries out of PostgreSQL except small metadata/JSON.
- Template version snapshot used by a report must remain resolvable after deprecation.
- Every payment entitlement must have a source order and explicit scope/expiry.
- Soft delete first; asynchronous purge follows deletion policy.

## 4. Indexes to plan

- project `(owner_user_id, updated_at DESC)`;
- document `(project_id, updated_at DESC)`;
- document_version `(document_id, version_number DESC)`;
- processing_job `(status, created_at)` and unique idempotency;
- validation_run `(document_version_id, created_at DESC)`;
- order `(user_id, created_at DESC)`, gateway order id unique;
- payment_event `(gateway, gateway_event_id)` unique;
- entitlement `(project_id, status, expires_at)`.

## 5. Deletion and ownership transfer

Account/report deletion must revoke signed download access immediately, enqueue object purge according to retention policy, retain only legally/operationally required payment records, and emit a privacy-safe audit event. Team ownership transfer is a later feature and must not be implemented by editing owner IDs without an explicit transaction/audit trail.
