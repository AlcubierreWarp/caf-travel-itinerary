# caf-travel-itinerary

The CAF Digital Travel Itinerary: a browser-only tool that helps CAF members prepare a temporary duty travel claim package. Used by CAF members; published on GitHub Pages.

Change model: Release.
- **Preview:** every push to `main` publishes the beta at `/beta/`. Changes go there first so the owner can test them.
- **Release:** production changes only when the owner says "release" or "push to production". Releasing is `python3 release.py promote`, then commit and push; the Site action builds that version once, files it as GitHub Release `vX.Y` (which also creates the tag) and serves those exact files from then on.

## Commands
- Build: `python3 build.py .`
- Check before every commit: `python3 release.py check`
- Test: `python3 test_beta.py .` and the other `test*.py` files that touch what changed (list in `REBUILD.md`); `python3 test_live.py .` for service worker or storage changes. Expect `errors: []`, `external requests: []`, `failures: []`.
- Next beta build: `python3 release.py beta`, add a changelog line, commit, push.
- Setup: `pip install playwright pillow pypdf` and `python3 -m playwright install chromium`.

## Where things live
- `app/app.html`: the whole app. `app/fr.js`: French text. `app/itin.js`: itinerary reader.
- `pwa/`: manifest, offline helper, icons, `beta.css` (beta-only styles).
- `build.py`, `release.py`: build and release. `.github/workflows/site.yml`: publishing.
- `test*.py`: Playwright tests.
- `docs/`: legal wording for review, and the two skill files that hold the working method (`docs/skills/`).
- `SOURCE.md`: orientation to the source. `REBUILD.md`: rebuilding from nothing but this repository.

## Conventions
- Every new or changed English string needs a French entry in `app/fr.js`.
- Beta-only code sits between the BETA-ONLY markers or in `pwa/beta.css`, and only when the owner calls a change "beta-specific".
- Every change adds a line under the "in progress" heading of `CHANGELOG.md`.
- No em dashes in text for users or the owner. Canadian English.

## Hard rules
- Never run `release.py promote`, change `VERSION`, tag or create a release until the owner says "release" or "push to production".
- A released version is never rebuilt or edited. Fixes go to the beta and out in the next release.
- No real personal data, itineraries or receipts in the repository, tests or fixtures.
- The app makes no network requests. Do not add any.
- This repository is public: keep personal details and secrets out of it.
