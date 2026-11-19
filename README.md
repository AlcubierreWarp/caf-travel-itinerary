# CAF Digital Travel Itinerary

A single-page tool that helps CAF members prepare a temporary duty travel claim.

Enter the trip itinerary, lodging, meals and expenses, attach receipt photos or PDFs, and the tool builds one PDF for the Orderly Room. The PDF contains the itinerary worksheet, totals by currency, a receipt index, every receipt labelled with its reference, and a DAOD 7000-1 statutory declaration for any receipt marked lost. Signature fields can be signed with a PKI certificate in Adobe Acrobat.

Leave taken during a trip can be recorded in the itinerary. Leave days stay on the trip record, but their meals are not claimed by default and no lodging is required for them.

## Privacy

Everything runs in the browser. The page has no server component and makes no network requests (a Content Security Policy in the page blocks them). Nothing you type or attach is uploaded.

By default a claim lasts only as long as the browser tab. In the menu you can choose **Keep my work on this device**, which stores the claim in this browser only, optionally encrypted with a PIN, and deletes it 30 days after the PDF is built. Use **Export claim file** (and **Import claim file** on the other device) to move a claim to another device.

## Use

- **Website:** open the published page. On a phone, use **Install app** in the menu (or Add to Home Screen on iPhone) to use it like an app, including offline.
- **Single file:** choose **Download offline copy** in the menu, or download `CAF_Digital_Travel_Itinerary.html` from this repository's [Releases page](https://github.com/AlcubierreWarp/caf-travel-itinerary/releases), and open it in any browser. It works with no internet connection and cannot make network requests at all.

The page opens with a fictional example claim; choose **Start a blank claim** to begin your own.

## Checksums

Only use an offline copy that you downloaded yourself from the published site or this repository's Releases page. If someone sends you one, check it first: its SHA-256 checksum must match the one below for its version, or the one shown in the app's menu under **Download offline copy**. A file that does not match may have been changed and should not be opened.

<!--CHECKSUMS-->
| Version | File | SHA-256 |
| --- | --- | --- |
| 1.10 | `CAF_Digital_Travel_Itinerary.html` | `a761b445b21eb47a2a4ed3b3be9a240781c421223f9d3703513c6fc2335edfd9` |
<!--/CHECKSUMS-->

This table shows the current production version. Checksums for both the production and beta files as published right now are at [checksums.txt](https://alcubierrewarp.github.io/caf-travel-itinerary/checksums.txt). Each release's file and checksum are also kept on the [Releases page](https://github.com/AlcubierreWarp/caf-travel-itinerary/releases).

To get a file's checksum:

- **Windows (PowerShell):** `Get-FileHash .\CAF_Digital_Travel_Itinerary.html`
- **macOS (Terminal):** `shasum -a 256 CAF_Digital_Travel_Itinerary.html`
- **Linux:** `sha256sum CAF_Digital_Travel_Itinerary.html`

The checksum of each production release is also listed in `CHANGELOG.md`.

## Beta

The next version is tested at `/beta/`. It keeps its own saved claims and offline copy, separate from the main site, and installs as **CAF Travel Beta**.

## Status

Unofficial prototype for testing and feedback. It is not an official DND/CAF application and does not calculate entitlements. Check all claims against current CFTDTI and Orderly Room direction.

## Versions

The version number is shown at the bottom of the page and in help emails. See `CHANGELOG.md`.

## Source and rebuilding

This repository holds the source, the build and release scripts, the tests and the documentation. A GitHub Action builds the site: the beta from `main` on every change, and production from each release. To rebuild or keep developing the app from nothing but this repository, follow `REBUILD.md`. Every production release is kept on the Releases page with the exact files that were published.

## Third-party code

pdf-lib (MIT License) and pdf.js (Apache License 2.0) are bundled inside the published page and `CAF_Digital_Travel_Itinerary.html`. See `THIRD_PARTY_NOTICES.md`.
