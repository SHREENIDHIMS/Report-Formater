# Payments and entitlement model

## 1. Business model recommendation

Start with a per-report/project pass. The student's need is tied to one submission and may be seasonal. Do not default to a monthly subscription in MVP.

Possible future product pass: a 90-day window for revisions and multiple exports on one project. Test whether students prefer a fixed report price or a time-limited pass.

## 2. Free-to-paid experience

Free:
- account and workspace;
- choose and inspect template;
- upload and run a limited import check;
- view a useful preview/validation summary;
- make limited draft edits if affordable.

Paid:
- apply selected final transformations (depending on product policy);
- full DOCX export;
- final rendered PDF export;
- defined revision/re-export window;
- team sharing only if collaboration is implemented and explicitly included.

Do not surprise the user after a long upload. Explain before processing which features are free and which require payment.

## 3. Initial price tests (hypotheses)

- Single report pass: test ₹49 / ₹79 / ₹99.
- 90-day project pass: test ₹149 / ₹199 / ₹249.
- Team pass (later, only when shared editing exists): test ₹249 / ₹299 / ₹399 for one shared project.

These are experiments, not final recommendations or current market averages. Confirm gateway charges, taxes and refund obligations before launch.

## 4. Entitlement fields

- `entitlement_type`: `single_report`, `project_pass`, `team_project_pass`.
- `scope`: project ID and optionally document ID.
- `starts_at`, `expires_at`.
- `included_exports` / `exports_used` or unlimited-within-window policy.
- `included_members` if collaboration exists.
- `status`: pending, active, expired, revoked, refunded.
- `source_order_id`.

Keep entitlement rules explicit. Example: a purchase grants unlimited edits and up to 10 final exports for one report for 30 days. Choose actual limits only after cost/UX testing.

## 5. Checkout lifecycle

1. Authenticated user requests order for a report/project.
2. API reads server-side price catalogue and creates pending order.
3. Gateway order created using server secret.
4. Client completes checkout via provider UI.
5. Provider sends signed webhook.
6. API verifies signature on raw body, amount/currency/order mapping and unique event ID.
7. In a transaction, mark order paid and create entitlement once.
8. Enqueue export job or allow user to request export.
9. UI polls order/entitlement state; never trust client redirect alone.

## 6. Failure handling

- Pending: show awaiting confirmation.
- Failed: allow retry with a new checkout session; keep old order for audit.
- Duplicate webhook: no duplicate entitlement.
- Webhook delayed: reconcile via provider API; don't grant from client signal.
- Refunded: revoke future use according to refund terms; existing downloads cannot be recalled, so policy must say this clearly.
- Partial export failure: do not consume entitlement twice; support retry.

## 7. Payment product catalogue

Store pricing in server-controlled product table/config with effective dates. Frontend only displays values returned by API. Amounts use integer paise. Never accept client-supplied amount or entitlement type without verifying catalogue eligibility.

## 8. Subscription decision

Do not launch recurring monthly billing until the product has a continuing use case (several report types, recurring portfolio, repeated semester submissions). A project season pass is simpler to explain and maps to the customer's job.
