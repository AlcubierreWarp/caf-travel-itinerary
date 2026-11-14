# Rebuilding the CAF Digital Travel Itinerary from scratch

This guide assumes nothing survives except this GitHub repository: no Claude account, no Claude skills or memory, no earlier workspace. Everything needed to rebuild, test, publish and keep developing the app is in the repository.

## 1. What is in the repository

Everything is on the `main` branch: the source, the build and release scripts, the tests and the documents. The published site is not stored in a branch. A GitHub Action builds it and publishes it to GitHub Pages.

| Where | What it holds |
| --- | --- |
| `main` | Everything needed to build and publish the site. Every push publishes the beta at `/beta/`. |
| Releases page | One release per production version, tagged `vX.Y`, with `site.zip` (the exact production site as published) and the offline single file. Production is always served from these files, never rebuilt. |
| `release-v1.0` to `release-v1.9`, `prod-v1.0-final` | Older copies of the published site from before releases were filed (kept as tags once converted). Version 1.9 was filed as a release from `release-v1.9`. |
| `source` | The old home of the source, before it moved to `main`. Its history is part of `main`. |

In the repository:
On the `source` branch:

| Path | Purpose |
| --- | --- |
| `app/app.html` | The whole app: markup, styles and script. Edit this. All text is English, passed through `T()`. |
| `app/fr.js` | French text (Government of Canada usage), keyed by the English text. |
| `app/itin.js` | Amex GBT itinerary reader (pure functions). |
| `pwa/` | Manifest, offline helper `sw.js`, icons, `beta.css` (beta-only styles), `make_icons.py` and the icon artwork in `pwa/src/`. |
| `npm/node_modules/...` | Pinned copies of pdf-lib 1.17.1 (MIT) and pdf.js 3.11.174 (Apache-2.0), with their licences. |
| `build.py` | Builds production, beta, the offline single file and the claude.ai copy into `out/`. |
| `release.py` | Raises the beta build, promotes beta to production, runs the channel check, and assembles the published site for the Site action. |
| `.github/workflows/site.yml` | The Site action: builds and publishes to GitHub Pages. |
| `CLAUDE.md`, `.claude/settings.json` | Working rules and settings for Claude Code sessions in this repository. |
| `msgfile.py` | Writes small fictional Outlook .msg files for `test_itin.py`. |
| `serve_cached.py` | Local web server that sends GitHub's caching header, for the service worker tests. |
| `test*.py` | Playwright tests. |
| `VERSION`, `BETA_BUILD` | Current production version and beta build number. |
| `SOURCE.md` | Short orientation to the source. |
| `docs/legal-wording-for-ajag-review.md` | Statutory declaration wording drafted for the tool, with its basis, for AJAG review. Master copy. |
| `docs/skills/` | The two Claude skills that hold the working method and the app's specifics (see section 9). |

## 2. Accounts and settings

- **GitHub:** the repository `AlcubierreWarp/caf-travel-itinerary`. If it ever has to be recreated, push `main` and the tags to the new repository, and upload each release's `site.zip` and offline file again (or at least the current version's).
- **GitHub Pages:** Settings, Pages, Source: "GitHub Actions". The Site action publishes on every push to `main`. No custom domain is used.
- **Contacts written into the app:** help and feedback emails go to Thomas.Huet@forces.gc.ca. The footer reads "© 2026 Thomas Huet". Change them in `app/app.html` if needed.

The app has no server, database or analytics. Members' claims live only in their own browsers, so there is no user data to back up or restore.

## 3. Tools on your computer

- Git.
- Python 3.11 or newer (the build uses `zoneinfo` with the America/Moncton time zone; on Windows also run `pip install tzdata`).
- Python packages: `pip install playwright pillow pypdf`
- A browser for the tests: `python -m playwright install chromium`
- `pdftoppm` (poppler) is optional, for looking at PDF pages as images.
- Node.js is only needed to update the bundled libraries (section 10).

## 4. Folder layout

One clone is all you need. You edit, build and test in it, and push `main`.

```
git clone https://github.com/AlcubierreWarp/caf-travel-itinerary.git
cd caf-travel-itinerary
```

Build output (`out/`, `_site/`) and test leftovers are ignored by git.

## 5. Build

```
python build.py .
```

It writes:

- `out/web/` production site as it would be released from this commit, with its offline file
- `out/web-beta/` beta site (published at `/beta/`), with its own offline file
- `out/checksums.json` the SHA-256 of each offline file. Each page shows its own offline file's checksum in the menu; the offline files show none, since a file cannot hold its own checksum
- `out/CAF_Digital_Travel_Itinerary.html` offline single file
- `out/travel-claim-packager.html` copy for a claude.ai artifact (optional)

The date stamp in the page is the current time, or the time of the commit when `SOURCE_DATE_EPOCH` is set (the Site action sets it), so the same commit always gives the same files and checksums. A clean clone rebuilds the live beta exactly; this was last confirmed on 14 Nov 2026 for beta 1.10 beta 10. Production is not rebuilt: it is served from its release.

## 6. Test

Run from the clone:

