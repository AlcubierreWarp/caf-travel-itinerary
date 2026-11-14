"""Release helper for the CAF Digital Travel Itinerary.

    python3 release.py check        build, then check that nothing beta-only reached production
    python3 release.py beta         raise BETA_BUILD for the next beta build
    python3 release.py promote      beta becomes production: raise VERSION, reset BETA_BUILD, date the changelog
    python3 release.py site DIR     put the whole published site in DIR (the Site action runs this)

Nothing here commits or pushes. After `beta` or `promote`, commit and push to main; the Site
action (.github/workflows/site.yml) publishes it. How publishing works:

  - /beta/ is built from main on every push.
  - Production is the version named in VERSION. The first time the action sees a version, it builds
    it once, files the result as GitHub Release vX.Y (site.zip and the offline file) and records
    its checksum in README.md and CHANGELOG.md. Every later publish serves those same files, so a
    released version never changes.
Run the tests before pushing. See REBUILD.md."""
import sys, os, re, subprocess, shutil, pathlib, datetime, zoneinfo, hashlib, zipfile, tempfile
S = pathlib.Path(__file__).resolve().parent
REPO = os.environ.get("GITHUB_REPOSITORY", "AlcubierreWarp/caf-travel-itinerary")
OFFLINE = "CAF_Digital_Travel_Itinerary.html"
def run(*a, check=True): return subprocess.run(a, cwd=S, check=check, capture_output=True, text=True)
def read(name): return (S / name).read_text().strip()
def sha(f): return hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()
def build(): print(run(sys.executable, "build.py", ".").stdout.strip().splitlines()[-1])

def check():
    """Stop if anything beta-only reached production, or the beta lost its markers."""
    from PIL import Image
    prod = (S / "out/web/index.html").read_text(); beta = (S / "out/web-beta/index.html").read_text()
    single = (S / "out" / OFFLINE).read_text(); art = (S / "out/travel-claim-packager.html").read_text()
    for name, doc in (("production", prod), ("single file", single), ("artifact", art)):
        bad = [m for m in ('data-channel="beta"', 'id="beta-only"', "CAF Travel Beta", "APP_CHANNEL = 'beta'", "BETA-ONLY", "beta-reset", "loadTestData") if m in doc]
        if re.search(r"APP_VERSION = '[^']*beta", doc) or re.search(r"Version [0-9.]+ beta", doc): bad.append("beta version label")
        assert not bad, f"beta-only content in {name}: {bad}"
    assert "Beta" not in (S / "out/web/manifest.webmanifest").read_text(), "beta name in production manifest"
    im = Image.open(S / "out/web/icon-192.png").convert("RGB").resize((24, 24))
    assert max(max(p) - min(p) for p in zip(*[iter(im.tobytes())] * 3)) > 40, "production icon is not in colour"
    for m in ('data-channel="beta"', 'id="beta-only"', "APP_CHANNEL = 'beta'", 'data-act="beta-reset"', "async function loadTestData"):
        assert m in beta, f"beta build is missing {m}"
    css = (S / "pwa/beta.css").read_text()
    assert css.count("/*") == css.count("*/"), "pwa/beta.css: a comment opener or closer inside a comment would hide the beta theme"
    print("channel check ok")

def record(ver, digest):
    """Write a released version's offline file checksum into the README table and under its changelog heading."""
    rd = S / "README.md"; txt = rd.read_text()
    assert "<!--CHECKSUMS-->" in txt and "<!--/CHECKSUMS-->" in txt, "README.md has no checksum markers"
    rows = ["| Version | File | SHA-256 |", "| --- | --- | --- |", f"| {ver} | `{OFFLINE}` | `{digest}` |"]
    rd.write_text(re.sub(r"<!--CHECKSUMS-->.*?<!--/CHECKSUMS-->", "<!--CHECKSUMS-->\n" + "\n".join(rows) + "\n<!--/CHECKSUMS-->", txt, flags=re.S))
    cl = S / "CHANGELOG.md"; c = cl.read_text()
    m = re.search(r"^## " + re.escape(ver) + r" \([^)]*\)\n\n", c, flags=re.M)
    assert m, f"CHANGELOG.md has no heading for {ver}"
    line = f"- Offline file SHA-256: `{digest}`\n"
    if line not in c: cl.write_text(c[:m.end()] + line + c[m.end():])

