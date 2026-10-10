# Automatic user manuals

Implemented for the current framework application. Every registered module must supply `guide` entries with unique ID, title, required permissions and plain-text steps. Application composition (`apps/manual-registry.js`) passes platform and module metadata to the domain-neutral generator; core does not import business modules.

`npm run build` automatically runs `docs:generate` and produces `docs/generated/USER_MANUAL.md`. Missing/invalid guide metadata fails generation. The authenticated `/api/v1/manual` endpoint assembles the manual from the same registry and filters sections by backend permissions. All signed-in users have the คู่มือการใช้งาน sidebar menu with searchable, safely escaped instructions. Shared getting-started sections require no additional permission.

For each new app, its scaffold must register its actual modules and platform sections in the registry, include the shared manual endpoint/sidebar, and keep the prebuild generation hook. The future create-tomvis-app CLI is not implemented yet. Arbitrary apps outside this framework do not acquire a manual automatically.

Generation assembles module-authored instructions; it does not infer correct workflows from arbitrary code or invent undocumented features. Authors update guide metadata with feature changes and review it against actual UI. Guides for planned features must not be presented as operational instructions. Screenshots, contextual page help, localization and package-entitlement filtering will be integrated after those systems exist.

Tests cover missing/duplicate documentation, role filtering and authenticated API behavior. Browser rendering remains unverified due to the previously reported local browser-tool failure.
