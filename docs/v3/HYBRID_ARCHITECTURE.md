# Python + Next.js/React integration

The active local application now runs Next.js/React at the browser origin and FastAPI on loopback. Next route handlers proxy only the fixed configured backend origin. They forward cookies and browser Origin without establishing identity or accepting client-provided tenant/role headers. Python owns identity, membership/permission checks, business API, reports, audit and error records. No CORS wildcard or browser token storage is used.

Existing alpha passwords (Node scrypt format), hashed opaque sessions, SQLite data and migration checksums remain compatible. Shared generated JSON contracts contain versioned migrations, role catalog and module-authored manuals; no customer records or secrets. Python does not require a Node API process. The legacy Node app is available only through `dev:legacy` for compatibility testing; do not run both applications as competing writers or independent identity services.

Python is appropriate for data processing, reporting and future backup/monitoring workers. React handles interactive screens and Next supplies the browser application, build and API facade. Durable background workers and MySQL persistence are still pending; the local synchronous SQLite adapter is not a production architecture claim. Production/staging continue to fail closed.

Run `npm ci`, create `.venv` with Python 3.12, install `apps/api/requirements.txt`, set `TOMVIS_DEMO_PASSWORD` and run `npm run dev`. Ports default to 3000 frontend and 8000 backend. Use the exact configured `TOMVIS_PUBLIC_ORIGIN` (default http://localhost:3000); Origin validation rejects other browser origins. `TOMVIS_PYTHON` can name another installed interpreter. `TOMVIS_API_PORT` configures the loopback API port. `npm start` uses a previously built Next bundle and still requires both runtimes.

Validation: `npm test` (legacy/core), `npm run test:python`, `npm run build` (actual Next production compilation), `npm run test:hybrid` (real HTTP through Next using temporary synthetic data), `npm run test:browser` (Chromium React workflows, CSV, responsive widths and print PDF). Install browser binaries with `npx playwright install chromium` first. Local browser checks pass at 360/390/768/1024/1440; comprehensive accessibility, multi-page print review and live MySQL tests remain pending. Test screenshots/PDF live under ignored `artifacts/ui` and contain only synthetic fixtures.

References: https://nextjs.org/docs/app/guides/backend-for-frontend ; https://fastapi.tiangolo.com/tutorial/testing/