def make_release(ver, target, folder, names):
    """File a production build as GitHub Release vX.Y, so it is served unchanged from now on."""
    with tempfile.TemporaryDirectory() as t:
        z = pathlib.Path(t) / "site.zip"
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for n in sorted(names): zf.write(folder / n, n)
        digest = sha(folder / OFFLINE)
        run("gh", "release", "create", f"v{ver}", "--repo", REPO, "--target", target, "--title", f"Version {ver}",
            "--notes", f"Production release {ver}. See CHANGELOG.md for what changed.\n\nOffline file `{OFFLINE}` SHA-256: `{digest}`",
            str(z), str(folder / OFFLINE))
    print(f"filed release v{ver} at {target[:10]}")

def site(dest):
    """Production from its release (never rebuilt), the beta from this build, and the checksums."""
    dest = pathlib.Path(dest).resolve(); shutil.rmtree(dest, ignore_errors=True); dest.mkdir(parents=True)
    current = read("VERSION"); ver = os.environ.get("PROD_VERSION") or current
    publish = os.environ.get("PUBLISH") == "1"
    names = [f.name for f in (S / "out/web").iterdir()]
    with tempfile.TemporaryDirectory() as t:
        got = run("gh", "release", "download", f"v{ver}", "--repo", REPO, "--pattern", "site.zip", "--dir", t, check=False)
        # an older version with no filed release: its restore point, a release-vX.Y branch or (once converted) the tag vX.Y
        branch = (run("git", "rev-parse", "--verify", "-q", f"origin/release-v{ver}^{{commit}}", check=False).stdout.strip()
                  or run("git", "rev-parse", "--verify", "-q", f"refs/tags/v{ver}^{{commit}}", check=False).stdout.strip())
        if got.returncode == 0:
            zipfile.ZipFile(pathlib.Path(t) / "site.zip").extractall(dest); origin = "its release"
        elif branch:  # a version released before releases were filed: take it from its restore branch
            for n in names: (dest / n).write_bytes(subprocess.run(["git", "show", f"{branch}:{n}"], cwd=S, check=True, capture_output=True).stdout)
            origin = f"restore point for {ver}"
            if publish: make_release(ver, branch, dest, names)
        elif ver == current:  # a new version: this build is the release
            for n in names: shutil.copy(S / "out/web" / n, dest / n)
            origin = "this build (new release)"
            if publish: make_release(ver, os.environ.get("GITHUB_SHA") or run("git", "rev-parse", "HEAD").stdout.strip(), dest, names)
        else:
            sys.exit(f"There is no release v{ver} to publish.")
    prod = sha(dest / OFFLINE)
    if publish and ver == current: record(ver, prod)
    shutil.copytree(S / "out/web-beta", dest / "beta")
    for f in ("CHANGELOG.md", "THIRD_PARTY_NOTICES.md"): shutil.copy(S / f, dest / f)
    (dest / ".nojekyll").write_text("")
    maj, mi = current.split("."); beta = sha(dest / "beta" / OFFLINE)
    (dest / "checksums.txt").write_text(
        "SHA-256 checksums of the offline files published here\n\n"
        f"Production, version {ver}\n{prod}  {OFFLINE}\n\n"
        f"Beta, version {maj}.{int(mi) + 1} beta {read('BETA_BUILD')}\n{beta}  beta/{OFFLINE}\n")
    print(f"site ready in {dest.name}: production {ver} from {origin} ({prod[:12]}), beta {beta[:12]}")

def beta():
    n = int(read("BETA_BUILD") or 0) + 1; (S / "BETA_BUILD").write_text(f"{n}\n")
    build(); check()
    maj, mi = read("VERSION").split(".")
    print(f"Next: commit and push to main. The beta will show {maj}.{int(mi) + 1} beta {n}.")

def promote():
    maj, mi = read("VERSION").split("."); new = f"{maj}.{int(mi) + 1}"; nxt = f"{maj}.{int(mi) + 2}"
    cl = S / "CHANGELOG.md"; c = cl.read_text(); head = f"## {new} (beta, in progress)"
    assert head in c, f'CHANGELOG.md has no "{head}" heading to release'
    today = datetime.datetime.now(zoneinfo.ZoneInfo("America/Moncton")).strftime("%d %b %Y")
    cl.write_text(c.replace(head, f"## {nxt} (beta, in progress)\n\n## {new} ({today})", 1))
    (S / "VERSION").write_text(new + "\n"); (S / "BETA_BUILD").write_text("1\n")
    build(); check()
    print(f"Next: commit and push to main. That releases {new} to production; the beta becomes {nxt} beta 1.")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "check": build(); check()
    elif mode == "beta": beta()
    elif mode == "promote": promote()
    elif mode == "site": site(sys.argv[2] if len(sys.argv) > 2 else "_site")
    else: sys.exit(__doc__)
