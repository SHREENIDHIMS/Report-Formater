# Deployment and operations plan

## 1. Environments

- Local: Docker Compose PostgreSQL/Redis, local private storage, API/web dev servers.
- Preview/staging: production-like containers, separate database/bucket/payment sandbox, synthetic data only.
- Production: managed PostgreSQL, private object storage, Redis, web/API/worker containers, payment production account.

Never share production customer reports with preview/staging. Never use production payment credentials in local `.env`.

## 2. Container boundaries

- Web container: serves Next.js; no document conversion binary required.
- API container: auth, routes, database, job enqueueing; no untrusted document conversion in request process.
- Worker container: parser/formatter/LibreOffice; non-root, limits, no network by default.
- Migration job: run Alembic migrations once as controlled deployment step.

## 3. Production checklist

- Domain and TLS.
- Secrets manager, not repository environment files.
- Database backups and point-in-time recovery.
- Private object bucket, encryption at rest and lifecycle policies.
- Queue retry/dead-letter handling.
- Worker CPU, memory, timeout and concurrency limits.
- Object upload/download size limits.
- Signed URL TTL and server authorization.
- Payment webhook endpoint, signature verification and event replay protection.
- Sentry/error tracking with data scrubbing.
- Structured logs and metrics.
- Rate limits and abuse monitoring.
- Health/readiness/liveness checks.
- Dependency/image scanning.
- Restore drill and incident runbook.

## 4. Metrics

Operational metrics:
- upload volume/bytes;
- import success/failure by safe error code;
- worker queue wait and processing duration;
- LibreOffice render duration/failure;
- page count distribution;
- retry and dead-letter count;
- storage bytes;
- API latency/error rate;
- payment webhook lag and entitlement activation errors.

Product metrics should use IDs/categories, not report body text.

## 5. Alerts

- worker failure rate above baseline;
- queue age/length above threshold;
- rendering timeout spike;
- database saturation/connection errors;
- storage upload/download failures;
- webhook signature failures/processing backlog;
- suspicious cross-user authorization failures;
- backup failure.

## 6. Backup and recovery

- Automated database backups with retention and PITR where supported.
- Object storage versioning or replication policy appropriate to cost and privacy commitments.
- Periodically test restoring database and a sample set of objects.
- Define recovery point objective (RPO) and recovery time objective (RTO) before paid launch; do not claim a guarantee without measured drills.

## 7. Runbooks to write before launch

- Stuck document job.
- Corrupted/malicious upload.
- Failed PDF render.
- Payment succeeded but entitlement missing.
- Refund and entitlement revocation.
- User report deletion.
- Data access incident.
- Database restore.
- Object storage credential rotation.
