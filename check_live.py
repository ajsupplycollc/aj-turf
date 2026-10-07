# Exits 0 only if every public page of the live AJ Turf site returns 200.
import sys, urllib.request
BASE = "https://ajsupplycollc.github.io/aj-turf/"
PATHS = ["", "artificial-turf-installation/", "pet-turf/", "putting-greens/", "pool-and-paver-turf/", "turf-repair/",
         "fort-myers/", "cape-coral/", "naples/", "estero/", "bonita-springs/", "sanibel/", "privacy/",
         "sitemap.xml", "robots.txt", "llms.txt", "img/og/home.jpg"]
bad = []
for p in PATHS:
    try:
        code = urllib.request.urlopen(BASE + p, timeout=20).status
    except Exception as e:
        code = getattr(e, "code", str(e))
    if code != 200:
        bad.append((p, code))
print("ALL 200" if not bad else f"FAIL {bad}")
sys.exit(1 if bad else 0)
