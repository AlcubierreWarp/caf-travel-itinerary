---
name: "caf-travel-itinerary-maintainer"
description: "Use when Tom asks to change, fix, release or push the CAF Digital Travel Itinerary (caf-travel-itinerary) beta or production, or says 'push to production'."
---

# Maintaining the CAF Digital Travel Itinerary

A browser-only tool: CAF members enter a TD itinerary, lodging, meals and expenses, attach receipts, and get one PDF package for the Orderly Room. Follow the caf-digital-tool-builder skill for principles. This skill covers the specifics of this app.

## Where things are
- **Repo:** `AlcubierreWarp/caf-travel-itinerary` (GitHub Pages, published by the Site action in `.github/workflows/site.yml`).
  - `main`: source, build and release scripts, tests, `VERSION`, `BETA_BUILD`. Read `CLAUDE.md` and `SOURCE.md` first.
  - Every push to `main` publishes the beta at `/beta/`.
  - Production is served from GitHub Release `vX.Y` (the exact files of that version), never rebuilt.
- **Artifact copy:** https://claude.ai/artifact/4UWaqjKN31YZgLJN9t3s82. Republish it from `out/travel-claim-packager.html` on every promotion, with a `Version X.Y` label.
- **Legal wording for AJAG review:** `docs/legal-wording-for-ajag-review.md` (master copy; the claude.ai doc https://claude.ai/artifact/BqVDd7XQjyfp5DYipR8sgQ mirrors it). Update it whenever declaration wording changes.
- **Contacts:** help and feedback emails go to Thomas.Huet@forces.gc.ca. The footer reads "(c) 2026 Thomas Huet". Tom built the tool on his own time and equipment.

## Starting over from nothing
If the Claude account or workspace is gone, follow `REBUILD.md`. It covers the GitHub Pages setup, local tools, folder layout, building, testing, releasing and restoring a release. Copies of this skill and caf-digital-tool-builder are in `docs/skills/`.

## Resuming in a new session
1. Attach the repo (add_repo with push access) and clone it. Work in the clone on `main`.
2. Run `pip install --break-system-packages playwright pillow pypdf` if missing. Then `python3 build.py .`.
3. Run the tests: `python3 test_beta.py .`, plus test_send, test_ios, test_names, test_notice, test_rail, test_ptr, test_fr, test_fr_more, test_modal and test_itin as relevant. Expect `errors: []`, `external requests: []` and `failures: []`. For service worker or storage changes also run `python3 release.py site _site` then `python3 test_live.py .` (local servers, upgrade check). Test leftovers (`fixtures/`, `shots/`) are ignored by git.

## Making a change
1. Edit `app/app.html`. Every new English string needs an entry in `app/fr.js` (test_fr fails otherwise). Put a change in `pwa/beta.css` (beta only) only if Tom calls it "beta-specific".
2. Run `python3 release.py beta`. It raises BETA_BUILD, builds and runs the channel check.
3. Test, and look at screenshots for visual changes.
4. Add a line under the "in progress" beta heading in `CHANGELOG.md`.
5. Commit with a message like "Beta X.Y build N: summary" and push `main`. The Site action publishes `/beta/` in a couple of minutes.
6. Confirm the Site run passed (`gh api repos/AlcubierreWarp/caf-travel-itinerary/actions/runs?per_page=1`).
7. Tell Tom the new label (e.g. 1.10 beta 11). He refreshes the installed beta app with pull to refresh.

## Push to production
Only when Tom says "release" or "push to production".
1. Run all tests.
2. Run `python3 release.py promote`. It raises VERSION, resets BETA_BUILD to 1, dates the changelog heading and adds the next "in progress" heading.
3. Commit ("Release X.Y to production") and push `main`. The Site action builds production once, files GitHub Release `vX.Y` with the site and the offline file (this creates the tag, so no tag is pushed by hand), commits the checksum to `README.md` and `CHANGELOG.md`, and publishes.
4. Pull, to pick up the checksum commit. Confirm the release exists and the live page shows the new version.
5. Republish the artifact.
6. If declaration wording changed, update `docs/legal-wording-for-ajag-review.md` and the claude.ai doc.
7. Tell Tom what is in the release. Installed apps update on their next online open.

To roll back: Actions, Site, Run workflow, with the version to put back (see `REBUILD.md`).

## Current beta-specific differences (keep unless Tom says otherwise)
- Greyscale icons, favicon and header logo (build.py inlines the logo; production's is in colour on a navy and blue theme).
- Grey launch and theme colour (#2b2b2b).
- "CAF Travel Beta" app name.
- Beta build label.
- `data-channel="beta"` marker.
- `pwa/beta.css`: violet colour theme (light and dark) in place of production's green, overriding the same `:root` tokens. Status colours (ok, warn, bad) are unchanged.
- `pwa/beta.css`: a Beta pill after the page title (Bêta in French), matching the import button's tag.
- Menu bottom (Beta testing, beta only): Load test data and Reset the beta, as code between `/*BETA-ONLY*/` and `<!--BETA-ONLY-->` markers that build.py strips from production. Put any future beta-specific script or markup inside those markers.

## Itinerary import (Amex GBT)
- Reader in `app/itin.js` (pure functions, inlined by build.py). pdf.js 3.11.174 is stored in the page as inert text and run on first import, no worker, no network.
- Fills section B, TAN and trip locator (shown only after an import), optional fare row, hotel stays, and the member's name (replacing an existing name only when ticked).
- Labelled Beta for users in both channels until Tom says otherwise.
- Never keep a real itinerary in the workspace or repo after use; tests build fictional ones.

## Statutory declarations
- Paragraphs come from `sdParts()`: 1 and 2 built (`sdParagraphs`/`sdParagraphsFr`) unless the member rewrote them (`sdP1`/`sdP2`, with the built text they replaced in `sdB1`/`sdB2` to flag later changes), an optional `sdMore` paragraph, then the reason and the two standard paragraphs (locked).
- Each editable paragraph is one paragraph (line breaks joined, typed numbers dropped), capped at 400 characters; the reason is capped at 200. `drawDeclaration` shrinks the paragraph text (to 7.5 pt at most) so the declaration stays on one page; `test_sdx.py` checks the longest case in both languages.

## Beautify export (experimental)
- Menu option `#opt-pretty`, a device preference (`caf-dti-pretty` + `CH`). When on, `build()` lays the package out with `prettyDraw()` (first page, sections, index and certification), `prettyRcHeader()` for receipt and declaration pages and `prettyFinish()` for the footer and marking. Off, nothing changes.
- The first page and index refer to later pages, so `build()` lays the designed worksheet out until its page count settles (up to 4 passes).
- Money tables share three trailing columns (`P.TRAIL`) and `P.band()`, so every subtotal and total lines up. Fallbacks: journey shows overnight places only (6 dots at most), meals by day (up to 7), by week (up to 35 days) or one row per day, second currencies listed apart, the page map is one mark per page. `test_pretty.py` covers them.
- Plain table cells are strings: test `typeof c === 'object'` before reading a cell option (`'x'.sub` is a String method).

## Gotchas
- Production and beta share an origin.
  - IndexedDB: `caf-dti-main` for production, `caf-dti` for beta.
  - Caches are named per scope.
  - localStorage is shared, so the beta suffixes its preference keys with `-beta` (`CH` in app.html: first-run seen, notice hidden, language, which falls back to production's). Reset the beta clears only those. Any new localStorage key must use `+ CH`.
- The installed iOS app keeps its home screen icon and storage. Reinstalling deletes kept claims, so tell Tom to save a draft file first.
- `test_beta.py` reads the production IndexedDB name (`caf-dti-main`).
- Do not pkill patterns that match your own shell. Kill test servers by PID.