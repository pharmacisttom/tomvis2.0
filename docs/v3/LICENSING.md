# V3 developer licensing and package entitlements

Status: agreed product requirement and implementation specification; runtime module not yet implemented. Updated 2026-10-10.

## Issuance boundary
The developer licensing authority issues a signed license for a specific customer tenant, product and purchased package. Customer Studio instances validate licenses; they do not receive the signing private key or issuance capability. Every product uses the shared verification contract through a product adapter.

License issuance is enabled only when the issuing service is in production, explicitly activated by the platform operator, and the authenticated developer has `licenses.issue`. Production mode alone is insufficient. Customer admin roles never inherit developer issuance rights. Both UI and backend enforce these rules. Demo/sandbox/development cannot issue live licenses. Existing local alpha continues to reject production startup; adding this specification does not enable production.

## Package catalog
Developer-managed versioned package definitions contain: package ID, product ID, display name, permitted features/modules, maximum users, VPS instances, monitored systems, monitoring interval floor and support term where applicable. Names, prices and quotas are configurable; no commercial values are assumed. Licenses snapshot an immutable package version so edits do not silently change existing purchases.

## Signed license claims
`version`, `license_id`, `issuer`, `audience` (product), `tenant_id`, `package_id`, `package_version`, `features`, `limits`, `environment`, `issued_at`, `not_before`, `expires_at`, `installation_binding` (optional) and `key_id`.

Use an established signed-token format/library with an explicit asymmetric algorithm allowlist. Only public verification keys ship to customer systems. Never accept a token-selected algorithm, unsigned token, wrong product, wrong tenant, wrong environment, unknown key ID or expired token. A license grants package entitlements, not authentication or user permissions. Backend authorization requires both user permission and package entitlement for every gated action.

## Lifecycle and enforcement
- Issue only after developer records an approved purchase/activation; do not infer payment success.
- Generate, renew, upgrade, suspend and revoke with transactional audit records and least-privilege permissions.
- Define online revocation polling, freshness policy, license expiry, offline operation and a documented configurable grace window before implementation. Signed offline licenses cannot provide instant revocation by themselves.
- On expiry or suspension preserve customer data and provide read/export and recovery paths according to explicit policy. Do not silently delete data or halt unrelated services.
- Enforce limits atomically at the backend; customer settings cannot increase purchased quotas. Validate monitoring schedules against package floors.
- Store signing keys in an operator secret manager, separate from customer and sandbox credentials. Rotate through key IDs and publish a reviewed verification key set.
- Avoid logging complete activation tokens. Audit issue/renew/upgrade/revoke with safe identifiers and request IDs.

## Acceptance gates
Unauthorized developer and customer admin cannot issue; non-production issuer cannot issue; unactivated production issuer cannot issue; forged/expired/wrong-tenant/wrong-product/wrong-environment licenses fail; package limits cannot be bypassed via API or concurrent requests; tenant configuration remains isolated; key rotation and revocation/grace behavior are verified. Production rollout requires these tests plus operational review.
