# Tomvis V3 development plan

Updated 2026-10-10. Version 3.0.0-alpha.1 is a development milestone, not a production-readiness claim.

## Product scope
Reusable domain-neutral framework hosting **TomvisHIMPro Developer Studio**, the user's clarified primary product: a central workspace for systems running on VPS and monitoring their operation. Feedback remains a reference module for framework tests. The user's original V2 specification remains the feature baseline. Production target retains the audited V1 Next.js, Prisma/MySQL and identity controls. Local SQLite code remains a sandbox prototype until production composition and migration are validated.

## Developer Studio scope (user clarification)
- Automatically generated user manuals from registered module guides, available in the authenticated sidebar and filtered by backend permissions. Current reference app implemented; future app scaffolding contract in AUTO_MANUAL.md.
- Per-tenant Backup & Recovery: encrypted off-site/offline or immutable backups, retention, RPO/RTO, scoped restore and restore-test evidence. See BACKUP_RECOVERY.md; backup executor/storage/restore integration remain pending.
- Configurable customer/system security-test policy and release gates: see SECURITY_TESTING.md. Validator and CI are implemented; live pentest and scanner integration remain pending.
- Per-customer package licensing: developer-only production issuance, tenant/product-bound signed licenses and backend package entitlements. See LICENSING.md; runtime implementation and commercial package values remain pending.
- System registry: project, repository, owner, deployment environment, domain and permitted host assignments.
- VPS inventory: logical host records, adapter type (PM2/Docker/other), connection status and explicit access scopes. No secrets in records or API responses.
- Monitoring: real health probes, freshness timestamps, unknown/unreachable states, uptime history, resource/process/container metrics where adapters provide them, and incident notifications.
- Operations: authorized log access, deploy history, rollback metadata and audited operational actions. Start with read-only monitoring; production deploy/restart/rollback requires a separately reviewed workflow and explicit operational authorization.
- Environment separation: development/demo/sandbox/staging/production per system; no sandbox connector may use production credentials.
- Security: tenant ownership and resource permissions for every host/project/action; least-privilege collectors, redaction, retention limits, bounded requests and SSRF-safe probe configuration.

Repository/path for existing TomvisHIMPro Developer Studio, VPS system inventory and current monitoring tooling have been requested. Live infrastructure access has not been supplied or performed. Do not fabricate online/healthy status, metrics or uptime. Unknown and not-connected are first-class states.

## Milestones and release gates
1. Foundation: versioned internal package boundaries, module registry, configuration validation, incremental migrations, migration rollback tests, CI and developer commands. First increment adds an actual migration runner and centralized runtime validation.
2. Identity: integrate existing V1 Argon2id/session/2FA/reset controls, tenant/organization/membership model, disabled/locked-account flows and session revocation. Gate: authentication lifecycle and cross-tenant tests on disposable MySQL.
3. Authorization: database custom roles and permissions, resource scopes, tenant constraints, privileged audit transactions. Gate: role assignment escalation and cross-tenant access denied at backend.
4. Feedback reference: validated CRUD, pagination/filter/sort, dashboards, notification center, accessible responsive UI. Gate: browser E2E and overflow checks at 360, 390, 768, 1024 and 1440px.
5. Sandbox lifecycle: private creation/seed/reset/expire/destroy, API sandbox, key scopes, synthetic fixtures, scheduler cleanup and environment guards. Gate: sandbox cannot reach production credentials/data/live API.
6. Integration: API key hashing/rotation/revocation, signed webhooks with retry and delivery logs, storage/notification/job adapters and simulators. Gate: signature/replay/retry/SSRF and scope tests.
7. Operations: health/readiness, doctor, structured logs, documented backups, MySQL migrations, Nginx/PM2/Docker examples and deployment checks. Gate: lint, types, unit/integration/E2E/build, security review, restore rehearsal and reviewed release.
8. Reference modules: Workforce, then EMS after Feedback and Core are stable. Other business domains are separate adapters/modules.

## Current evidence
- Active FastAPI backend and Next.js/React frontend implemented with shared contracts; compatibility tests preserve Node alpha database, scrypt passwords and hashed sessions. Actual Next build and real HTTP integration pass.
- Domain-neutral reporting with Feedback/Users adapters, CSV and print UI, safe local Framework error reporting and React error boundaries implemented. Domain adapters/central collection are pending.
- Browser workflows, CSV formula-prefix protection and no horizontal overflow verified at 360/390/768/1024/1440 with synthetic data; print PDF generated. Comprehensive accessibility/financial and multi-page print acceptance remain pending.
- V2 local Feedback prototype and tests preserved on their original branch.
- V3 branch starts from the tested V2 commit.
- Added checksummed transactional SQLite migration runner, legacy V2 compatibility and tenant-query indexes.
- Added validated runtime configuration and migration/configuration tests.
- Production MySQL migration, identity integration, complete browser QA and deployment remain pending.

## Compatibility and safeguards
Do not change V1 or production databases. Do not connect synthetic sandboxes to production. Do not rename the existing API prefix solely because the product version changes. New schema versions must have reviewed migrations. Production release requires evidence for every gate above; skipped tests are recorded as pending.
