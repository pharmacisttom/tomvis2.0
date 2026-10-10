# V3 Backup and Recovery baseline

Status: product requirements and implementation specification. No backup executor, storage connector, restore job or customer VPS access has been implemented or run. Updated 2026-10-10.

## Required protection
Use a 3-2-1 baseline: primary data plus two backup copies, two independent storage/media types, at least one off-site. Include an offline or immutable copy with separate credentials and administration. A copy on the same VPS is not disaster recovery. Encrypt backup transport and stored artifacts; maintain separately protected recoverable encryption keys. Restrict operators through least privilege and audit.

Cover database, uploaded objects, tenant settings, module/package versions, migration state, deployment manifests and recovery documentation. Back up secrets through a separate operator-controlled vault recovery procedure; do not bundle plaintext .env files, production credentials or license signing keys into customer archives. Record consistency point across database and object storage.

## Customer policies
Tenant/system policy includes database adapter, protected sources, destination credential references (never raw secrets), schedule/timezone, retention, encryption-key reference, immutable/offline protection, RPO, RTO, capacity quota, restore-test frequency, alerts and permitted operators. Packages may offer different capacity/frequency options without bypassing isolation, encryption, audit or restore checks. Minimum baseline and changes require operator validation.

Example planning targets only: daily full backup, daily copies retained 7 days, weekly copies 4 weeks, monthly copies 12 months; RPO 24 hours, RTO 4 hours. These are not guarantees. Choose actual targets and retention with the customer based on transaction volume, data sensitivity, recovery needs and measured restore performance. Frequent transactions may require continuous binlog archival/PITR and a shorter RPO. Lifecycle expiration must respect immutable retention and approved holds.

## Adapter consistency
- MySQL/InnoDB: consistent logical/physical backup with a pinned supported tool; prevent conflicting DDL during logical backup. Include routines/events/triggers and the appropriate binlog/GTID recovery metadata when required. Non-transactional tables need a separately reviewed consistency method.
- PITR: retain a verified full backup and all required binary logs through the desired recovery point; monitor gaps and retention. Validate tooling against the deployed MySQL version.
- Local SQLite prototype: use SQLite's online backup capability or a tested consistent snapshot procedure; never blindly copy an actively written database/WAL.
- File/object storage: versioned manifest, checksums and matching database references; incremental/versioned copies where supported.
- VPS snapshot is supplementary; verify application/database consistency and a restore procedure before counting it as recoverable.

## Job evidence and monitoring
Record backup ID, tenant/system, source/adapter, environment, schema/app version, started/completed timestamps, size, protected storage location reference, checksum, encryption key ID, consistency point, retention deadline and last restore-test result. Never expose archive contents or signed download URLs in ordinary logs. Bounded retries, lock against conflicting jobs, cleanup partial artifacts and alert for failures, missing/stale backups, quota/capacity problems or restore-test failures.

Use distinct statuses: queued, running, artifact-created, integrity-verified, restore-tested, failed. A successful upload or checksum is not proof of successful recovery. Dashboard shows the last successful backup and last tested restore separately. Missing integration means not configured, never healthy.

## Restore workflow
Authorize with `backups.restore` in the same tenant and explicit target environment. Restore to a clean isolated environment first, validate decryptability, integrity, schema/application compatibility, tenant ownership, row/object consistency and application behavior. Record measured RPO/RTO and evidence. Customer archives must not be restored into demo/sandbox environments exposed to unrelated users.

For shared multi-tenant databases, a whole-database dump includes other customers. Do not expose it as a tenant download or overwrite the shared production database for a single-customer restore. Restore the full snapshot in restricted isolation and extract/import only the authorized tenant through reviewed scoped tools, preserving relational consistency.

Production replacement needs a concrete restore preview, explicit owner approval, maintenance plan, a pre-restore backup and rollback/recovery plan. Do not automatically overwrite production or run schema downgrades. Drill recovery at a customer-approved interval and after material schema/infrastructure changes. Separate permissions for configure, run, view, download, restore and retention deletion; audit each critical action.

## Acceptance gates
Tenant A cannot list/download/restore B backups; no archive secrets leak; incomplete/corrupt/wrong-key backups fail validation; interrupted jobs cannot become successful; shared-database restore preserves other tenants; backup storage outage triggers alerts; new environment rebuild and PITR are rehearsed where supported; version/DDL consistency and encrypted restore are verified. Document and measure results before declaring disaster-recovery readiness.

References:
- https://www.cisa.gov/stopransomware/ransomware-guide
- https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-165a
- https://dev.mysql.com/doc/refman/8.0/en/mysqldump.html
- https://downloads.mysql.com/docs/mysql-backup-excerpt-8.0-en.a4.pdf
