# Configurable security testing

Status: policy validator and CI implemented; scanner execution, UI, persistence, reports and customer VPS connection are pending. No live customer scans have run.

## Per-tenant policy
Customer/system policies define enabled status, allowed HTTPS origins, environment, passive/active mode, maximum duration, request rate, authorization approver and validity window, report retention and notification channel. Policies and authorization must be server-owned trusted records, not caller-supplied flags. Developer privileges do not imply customer target authorization.

`packages/security/scan-policy.js` currently validates permission, tenant scope, authorization window, target scope, environment and job limits. It does not implement a scanner or DNS/redirect safety. Future worker must enforce stop deadlines, rate limits across workers, URL/DNS/redirect revalidation and network egress restrictions against metadata endpoints and out-of-scope hosts. Private VPS targets require a dedicated authorized connector, not arbitrary internet proxy access.

## Test layers
1. Every commit: syntax, unit/API, tenant isolation, migration, authorization, security-policy regression checks through GitHub Actions.
2. Next integration: CodeQL/SAST, secret scanning, dependency advisory checks and container scanning. Configure tool availability and retention before enabling. Existing alpha has no npm dependencies; future pinned packages require lockfile reviews.
3. Authorized staging: ZAP baseline/passive inspection; authenticated coverage through disposable accounts; selected active testing with explicit scope and window. Baseline crawler still generates requests and may hit state-changing GET routes, so it is not assumed to have zero impact.
4. Production: passive checks only under default policy and explicit target-owner authorization. No automated active scan, exploit attempt, destructive probe or traffic stress test.
5. Before release: manual pentest of authorization, tenant isolation, token/license issuance, SSRF, secret exposure and business logic; automated findings alone do not prove security.

Security scanning is distinct from uptime monitoring and package licensing. Reports may contain sensitive paths or evidence; restrict them by tenant, redact secrets and define retention. Critical/high findings require triage and reviewed remediation; do not silently suppress findings to pass a gate. Scan results always retain tool/version, target scope, timestamp and coverage limitations.

## Reduce development time
Reuse V1 identity/RBAC and MySQL services rather than implement a second production auth stack. Deliver one end-to-end Developer Studio slice (system registration → authorized health check → current/unknown status → audit), followed by customer configuration and entitlements. Reuse module contracts, shared UI and synthetic fixtures. CI stops failures early and cancels superseded runs. Defer optional adapters and business domains until this slice is verified. No percentage/time guarantee is assumed without measuring the backlog and integration effort.

References: https://www.zaproxy.org/docs/docker/baseline-scan/ ; https://docs.github.com/en/code-security/concepts/code-scanning/setup-types