```
python test_beta.py .
python test.py .
python test_send.py .
python test_ios.py .
python test_names.py .
python test_notice.py .
python test_rail.py .
python test_ptr.py .
python test_fr.py .
python test_fr_more.py .
python test_modal.py .
python test_itin.py .
python test_swipe_vis.py .
python test_offline_copy.py .
python test_fileno.py .
python test_pdfver.py .
python test_savenow.py .
python test_switch.py .
python test_sdx.py .
python test_split.py .
python test_betatools.py .
python test_theme.py .
python test_crop.py .
python test_autocrop.py .
python test_pretty.py .
python test_leave.py .
python test_menu.py .
python test_checksum.py .
```

Each prints `errors: []`. Tests that check privacy also print `external requests: []`, and the newer ones print `failures: []`. `test_fr.py` also prints `missing: []` (no untranslated text). Delete the `fixtures/` and `shots/` folders afterwards.

The service worker tests (`test_channels.py`, `test_offline.py`, `test_ptr_live.py`, `test_upgrade.py`) need local web servers that cache like GitHub Pages. Run them together with:

```
python test_live.py .
```

It copies the built sites into `live/`, starts `serve_cached.py` on ports 8765 to 8767, runs the four tests and stops the servers. `test_upgrade.py` starts from the released production site in `_site/` and upgrades it to your new build, checking that a member's saved claim survives. Make `_site/` first with `python release.py site _site` (it downloads the current release with the `gh` tool). The tests use `localhost`, because service workers do not register on 127.0.0.1.

Never put real personal data in tests or fixtures. `test_itin.py` builds fictional itineraries every time it runs.

## 7. Release

Beta (every change):

1. Edit `app/app.html`. Add a French entry to `app/fr.js` for every new English string.
2. `python release.py beta` raises `BETA_BUILD`, builds and checks that nothing beta-only reaches production.
3. Run the tests and look at screenshots of anything visual.
4. Add a line under the "in progress" heading of `CHANGELOG.md`.
5. Commit and push `main`. The Site action publishes the beta at `/beta/` within a couple of minutes.

Production ("push to production"):

1. Run all the tests.
2. `python release.py promote` raises the minor version in `VERSION`, resets `BETA_BUILD` to 1, dates the beta heading in `CHANGELOG.md` and adds a new "in progress" heading for the next version.
3. Commit and push `main`. The Site action sees a version with no release yet, so it builds production once, files it as GitHub Release `vX.Y` (this creates the tag) with `site.zip` and the offline file, writes the checksum into `README.md` and `CHANGELOG.md` in a commit of its own, and publishes. Pull afterwards to get that commit.

A released version is never rebuilt. Every later publish downloads that release's `site.zip`, so the production files and their checksum stay exactly as released.

Version labels: production shows `Version X.Y, updated DD Mon YYYY`; the beta shows `Version X.(Y+1) beta N, built ... (production is X.Y)`. The minor number goes up only on promotion; the owner decides major versions.

## 8. Roll back production

On GitHub: Actions, Site, "Run workflow", and enter the version to put back (for example `1.9`). Production is served from that release until the workflow is run again with the field empty, or until the next push to `main`. To stay on the older version, also set `VERSION` back and push.

Versions before 1.9 have no filed release; the workflow takes them from their restore point, the tag `vX.Y` (formerly the branch `release-vX.Y`), and files a release from it.

## 9. Working with Claude again

The working method lives in two skill files in `docs/skills/`:

- `caf-digital-tool-builder/SKILL.md`: principles for any small CAF tool (local only, no real personal data, file naming, security markings, bilingual text, phone lessons, testing, release discipline, Tom's writing preferences).
- `caf-travel-itinerary-maintainer/SKILL.md`: this app's specifics (repository layout, release steps, beta-only differences, the itinerary import, known pitfalls).

In a new Claude account, add both as skills, or attach them at the start of a conversation and ask Claude to follow them. Then give Claude access to this repository and point it at this file.

Owner rules worth repeating:

- Changes go to the beta. Production changes only when the owner says "release" or "push to production".
- Only changes the owner calls "beta-specific" go in the beta-only layer (`pwa/beta.css`, beta build settings in `build.py`). Today these are: greyscale icons and header logo, grey launch colour, the "CAF Travel Beta" name, the beta version label, the violet colour theme, the Beta pill after the page title, and the Load test data and Reset the beta tools in the menu (code between BETA-ONLY markers, removed from production by build.py).
- Statutory declaration wording that is not from an official source is listed in `docs/legal-wording-for-ajag-review.md`. Update it whenever that wording changes.

## 10. Updating the bundled libraries

```
npm pack pdf-lib@1.17.1 pdfjs-dist@3.11.174
```

Unpack each `.tgz` and copy `package/dist/pdf-lib.min.js`, `package/LICENSE.md`, `package/build/pdf.min.js`, `package/build/pdf.worker.min.js` and `package/LICENSE` into the matching `npm/node_modules/...` paths. `build.py` refuses a library that contains `</script`, `<!--` or the U+FFFD character, because the page inlines them. A new pdf.js version must still offer the global `pdfjsWorker` fake-worker path (the 3.x series does); test `test_itin.py` after any change.

## 11. Things that are not in the repository

- The claude.ai artifact copy of the app and the claude.ai doc of the legal wording. Both can be recreated from the repository (`out/travel-claim-packager.html` and `docs/legal-wording-for-ajag-review.md`).
- Claude conversation history and memory. Nothing in them is needed to rebuild.
- Real itineraries or receipts. They are never kept.
