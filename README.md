# Tomvis V3 — Python + Next.js/React

Version 3.0.0-alpha.1. Developer Studio reference application with FastAPI backend, Next.js/React frontend and shared module contracts. V1 is preserved. Production/staging remain disabled; MySQL and live customer VPS connections are not implemented.

## Setup
Requires Node 22.17+ and Python 3.12. From the repository root:

```powershell
npm ci
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r apps/api/requirements.txt
$env:TOMVIS_MODE='sandbox'
$taskDemoPassword=Read-Host 'Choose local demo password (12–256 characters)' -AsSecureString
$env:TOMVIS_DEMO_PASSWORD=[System.Net.NetworkCredential]::new('', $taskDemoPassword).Password
npm run dev
```

Open http://localhost:3000. FastAPI binds to 127.0.0.1:8000. The launcher selects .venv automatically; TOMVIS_PYTHON may point to another interpreter. If python is not installed/on PATH, supply an installed Python 3.12 executable when creating the virtual environment. .env.example documents variables; the root .env is not automatically loaded.

Synthetic demo accounts: admin@tomvis.demo, staff@tomvis.demo, viewer@tomvis.demo. All use the password supplied on first database initialization. Setting a new environment password does not change existing accounts. Node alpha password hashes, session hashes and SQLite data remain compatible with Python. Data stays in ignored data/<mode>.sqlite; no production data is accessed.

## Implemented
- Login/logout, hashed opaque sessions, membership-scoped authorization, transactional audit and tenant isolation.
- Dashboard, Feedback create/search/filter/resolve, users, roles matrix, audit and confirmed sandbox reset.
- Role-filtered searchable user manuals generated from registered module metadata on dev/build.
- Report Studio: Feedback/Users dataset adapters, filters, allowlisted columns, group counts, CSV export and dedicated A4 print/Save-as-PDF layout.
- Tenant-scoped System errors, safe error fingerprints/version/Request ID, occurrence grouping and React error boundaries.
- Security-scan policy validator, incremental checksummed migrations and CI.

## Validation
```powershell
npm test
npm run test:python
npm run build
npm run test:hybrid
npx playwright install chromium
npm run test:browser
```
Build now compiles the actual Next application. npm start runs the built frontend with FastAPI and still requires local environment configuration. npm run dev:legacy retains the original Node reference API/UI for compatibility work; it does not contain the new React report/error pages. Do not run two independent app compositions against the same database at once.

Browser smoke tests use temporary synthetic data, cover React workflows, CSV formula-prefix protection and viewport widths 360/390/768/1024/1440, and generate screenshots/print PDF in ignored artifacts/ui. No customer VPS is scanned or contacted. Python tests include direct Node-to-Python password/database/session compatibility.

## Remaining production work
MySQL adapter, complete V1 identity/2FA/password-reset integration, custom database roles, account lockout, production session/security review, multi-worker rate limits, VPS collectors, background scheduler, Google Drive backup/restore execution, license issuance, live pentest runners and opt-in central error collection. Accounting/HR adapters, monetary totals, XLSX, scheduled reports and AI report generation require actual domain requirements and data. Current reports cap output at 1000 records with an explicit warning; group counts cover returned records.

See docs/v3/DEVELOPMENT_PLAN.md, HYBRID_ARCHITECTURE.md, REPORTING_AND_ERRORS.md, AUTO_MANUAL.md, BACKUP_RECOVERY.md, LICENSING.md and SECURITY_TESTING.md. Target Git branch: v3-development at https://github.com/pharmacisttom/tomvis2.0.
