# Tomvis V3 development plan

Updated 2026-10-10. Version 3.0.0-alpha.1 is a development milestone, not a production-readiness claim.

## Product scope
Reusable domain-neutral framework with Feedback as the provisional reference application. The user's original V2 specification remains the feature baseline. Production target retains the audited V1 Next.js, Prisma/MySQL and identity controls. Local SQLite code remains a sandbox prototype until production composition and migration are validated.

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
- V2 local Feedback prototype and tests preserved on their original branch.
- V3 branch starts from the tested V2 commit.
- Added checksummed transactional SQLite migration runner, legacy V2 compatibility and tenant-query indexes.
- Added validated runtime configuration and migration/configuration tests.
- Production MySQL migration, identity integration, complete browser QA and deployment remain pending.

## Compatibility and safeguards
Do not change V1 or production databases. Do not connect synthetic sandboxes to production. Do not rename the existing API prefix solely because the product version changes. New schema versions must have reviewed migrations. Production release requires evidence for every gate above; skipped tests are recorded as pending.
