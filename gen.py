# Generates service + city pages, sitemap, robots, llms.txt for the AJ Turf site.
# Run: python gen.py   (home page index.html is hand-built; this only writes the rest)
import json, os, datetime, re, html
from PIL import Image

BASE = "https://ajturffl.com/"  # ponytail: swap to the real domain when it exists
PHONE, PHONE_HREF = "305-762-9901", "+13057629901"
EMAIL = "ajturffl@gmail.com"
PUBLISH_GUIDE = True   # flip to True when Jereme approves the Turf Guide
BOOK = "https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ2DTv90ZIlO1yxFsxeEcVhJxtTSvLrjRpB3xc9llHbTBaQ1nFWr8KTX7mevE-Gx56R-V1wuX7ax"
TODAY = datetime.date.today().isoformat()
AREAS = ["Fort Myers", "Cape Coral", "Naples", "Estero", "Bonita Springs", "Sanibel", "Lehigh Acres", "Marco Island"]

# YouTube videos (@AJTurf). Thumbs are self-hosted crops in img/vid/; add new uploads here, then to a page or OUR_WORK.
# id: (YouTube title, schema description, seconds, upload date, vertical?, card caption)
VIDEOS = {
 "4j__CUFYhnQ": ("Whole-Yard Artificial Turf Transformation — Finished Property Tour", "A full walkthrough of a finished whole-property artificial turf install: front yard, both side yards and around the pool.", 134, "2026-10-09", True, "Whole-property tour · front, sides, pool"),
 "3yovFZ8U0ns": ("Artificial Turf Lawn Walkthrough in Fort Myers, FL", "A finished AJ Turf lawn in Fort Myers, Florida: curved lawn, palms and planters, no mowing or watering.", 12, "2026-10-08", False, "Fort Myers · finished lawn"),
 "IhduTxos9As": ("My First Job: Building a Backyard Putting Green Start to Finish", "A backyard putting green filmed day by day across seven visits, from the bare yard through excavation, base and weed barrier to the finished green.", 549, "2026-10-08", True, "Putting green · start to finish"),
 "aATUhfArpEY": ("The AJ Method: How We Install Artificial Turf", "Jereme walks through the AJ Turf install method on a real Florida Keys job: excavation, base compaction, weed barrier and the turf going down.", 138, "2026-10-08", True, "The AJ Method · on a real job"),
 "LgpH3u-eJ6A": ("Duck Key, FL Project Walkthrough — Whole-Property Turf & Landscaping", "A canal-front, whole-property turf and landscaping project in progress in Duck Key, in the Florida Keys.", 32, "2026-10-08", True, "Duck Key · canal-front, in progress"),
 "HgPybt3IXWA": ("Coral Gables, FL Project Recap: New Fence, Privacy Hedges & Finished Turf", "A full-property recap in the Coral Gables area: new chain-link fence, a Clusia privacy hedge and finished artificial turf.", 53, "2026-10-08", True, "Coral Gables · fence, hedge, turf"),
}

# Every upload on the AJ Turf channel lands on /videos/ automatically: the build reads the channel's public feed,
# adds new ids to VIDEOS (title, description, date, short/long, length, thumbnail), and caches them in videos_cache.json
# so a build with no network still renders. ponytail: feed = the newest 15 uploads; older ones live on in the cache.
import json as _json, urllib.request as _ur, html as _html
CHANNEL = "UCu5g85tvUUTuOrH4CoHcimQ"
def _get(url):
    return _ur.urlopen(_ur.Request(url, headers={"user-agent": "Mozilla/5.0"}), timeout=30).read()
def sync_videos():
    try: cache = _json.load(open("videos_cache.json", encoding="utf-8"))
    except Exception: cache = {}
    try:
        feed = _get(f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL}").decode("utf-8")
        for e in re.findall(r"<entry>(.*?)</entry>", feed, re.S):
            v = re.search(r"<yt:videoId>(.*?)<", e).group(1)
            if v in VIDEOS or v in cache: continue
            title = _html.unescape(re.search(r"<title>(.*?)<", e).group(1)).split(" | ")[0]
            desc = _html.unescape((re.search(r"<media:description>(.*?)</media:description>", e, re.S) or [None, ""])[1]).strip().split("\n")[0][:300] or title
            tall = "/shorts/" in e
            try: sec = int(re.search(rb'"lengthSeconds":"(\d+)"', _get(f"https://www.youtube.com/watch?v={v}")).group(1))
            except Exception: sec = 0
            cache[v] = [title, desc, sec, re.search(r"<published>(\d{4}-\d\d-\d\d)", e).group(1), tall, title.split(" — ")[0]]
        _json.dump(cache, open("videos_cache.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    except Exception as ex:
        print("video feed skipped:", ex)
    for v, row in cache.items():
        VIDEOS.setdefault(v, tuple(row))
    from PIL import Image
    import io
    for v, row in VIDEOS.items():  # local thumbnail for every video (YouTube's own frame), so pages don't hotlink
        out = f"img/vid/{v}.webp"
        if os.path.exists(out): continue
        for name in (["oardefault", "hqdefault"] if row[4] else ["maxresdefault", "hqdefault"]):
            try: im = Image.open(io.BytesIO(_get(f"https://i.ytimg.com/vi/{v}/{name}.jpg"))).convert("RGB"); break
            except Exception: im = None
        if im is None: continue
        if row[4] and im.width > im.height:  # letterboxed short: keep the centre 9:16
            w = round(im.height * 9 / 16); im = im.crop(((im.width - w) // 2, 0, (im.width + w) // 2, im.height))
        im.thumbnail((720, 720)); im.save(out, quality=80)
sync_videos()

# Duck Key stitch: mid-install, rotated, no payoff (Jereme via Muse 10/16): off every page.
HIDDEN = {"LgpH3u-eJ6A"}
OUR_WORK = ["4j__CUFYhnQ", "3yovFZ8U0ns", "IhduTxos9As", "aATUhfArpEY", "HgPybt3IXWA", "v2eITlM3ujc", "EF2Vn8CENRE", "zzQ96jgy13k"]
CITY_VIDEOS = {"Fort Myers": (["3yovFZ8U0ns"], "A finished Fort Myers <b>lawn.</b>")}  # geo-matched only: the video's city = the page's city
SERVICE_VIDEOS = {"putting-greens": (["IhduTxos9As", "zzQ96jgy13k"], "Watch one <b>go in.</b>"), "pool-and-paver-turf": (["gwrSbYCwsoA"], "A pool surround, <b>on the job.</b>"),
                  "pet-turf": (["VXatdDEOrdw"], "A rooftop dog run, <b>on video.</b>"), "artificial-turf-installation": (["aATUhfArpEY"], "The method, <b>on a real job.</b>"),
                  "turf-repair": (["aATUhfArpEY"], "How we <b>rebuild it.</b>")}
# a service video sits right after this section (default: after the first)
SERVICE_VIDEO_AFTER = {"artificial-turf-installation": "How we <b>build it.</b>", "turf-repair": "How we <b>rebuild.</b>"}

# 4: video -> its job page (matched by place + job; unmatched videos get no link)
VIDEO_JOB = {"G8VQdQvdHKs": "work/marathon-resort-lawn-and-pool", "qcrd7AaRggQ": "work/marathon-waterfront-lawn", "VXatdDEOrdw": "work/key-largo-rooftop-dog-run",
 "KCdGos73yv8": "work/west-palm-beach-rooftop-terrace", "XV1PvYFIxKY": "work/west-palm-beach-rooftop-terrace", "E4Mxf-pbMyY": "work/south-miami-driveway-turf-strips",
 "IhduTxos9As": "work/boynton-beach-putting-green-build", "70gmWscveDg": "work/long-key-50-ft-putting-green", "XeKvGsyuBuI": "work/lower-matecumbe-canal-lawn",
 "bs1ThPgmBGQ": "work/hialeah-gardens-front-yard-putting-green", "Ak-UVF63S1g": "putting-greens", "U7XIJkDtIYs": "work/dogs-on-pet-turf", "ajRINxB-_YQ": "work/miami-front-yard-lawn"}
def vcard(v, r, job=False):
    t, _, _, _, tall, cap = VIDEOS[v]
    return (f'<figure class="vid{"" if tall else " wide"}"><button class="yt" data-id="{v}" data-title="{t}" aria-label="Play video: {t}">'
            f'<img src="{r}img/vid/{v}.webp" alt="{_html.escape(cap)}" loading="lazy"><span class="play"></span></button><figcaption class="cap mono">{cap}</figcaption>' + (f'<a class="vid-job mono" href="{r}{VIDEO_JOB[v]}/">See this job →</a>' if v in VIDEO_JOB and job else "") + '</figure>')

def vcta():
    return f'<p class="vid-cta"><a class="book" href="{BOOK}" target="_blank" rel="noopener">Book a free estimate <span aria-hidden="true">→</span></a><a class="alt mono" href="tel:{PHONE_HREF}">Or call {PHONE}</a><a class="alt mono" href="sms:{PHONE_HREF}">Or text us</a></p>'

def vblock(ids, r, h2):
    # no orphan video: the booking CTA sits directly under every player
    return (f'<section class="work"><header><h2>{h2}</h2></header><div class="strip">' + "".join(vcard(v, r) for v in ids) + "</div>" + vcta() + "</section>")

def vobj(v):
    t, d, s, date, _, _ = VIDEOS[v]
    return {"@type": "VideoObject", "name": t, "description": d, "thumbnailUrl": BASE + f"img/vid/{v}.webp", "uploadDate": date,
            **({"duration": f"PT{s // 60}M{s % 60}S"} if s else {}), "embedUrl": f"https://www.youtube.com/embed/{v}"}

HOME_VIDEOS = ["4j__CUFYhnQ", "3yovFZ8U0ns", "aATUhfArpEY", "v2eITlM3ujc"]  # embedded by hand in index.html
PAGE_VIDEOS = {"": HOME_VIDEOS}  # path -> video ids, for the video sitemap

import photo_content as PC
SRC = ["../website-photos-processed/{}.jpg", "../website-photos/hero/hero-{}.jpg", "../website-photos/raw/{}.jpg", "../website-photos/greens/{}.jpg"]
def pfile(i):
    # right-sized webp, built once: 800w always, 1600w when the source is big enough (the 2400px hero pulls)
    out = f"img/p/{i}-800.webp"
    if not os.path.exists(out):
        src = next(x.format(i) for x in SRC if os.path.exists(x.format(i)))
        im = Image.open(src).convert("RGB"); os.makedirs("img/p", exist_ok=True)
        for w in (800, 1600):
            if w == 800 or im.width >= 1600:
                im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(f"img/p/{i}-{w}.webp", quality=78)
    im = Image.open(out); big = os.path.exists(f"img/p/{i}-1600.webp")
    return im.width, im.height, big

def fig(item, r):
    if isinstance(item, tuple) and item[0] != "pair":  # an existing site image: (slug, alt, caption)
        i, a, c = item; im = Image.open(f"img/{i}.webp")
        return f'<figure class="{"wide" if im.width > im.height else ""}"><img src="{r}img/{i}.webp" alt="{a}" width="{im.width}" height="{im.height}" loading="lazy"><figcaption class="cap mono">{c}</figcaption></figure>'
    if isinstance(item, tuple):
        return fig(item[1], r) + fig(item[2], r)
    a, c = PC.PHOTOS[item]; w, h, big = pfile(item)
    ss = f' srcset="{r}img/p/{item}-800.webp 800w, {r}img/p/{item}-1600.webp 1600w" sizes="(max-width:860px) 88vw, 780px"' if big else ""
    return f'<figure class="{"wide" if w > h else ""}"><img src="{r}img/p/{item}-800.webp"{ss} alt="{a}" width="{w}" height="{h}" loading="lazy"><figcaption class="cap mono">{c}</figcaption></figure>'

PHOTO_JOB = {  # city-strip photo -> the job page showing the same picture (image-hash match, 10/16); the other 10 aren't on any job page
 "037": "lower-matecumbe-canal-lawn", "130": "lower-matecumbe-canal-lawn", "161": "lower-matecumbe-canal-lawn", "269": "lower-matecumbe-canal-lawn",
 "135": "boynton-beach-putting-green-build", "293": "boynton-beach-putting-green-build", "107": "boynton-beach-putting-green-build",
 "green_waterfront_03": "long-key-50-ft-putting-green", "green_canal_03": "pembroke-pines-canal-putting-green", "237": "marathon-waterfront-lawn",
 "299": "marathon-resort-lawn-and-pool", "190": "marathon-resort-lawn-and-pool", "124": "marathon-resort-lawn-and-pool",
 "196": "southwest-florida-backyard-lawn", "069": "southwest-florida-backyard-lawn", "120": "southwest-florida-backyard-lawn", "098": "southwest-florida-backyard-lawn"}
def pstrip(items, r, h2="Real <b>jobs.</b>", style=' style="padding-top:clamp(70px,10vw,140px)"', link=False):
    # every photo gallery ends at the booking CTA
    return (f'<section class="work"{style}><header><h2>{h2}</h2></header>'
            f'<div class="strip">' + "".join(fig(x, r) if not (link and isinstance(x, str) and x in PHOTO_JOB) else
                                             f'<a href="{r}work/{PHOTO_JOB[x]}/" class="pjob">' + fig(x, r) + "</a>" for x in items) + "</div>" + vcta() + "</section>")

# Project pages (projects.py, from Muse's staging manifest). Masters are HEIC/MOV; only web derivatives ship.
# Re-saving through PIL drops EXIF, so no GPS from clients' homes leaves this machine.
import projects as PJ
try:
    import pillow_heif; pillow_heif.register_heif_opener()
except ImportError:
    pass
from PIL import ImageOps, ImageFilter, ImageStat
# P-07: the house number plaque beside the door, painted out in every frame that shows it (rects in source pixels)
PATCH = {"018.jpg": (500,135,518,170), "122.jpg": (646,222,664,252), "168.jpg": (491,316,510,360), "247.jpg": (592,113,609,145),
         "204.jpg": (935,257,957,308), "133.jpg": (410,141,428,184), "IMG_3440.HEIC": (1070,680,1135,860)}
def _patch(im, r):
    x0, y0, x1, y1 = r; m = max(4, (x1 - x0) // 3)
    ring = [im.crop((x0 - m, y0, x0, y1)), im.crop((x1, y0, x1 + m, y1))]
    im.paste(tuple(int(sum(ImageStat.Stat(c).median[i] for c in ring) / 2) for i in range(3)), r)
    reg = im.crop((x0 - m, y0 - m, x1 + m, y1 + m)).filter(ImageFilter.GaussianBlur(m / 3))
    im.paste(reg.crop((m // 2, m // 2, reg.width - m // 2, reg.height - m // 2)), (x0 - m + m // 2, y0 - m + m // 2))

def wfile(p, f, n):
    # img/w/<project-slug>-NN-800.webp (+1600): descriptive names, built once
    base = f"img/w/{p['slug']}-{n:02d}"
    if not os.path.exists(base + "-800.webp"):
        im = ImageOps.exif_transpose(Image.open(os.path.join(PJ.STAGE, p["dir"], f))).convert("RGB")
        if p["dir"].endswith("P-07-south-miami-lawn") and f in PATCH: _patch(im, PATCH[f])
        os.makedirs("img/w", exist_ok=True)
        for w in (800, 1600):
            if w == 800 or im.width >= 1600:
                im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(f"{base}-{w}.webp", quality=76)
    im = Image.open(base + "-800.webp")
    return base, im.width, im.height, os.path.exists(base + "-1600.webp")

import subprocess
def poster(p, sfx=""):
    base = f"img/w/{p['slug']}{sfx}-poster"
    if not os.path.exists(base + "-800.webp"):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1", "-i", f"vid/w/{p['slug']}{sfx}.mp4", "-frames:v", "1", "-vf", "scale='min(800,iw)':-2", base + "-800.webp"], check=True)
    im = Image.open(base + "-800.webp")
    return base, im.width, im.height, False, "F"

KIND = {"F": "Finished", "D": "Finished · detail", "B": "Before", "P": "During the install"}
for p in PJ.PROJECTS:
    p["imgs"] = []
    for n, (f, k) in enumerate(p["photos"], 1):
        base, w, h, big = wfile(p, f, n); p["imgs"].append((base, w, h, big, k))
    if p.get("slider"):
        p["ba"] = [wfile(p, f, 90 + i) for i, f in enumerate(p["slider"][:2])]
    p["hero"] = next((i for i in p["imgs"] if i[4] == "F"), None) or poster(p)  # no finished still: the finished video's frame
    p["path"] = f"work/{p['slug']}/"

def pfig(p, i, r, n, total):
    base, w, h, big, k = i
    t = re.sub(r"<[^>]+>", "", p["title"]).replace("&amp;", "&")
    alt = f"{KIND[k]}: {t.lower()} in {p['city']}" + ("" if k in "BP" else f", photo {n} of {total}")
    ss = f' srcset="{r}{base}-800.webp 800w, {r}{base}-1600.webp 1600w" sizes="(max-width:860px) 88vw, 780px"' if big else ""
    return (f'<figure class="{"wide" if w > h else ""}"><img src="{r}{base}-800.webp"{ss} alt="{alt}" width="{w}" height="{h}" loading="lazy">'
            f'<figcaption class="cap mono">{KIND[k]} · {p["city"]}</figcaption></figure>')

def gfig(p, i, r, n, total):
    # grid tile that opens the full-screen viewer (site.js) at the 1600w file when there is one
    base, w, h, big, k = i
    t = re.sub(r"<[^>]+>", "", p["title"]).replace("&amp;", "&")
    alt = f"{KIND[k]}: {t.lower()} in {p['city']}" + ("" if k in "BP" else f", photo {n} of {total}")
    return (f'<figure><button type="button" class="zoom" data-full="{r}{base}-{1600 if big else 800}.webp" aria-label="Enlarge photo {n}">'
            f'<img src="{r}{base}-800.webp" alt="{alt}" width="{w}" height="{h}" loading="lazy"></button><figcaption class="cap mono">{KIND[k]} · {p["city"]}</figcaption></figure>')

def card(p, r):
    base, w, h, big, _ = p["hero"]
    return (f'<li><a href="{r}{p["path"]}"><img src="{r}{base}-800.webp" alt="" width="{w}" height="{h}" loading="lazy">'
            f'<span class="mono">{p["city"]}</span><h3>{p["title"]}</h3></a></li>')

def cards(ps, r, h2, kicker="Projects"):
    return (f'<section class="pcards"><header><span class="mono" style="color:var(--turf)">{kicker}</span><h2>{h2}</h2></header>'
            f'<ul>{"".join(card(p, r) for p in ps)}</ul>{vcta()}</section>')

METHOD = ("<p>Every AJ Turf install is built the same way. We outline the area with 6-inch metal or plastic edging, "
          "pour a 3 x 3 x 3 inch concrete border along the inside of it, lay a weed barrier over everything, then glue the "
          "turf edges to the concrete with turf glue that carries a 15-year warranty.</p>"
          "<p>Most installers pin turf down with 6-inch steel spikes driven through the whole lawn. Spikes work loose, can hurt "
          "bare feet and paws, and tear the backing over time. A glued edge is safer and lasts longer.</p>")

# Thumbtack reviews, VERBATIM from FROM-MUSE-reviews-2026-10-12.md (all 14 are 5 stars, earned as AJ Supply).
# Left out on purpose: Darleen S. (Jereme's mother: his call), Lori L. (a deck job), the one-liners.
# Outbound link = the AJ Turf profile (Muse addendum 11/17). The 14 reviews still live on the legacy AJ Supply
# profile, so the link text must not promise them at the destination.
TT_URL = "https://www.thumbtack.com/fl/fort-myers/artificial-turf-installation/aj-turf/service/592250557913456653"
REVIEWS = [
 ("Patricia C.", "2021", "Jereme and his team were excellent. They were professional and courteous during the original estimate. Jereme was able to answer all of my questions and find a grass and layout that worked for my home. The kids and dogs absolutely love our new fake grass and now I don't have to worry about dirt, mud or bugs!!"),
 ("Melissa H.", "2022", "Jereme Strange was a great help in getting me through this process of leaving my horrible Florida Sod to this amazing stress free Turf. I would 100% recommend anyone who has been thinking about Turf to use AJ Supply. Jereme was so responsive to my needs, he gave very realistic expectations and was straight forward about everything."),
 ("Dante D.", "2022", "Team was very professional and courteous. They took the time to break down each detail of my install. They have helped me create my dream back yard! I am a customer for life."),
 ("Tiffany M.", "", "Hands down the best company to go to for all your turf needs. His professionalism and attention to detail is unmatched. Great customer service. You won't be disappointed!"),
 ("Karla S.", "2023", "Jereme is very professional and listened to all my needs and wants without any hesitation. His work is very good and I can tell that he loves what he does, he is a true craftman and an artist."),
 ("Adriana T.", "2022", "Great work from beginning to end. The service was smooth and very straight-forward. The team really went the extra mile at every stage and were so very helpful answering any concerns. I would recommend them unreservedly."),
]
def reviews_block(n=6):
    cards = "".join(f'<li><p>&ldquo;{html.escape(t)}&rdquo;</p><span class="mono">{who}{" · " + y if y else ""} · Thumbtack</span></li>' for who, y, t in REVIEWS[:n])
    return (f'<section class="reviews" id="reviews"><header><span class="mono" style="color:var(--turf)">&#9733;&#9733;&#9733;&#9733;&#9733; 5.0 on Thumbtack</span>'
            f'<h2 style="margin-top:18px">What clients <b>say.</b></h2></header><ul>{cards}</ul>'
            f'<p class="rv-note mono">Earned under our former name, AJ Supply. <a href="{TT_URL}" target="_blank" rel="noopener">See us on Thumbtack &rarr;</a></p></section>')

FAQ_BLOCK = """<details><summary>How do you price a yard?</summary><p>Most installs run $9 to $15 a square foot, depending on the turf and the site. For your yard, we measure and photograph it on site, review it, then follow up with one exact written price. The estimate is free. Turf comes in 15-foot-wide rolls, so every quote includes a standard allowance for cuts around your yard's shape.</p></details>
<details><summary>How long does an install take?</summary><p>About two days for every 1,000 square feet, depending on the site. Installs are typically scheduled within two weeks, or on your preferred date. New installs start at 1,000 square feet; repairs have no minimum.</p></details>
<details><summary>How do payments work?</summary><p>30% to put your install on the schedule, 35% on the first day on site, and the last 35% when the job is done and you've walked it with us. We take cash, PayPal, Venmo or card (card payments carry a 3% fee). We don't take Zelle.</p></details>
<details><summary>Why a concrete border instead of spikes?</summary><p>Spikes driven through a lawn can work loose, hurt bare feet and paws, and tear the turf backing. Gluing the turf edge to a poured concrete border holds it down without anything sticking up, and it lasts longer.</p></details>
<details><summary>What happens to my sprinklers?</summary><p>Existing sprinkler heads are capped and left in place, not ripped out. That keeps your system intact and the yard reversible. Florida's turf rule bars using in-ground irrigation to water turf areas, so a quick hose rinse is the way to clean and cool it on hot days.</p></details>
<details><summary>What's the warranty?</summary><p>Turf carries the manufacturer's warranty for the product you choose (8 to 25 years depending on the product), covering UV stability and strength; installation is covered by AJ Turf's 1-year labor warranty. You'll see the exact warranty for your product before you sign. Every AJ Turf installation includes a 1-year labor warranty. During that first year, if your turf needs attention because of how it was installed — infill settling or running low, turf laying down in high-traffic areas, seams or edges lifting — we come back out, assess it in person, and make it right. That's covered by the warranty, not an extra service call. Routine cleaning and cosmetic upkeep aren't included — but if the install itself isn't performing, that's on us.</p></details>
"""

SEO = {'artificial-turf-installation': ('Artificial Turf Lawns in Fort Myers &amp; Naples | AJ Turf', 'Artificial turf lawns, built to last', 'Green year round with no mowing or watering. Installed on a compacted base with a glued concrete border, no spikes. Free onsite estimate.', 'Artificial turf<br><b>lawns.</b>'), 'pet-turf': ('Pet Turf Installation in Fort Myers &amp; Naples | AJ Turf', 'Pet turf that drains, not smells', "Built drainage-first so Florida heat doesn't trap odor. Pet-friendly infill and glued edges with no spikes for paws. Free onsite estimate.", 'Pet turf that<br><b>drains.</b>'), 'putting-greens': ('Backyard Putting Greens in Fort Myers &amp; Naples | AJ Turf', 'Backyard putting greens with a true roll', 'Putting surface plus fringe, cut and seamed by hand, off the lanai or out by the water. Free onsite estimate, then one exact price.', 'Backyard<br><b>putting greens.</b>'), 'pool-and-paver-turf': ('Turf for Pools &amp; Pavers in Fort Myers &amp; Naples | AJ Turf', 'Turf for pools and pavers', 'Turf strips between pavers and tight, glued borders around pool decks. Clean lines that look designed, not patched in. Free onsite estimate.', 'Pools &amp;<br><b>pavers.</b>'), 'turf-repair': ('Artificial Turf Repair in Fort Myers &amp; Naples | AJ Turf', 'Artificial turf repair and re-installs', 'Ripples, open seams, washouts and loose edges fixed, or a full re-install done right with a concrete border. Free onsite estimate.', 'Turf repair &amp;<br><b>re-installs.</b>')}

SERVICES = [
 dict(slug="artificial-turf-installation", nav="Lawns", title="Artificial Turf Installation", h1="Artificial turf <b>lawns.</b>",
      img="palm-yard", kw="artificial turf installation",
      lede="Front yards, back yards and side yards that stay green through a Florida August, with no mowing, watering or brown patches.",
      sections=[("Why homeowners <b>switch.</b>",
        "<p>Southwest Florida lawns fight heat, sandy soil, shade from palms and oaks, and watering restrictions. Turf ends the cycle of resodding, fertilizing and mowing, and it looks the same in March as it does in September.</p>"
        "<ul><li><b>No mowing or watering.</b> A rinse and a brush is the upkeep.</li><li><b>Stays green.</b> No brown patches from drought, grubs or chinch bugs.</li><li><b>Built to drain.</b> Rain goes through the turf and the compacted base, not across your patio.</li></ul>"),
       ("Commercial &amp; <b>event lawns.</b>",
        "<p>The same build works beyond the backyard: storefronts, offices, rental properties and event spaces that need to look green and finished every day, with no mowing crew and no muddy patches after rain.</p>"
        "<p>One event venue went from bare ground and a temporary floor to a full turf lawn around the tent. See it in the photos below.</p>"),
       ("How we <b>build it.</b>", METHOD)],
      photos=[("event-before","An event tent on bare ground and a temporary floor before the install","Before · event space"),("event-after","The same event space with a full turf lawn around the tent","After · event lawn")]),
 dict(slug="pet-turf", nav="Pet turf", title="Pet Turf", h1="Pet <b>turf.</b>", img="side-garden", kw="pet turf",
      photos=[("pet-dogs","Two dogs playing on pet turf","Pet turf · dog-tested"),("pet-dogs-corner","Dogs on a fenced pet turf area","Fenced pet area")],
      lede="Turf built for dogs: drainage first, pet-friendly infill, and a glued edge with no spikes for paws to find.",
      sections=[("Odor is a <b>base problem.</b>",
        "<p>In Florida heat and humidity, pet odor comes from what happens under the turf, not the blades. When urine can't drain, it sits in the base and smells. That's why we start with a compacted screening-sand base that drains, then add pet-friendly infill.</p>"
        "<ul><li><b>Drains fast.</b> Rinse the area and it washes through.</li><li><b>No spikes.</b> Nothing to work loose under running dogs.</li><li><b>No mud.</b> No dug-up patches or dirty paws after rain.</li></ul>"),
       ("How we <b>build it.</b>", METHOD)]),
 dict(slug="putting-greens", nav="Putting greens", title="Backyard Putting Greens", h1="Putting <b>greens.</b>", img="green-waterfront", kw="backyard putting green",
      # green-course.webp OFF the site 10/9: Jereme — "not my work", origin unknown (maybe a sub's job elsewhere). Never re-add.
      # Strip = Muse's plan set (photo_content.SERVICE); the old copies duplicated those files.
      lede="True-rolling backyard greens with fringe, built off the patio, beside the pool or out by the water.",
      # Greens pricing: Jereme 11/18 ruled $9-$15 across the board, greens included (supersedes the 11/16 no-figure call).
      faq="<details><summary>How much does a backyard putting green cost?</summary><p>Most backyard greens run $9 to $15 a square foot installed, the same range as our lawns. Where yours lands depends on the putting turf, the fringe, and how much the base has to be shaped for a true roll. The exact price comes after a free onsite estimate: we measure and take photos, review it, then follow up with one exact written price.</p></details>"
          "<details><summary>What's included in that price?</summary><p>The full build: excavation, a shaped and compacted base, the putting surface and a taller fringe cut and seamed by hand, cups placed where you want them, infill, and haul-away. Every green is play-tested before handoff.</p></details>"
          "<details><summary>How fast will it roll?</summary><p>That depends on the turf and how the green is set up, so we don't promise a speed. See the <a href='../guide/how-fast-does-a-turf-putting-green-roll/'>lab-measured speeds and test conditions</a> in the Turf Guide.</p></details>"
          "<details><summary>How do you make sure it putts right?</summary><p>The base is shaped and compacted so the ball rolls true, and we play-test every green before handoff.</p></details>"
          "<details><summary>Where can a green go?</summary><p>Off a lanai, beside a pool, along a canal or tucked into a side yard. Cups and flags go where you want them.</p></details>"
          "<details><summary>Do you repair or resurface old greens?</summary><p>Yes. See <a href='../turf-repair/'>turf repair</a>: a worn green along a pool deck is on that page, before and after.</p></details>",
      sections=[("Built like a <b>green.</b>",
        "<p>A good green is about the base. We shape and compact it so the ball rolls true, then install a short putting surface surrounded by a slightly taller fringe turf, the same way a course frames a green. How fast does a backyard green roll? See the <a href='../guide/how-fast-does-a-turf-putting-green-roll/'>lab-measured speeds and test conditions</a>.</p>"
        "<ul><li><b>Putting surface plus fringe.</b> Two turfs, cut and seamed by hand.</li><li><b>Cups and flags placed where you want them.</b></li><li><b>Fits real yards.</b> Off a lanai, along a canal or tucked into a side yard.</li></ul>"),
       ("The <b>details.</b>", METHOD)]),
 dict(slug="pool-and-paver-turf", nav="Pools & pavers", title="Turf for Pools & Pavers", h1="Pools &amp; <b>pavers.</b>", img="pavers", kw="turf around pools and pavers",
      lede="Turf strips between pavers, clean borders around pool decks, and green that runs right up to the stone.",
      sections=[("Clean <b>lines.</b>",
        "<p>Turf next to hardscape only looks good if every edge is tight. We cut turf to the stone, glue the edges down, and keep the lines straight so it looks designed, not patched in.</p>"
        "<ul><li><b>Paver strips.</b> Grass-look joints that never need trimming.</li><li><b>Pool surrounds.</b> A soft green border that drains after every swim.</li><li><b>No spikes near the pool.</b> Glued edges hold without anything sticking up.</li></ul>"),
       ("How we <b>build it.</b>", METHOD)]),
 dict(slug="turf-repair", nav="Repairs", title="Artificial Turf Repair & Re-installs", h1="Repairs &amp; <b>re-installs.</b>", img="pool-side", kw="artificial turf repair",
      photos=[("repair-before","A worn, matted putting green along a pool deck before the repair","Before · worn green by the pool"),("repair-after","The same green after the repair, fresh and even","After · same green, repaired"),("repair-after-wide","The repaired green running the length of the pool deck","After · full length")],
      lede="Ripples, open seams, washed-out bases and loose edges. We fix turf other crews put in, or pull it and do it right. Free onsite assessment, an exact price in a follow-up, and no minimum job size.",
      sections=[("What we <b>fix.</b>",
        "<ul><li><b>Ripples and wrinkles.</b> Re-stretched and re-secured.</li><li><b>Open or visible seams.</b> Re-cut and re-taped.</li><li><b>Dips and washouts.</b> Base rebuilt and compacted.</li><li><b>Loose edges.</b> Secured, or re-done with a concrete border.</li></ul>"
        "<p>Sometimes a repair isn't worth it. If the base or the turf itself has failed, we'll tell you straight and quote a full re-install instead.</p>"),
       ("How we <b>rebuild.</b>", METHOD)]),
]

CITY = {
 "Fort Myers": ("fort-myers", "Lee County", "hero-after",
   "Fort Myers yards deal with sandy soil, summer downpours and shade from mature trees. Turf on a compacted, draining base handles all three."),
 "Cape Coral": ("cape-coral", "Lee County", "waterfront",
   "Cape Coral is canal country. Waterfront lots and pool cages are where turf and putting greens make the biggest difference."),
 "Naples": ("naples", "Collier County", "courtyard",
   "Naples homes and HOA communities expect a finished, high-end look. Tight edges, hidden seams and a natural-looking turf matter here."),
 "Estero": ("estero", "Lee County", "backyard-green",
   "Estero's newer communities often mean HOA review before anything changes in the yard. We prepare the HOA application and submit it for you."),
 "Bonita Springs": ("bonita-springs", "Lee County", "pool-deck",
   "Between Fort Myers and Naples, Bonita Springs yards range from golf communities to waterfront lots, both a natural fit for putting greens and pool-side turf."),
 "Lehigh Acres": ("lehigh-acres", "Lee County", "backyard-wide",
   "Just east of Fort Myers, Lehigh Acres yards sit on sandy soil where keeping grass green through summer is a constant fight. Turf on a compacted, draining base ends that."),
 "Sanibel": ("sanibel", "Lee County", "palm-yard",
   "On a barrier island, salt air, sandy soil and storm recovery shape what holds up. A glued edge with no spikes is a sturdy choice for island yards."),
 "Marco Island": ("marco-island", "Collier County", "green-waterfront",
   "On Marco Island, salt air, full sun and sandy island soil are what turf has to stand up to, and many yards already have a green or a lawn that's starting to show its age."),
}

# Cities whose page leads with something other than the generic service list (Muse spec 10/22, Jereme-approved):
# Marco = putting greens + repairs first, then waterfront, then general installs. Only claims already live on the site.
CITY_FOCUS = {"Marco Island": dict(
  title="Putting Greens &amp; Turf Repair, Marco Island FL | AJ Turf",
  desc="Backyard putting greens built and repaired on Marco Island, turf repair whoever installed it, and canal-front lawns. Free onsite assessment.",
  h1="Marco Island<br><b>greens &amp; repair.</b>",
  lede="Backyard putting greens built and repaired, turf repair whoever put it in, and canal-front lawns. Free onsite estimate, then one exact price.",
  secs=[
   ("Putting greens on <b>Marco Island.</b>",
    "<p>We build new backyard greens and repair the ones already there. On an older green the usual problems are open seams, lifting edges, worn cups and fringe, and matted spots that no longer roll true.</p>"
    "<ul><li><b>New greens.</b> A shaped, compacted base, a putting surface plus a taller fringe, cut and seamed by hand, with cups placed where you want them. <a href='../putting-greens/'>How we build a green</a>.</li>"
    "<li><b>Green repair.</b> Seams re-cut and re-taped, edges re-secured, low spots rebuilt. See a <a href='../work/marco-island-canal-front-putting-green/'>canal-front green we finished in Marco Beach</a>, on video.</li>"
    "<li><b>Repair or resurface.</b> If the base or the turf itself has failed, we'll tell you straight and quote a rebuild instead. <a href='../guide/can-artificial-turf-be-repaired-or-does-it-need-replacing/'>How to tell the difference</a>.</li></ul>"),
   ("Turf repair, <b>whoever installed it.</b>",
    "<p>We fix turf other crews put in, or pull it and do it right. Every repair starts with a free onsite assessment and an exact price, and repairs have no minimum job size.</p>"
    "<ul><li><b>Ripples and wrinkles.</b> Re-stretched and re-secured.</li><li><b>Open or visible seams.</b> Re-cut and re-taped.</li><li><b>Dips and washouts.</b> Base rebuilt and compacted.</li><li><b>Loose edges.</b> Secured, or re-done with a concrete border.</li></ul>"
    "<p><a href='../turf-repair/'>More on turf repair</a>.</p>"),
   ("Canal-front <b>lawns.</b>",
    "<p>Waterfront yards get salt air, full sun and sandy soil. We build on a compacted base that drains and glue the turf to a concrete border with no spikes, so the edges hold. Older turf fades in Florida sun; here's <a href='../guide/will-artificial-turf-fade-in-the-florida-sun/'>what decides how fast</a>. See a <a href='../work/marco-island-canal-front-lawn/'>canal-front lawn we built on Marco Island</a>.</p>"),
   ("New turf <b>lawns.</b>",
    "<p>New installs start at 1,000 square feet, and most run $9 to $15 a square foot, depending on the turf and the site. For your yard, we measure and photograph it on site, review it, then follow up with one exact written price. The estimate is free. <a href='../artificial-turf-installation/'>How we install a lawn</a>.</p>"
    "<ul>" + "".join(f'<li><b><a href="../{x["slug"]}/" style="color:inherit">{x["title"]}</a></b></li>' for x in SERVICES) + "</ul>"),
  ])}

import hashlib
# cache-bust: browsers keep style.css/site.js ~10 min, so new markup met old CSS (Jereme 10/13 "pics are squished")
ASSET_V = hashlib.md5(open("style.css", "rb").read() + open("site.js", "rb").read()).hexdigest()[:8]

def head(title, desc, path, depth, schema, og_title=None, og_slug="home"):
    r = "../" * depth
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-EFM29XK9QK"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-EFM29XK9QK');
document.addEventListener('input',e=>{{const b=e.target.closest('.ba');if(b)b.style.setProperty('--p',e.target.value+'%')}});
document.addEventListener('click',e=>{{const y=e.target.closest('.yt');if(y){{const f=document.createElement('iframe');f.src='https://www.youtube-nocookie.com/embed/'+y.dataset.id+'?autoplay=1&playsinline=1&rel=0';f.allow='autoplay; encrypted-media; picture-in-picture; fullscreen';f.allowFullscreen=true;f.title=y.dataset.title;y.replaceWith(f);gtag('event','video_play',{{video_title:y.dataset.title}});return}}const a=e.target.closest('a');if(!a)return;if(a.href.includes('appointments/schedules'))gtag('event','generate_lead',{{method:'booking_link'}});else if(a.href.startsWith('tel:'))gtag('event','generate_lead',{{method:'phone_call'}});else if(a.href.startsWith('sms:'))gtag('event','generate_lead',{{method:'text_message'}});}});</script>
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{BASE}{path}">
<meta name="theme-color" content="#121613">
<meta property="og:site_name" content="AJ Turf"><meta property="og:locale" content="en_US"><meta property="og:type" content="website">
<meta property="og:title" content="{og_title or title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{BASE}{path}">
<meta property="og:image" content="{BASE}img/og/{og_slug}.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{(og_title or title)} by AJ Turf">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{og_title or title}"><meta name="twitter:description" content="{desc}"><meta name="twitter:image" content="{BASE}img/og/{og_slug}.jpg">
<link rel="icon" href="{r}img/mark.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,300;12..96,500;12..96,700&family=Hanken+Grotesk:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap" onload="this.onload=null;this.rel='stylesheet'"><noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,300;12..96,500;12..96,700&family=Hanken+Grotesk:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap"></noscript>
<link rel="stylesheet" href="{r}style.css?v={ASSET_V}">
<script type="application/ld+json">{json.dumps(schema)}</script>
</head>
<body>
<nav class="nav solid" id="nav">
  <a class="mark" href="{r}"><img src="{r}img/mark.svg" alt="" width="34" height="34">AJ<span>/</span>TURF</a>
  <div class="mid mono"><a href="{r}#method">Method</a><a href="{r}our-work/">Work</a><a href="{r}videos/">Videos</a><a href="{r}#services">Services</a><a href="{r}guide/">Turf Guide</a></div>
  <a class="cta mono" href="#book">Free estimate</a>
</nav>'''

SOCIAL = open("_social.html", encoding="utf-8").read().strip()  # brand icons (Simple Icons, CC0)
QF = open("_qf.html", encoding="utf-8").read().strip()  # the quick form, shared with the hand-built home page
def close(depth):
    r = "../" * depth
    svc = "".join(f'<a href="{r}{s["slug"]}/">{s["nav"]}</a>' for s in SERVICES)
    ar = "".join(f'<a href="{r}{CITY[a][0]}/">{a}</a>' for a in AREAS)
    return f'''<section class="close" id="book">
  <img src="{r}img/green-canal.webp" alt="" loading="lazy">
  <div class="in">
    <h2>See it in<br><b>your yard.</b></h2>
    <div><p style="max-width:380px;margin-bottom:24px">Book a free onsite estimate. We'll measure, bring samples you can feel, and follow up with one exact written price.</p>
      <a class="book" href="{BOOK}" target="_blank" rel="noopener">Book a free estimate <span aria-hidden="true">→</span></a>
      <a class="alt mono" href="tel:{PHONE_HREF}">Or call {PHONE}</a><a class="alt mono" href="sms:{PHONE_HREF}">Or text us</a>
      <p class="book-note">Estimates are booked at least 48 hours out. We'll call the day before to confirm, and again when we're on our way.</p>
      {QF}</div>
  </div>
</section>
<footer class="mono"><span>AJ Turf · Southwest Florida</span><span class="foot-links">{svc}</span><span class="foot-links">{ar}</span><span class="foot-links"><a href="{r}our-work/">Our work</a><a href="{r}videos/">Videos</a><a href="{r}guide/">Turf Guide</a><a href="{r}privacy/">Privacy</a><span>Mon–Sat 9–5</span></span>{FIND_US}{SOCIAL}</footer>
<script src="{r}site.js?v={ASSET_V}" defer></script>
<script src="https://ajturf-chat.sam-947.workers.dev/widget.js" defer></script>
</body>
</html>'''

# One canonical URL per live profile (Muse 11/10 + 11/17 briefs): feeds schema sameAs AND the footer "Find us on" row.
PROFILES = [("Yelp", "https://www.yelp.com/biz/aj-turf-fort-myers"), ("Instagram", "https://www.instagram.com/aj.turf"),
            ("Facebook", "https://www.facebook.com/aj.turf"), ("YouTube", "https://www.youtube.com/@AJTurf"),
            ("Houzz", "https://www.houzz.com/pro/jereme-strange"), ("Nextdoor", "https://nextdoor.com/page/aj-turf-fort-myers-fl/"),
            ("Thumbtack", TT_URL), ("Bark", "https://www.bark.com/en/us/company/aj-turf/GRBJeL"),
            ("Manta", "https://www.manta.com/c/m1hdvgq/aj-turf"),
            ("Hotfrog", "https://www.hotfrog.com/company/AaHqnXySc_WpuZN1DYZzfA/aj-turf/fort-myers/lawn-garden"),
            ("MerchantCircle", "https://www.merchantcircle.com/aj-turf-fort-myers-fl"), ("Cylex", "https://www.cylex.us.com/company/aj-turf-40786360.html"),
            ("LinkedIn", "https://www.linkedin.com/in/jeremestrange/")]  # Jereme's profile, AJ Turf = Owner (Muse 11/18)
FIND_US = '<span class="foot-links find-us"><span>Find us on</span>' + "".join(f'<a href="{u}" target="_blank" rel="me noopener">{n}</a>' for n, u in PROFILES) + "</span>"
def org():
    return {"@type": "HomeAndConstructionBusiness", "@id": BASE + "#business", "name": "AJ Turf", "url": BASE,
            "telephone": "+1-" + PHONE, "email": EMAIL, "image": BASE + "img/og/home.jpg", "logo": BASE + "img/mark.svg",
            "areaServed": [{"@type": "City", "name": a + ", FL"} for a in AREAS],
            "openingHours": "Mo-Sa 09:00-17:00", "priceRange": "Free onsite estimate",
            "sameAs": [u for _, u in PROFILES]}

def crumbs(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(items)]}

import re as _re
def faq_schema(html):
    qa = _re.findall(r"<summary>(.*?)</summary><p>(.*?)</p>", html)
    from html import unescape as _unesc; t = lambda s: _unesc(_re.sub(r"<[^>]+>", "", s))  # schema text = the visible text, minus the link markup
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": t(q), "acceptedAnswer": {"@type": "Answer", "text": t(a)}} for q, a in qa]}

def page(path, title, desc, kicker, h1, lede, img, sections, schema_extra, related, og_title=None, og_slug="home", photos=(), faq=""):
    faq = faq + FAQ_BLOCK  # page-specific questions first, then the shared set
    depth = path.count("/")
    r = "../" * depth
    schema = {"@context": "https://schema.org", "@graph": [org()] + schema_extra + [faq_schema(faq)]}
    secs = "".join(x if isinstance(x, str) else f'<section class="prose"><h2>{x[0]}</h2><div class="body">{x[1]}</div></section>' for x in sections)
    rel = "".join(f'<li><a href="{r}{u}">{n}</a></li>' for n, u in related)
    if photos: secs += pstrip(photos, r)
    # ballpark calculator on the service pages (Muse pass-1 §5); site.js builds it
    ct = {"artificial-turf-installation/": "Lawn", "pet-turf/": "Pet turf", "putting-greens/": "Putting green", "pool-and-paver-turf/": "Pool & pavers", "turf-repair/": "Repair"}.get(path)
    if ct: secs += f'<section class="calc-sec"><div class="calc" data-type="{ct}"></div></section>'
    html = head(title, desc, path, depth, schema, og_title, og_slug) + f'''
<header class="sub-hero">
  <img src="{r}img/{img}.webp" alt="">
  <div class="in"><span class="mono crumbs"><a href="{r}">AJ Turf</a> / {kicker}</span>
    <h1>{h1}</h1><p class="lede">{lede}</p>
    <p style="margin-top:28px"><a class="book" href="{BOOK}" target="_blank" rel="noopener">Book a free estimate <span aria-hidden="true">→</span></a></p></div>
</header>
<main>{secs}
{reviews_block(3)}
<section class="split"><div><span class="mono" style="color:var(--turf)">Questions</span><h2 style="margin-top:18px">Good to<br><b>know.</b></h2></div><div>
{faq}</div></section>
<section class="related"><span class="mono" style="color:var(--turf)">Keep looking</span><ul>{rel}</ul></section>
</main>
''' + close(depth)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    open(os.path.join(path, "index.html") if path.endswith("/") else path, "w", encoding="utf-8").write(html)

# Aimed internal links (Muse GSC aiming 11/16): point at the install page Google picked (how-artificial-turf-is-installed)
# and the guide questions sitting closest to page one. Re-aim from Muse's Monday keyword tracker.
def gtitle(s): return GUIDE_TITLE.get(s) or re.search(r"^# (.+)$", open(f"kb_src/{s}.md", encoding="utf-8").read(), re.M).group(1)  # same title the guide hub shows
GUIDE_TITLE = {"how-artificial-turf-is-installed": "How Artificial Turf Is Installed, Step by Step"}
CLUSTER = ["how-long-does-an-artificial-turf-installation-take", "what-base-goes-under-artificial-turf",
           "do-i-need-a-weed-barrier-under-artificial-turf", "does-artificial-turf-get-mold-algae-or-bugs",
           "does-artificial-turf-contain-pfas-or-lead", "can-artificial-turf-go-around-a-pool-deck-or-over-hardscape",
           "what-does-a-turf-warranty-cover"]
SVC_READ = {
    "artificial-turf-installation": ("Straight answers <b>before you buy.</b>", ["how-artificial-turf-is-installed"] + CLUSTER),
    "turf-repair": ("What went wrong, <b>and why.</b>", ["can-artificial-turf-be-repaired-or-does-it-need-replacing",
        "why-is-my-artificial-turf-wrinkling-or-lifting", "why-do-artificial-turf-installs-fail-in-the-first-two-years",
        "why-did-my-turf-melt", "does-artificial-turf-help-or-hurt-yard-drainage", "will-artificial-turf-puddle-or-flood-in-heavy-rain",
        "does-artificial-turf-get-mold-algae-or-bugs", "why-does-my-artificial-turf-smell", "what-maintenance-does-artificial-turf-need",
        "what-does-a-turf-warranty-cover", "how-artificial-turf-is-installed"]),
    "pet-turf": ("Pet turf, <b>answered.</b>", ["best-artificial-turf-for-dogs-in-florida", "what-infill-stops-pet-odor-in-artificial-turf",
        "why-does-my-artificial-turf-smell", "silica-zeolite-or-coated-sand-which-infill-should-i-use", "how-fast-should-artificial-turf-drain"]),
    "putting-greens": ("Greens, <b>answered.</b>", ["how-fast-does-a-turf-putting-green-roll", "what-pile-height-is-right-for-lawns-pets-and-putting-greens",
        "how-much-does-artificial-turf-cost-in-southwest-florida", "can-artificial-turf-be-repaired-or-does-it-need-replacing"]),
}
# Repair wedge (Muse 11/18 item 2): these guides each send readers to /turf-repair/ at the end of the article.
REPAIR_Q = set(SVC_READ["turf-repair"][1]) - {"how-artificial-turf-is-installed", "what-does-a-turf-warranty-cover"} | {
    "why-do-artificial-turf-installs-fail-in-the-first-two-years", "how-long-does-artificial-turf-last-in-florida", "will-artificial-turf-fade-in-the-florida-sun"}
def readlist(h, slugs, r): return (h, "<ul>" + "".join(f'<li><a href="{r}guide/{s}/">{gtitle(s)}</a></li>' for s in slugs) + "</ul>")

urls = [""]
for s in SERVICES:
    path = s["slug"] + "/"
    rel = [(x["nav"], x["slug"] + "/") for x in SERVICES if x is not s] + [(a, CITY[a][0] + "/") for a in AREAS[:3]]
    t, ogt, desc, _ = SEO[s["slug"]]
    svc = {"@type": "Service", "name": s["title"], "serviceType": s["kw"], "provider": {"@id": BASE + "#business"},
           "areaServed": [{"@type": "City", "name": a + ", FL"} for a in AREAS], "url": BASE + path}
    secs, vids = list(s["sections"]), []
    if s["slug"] in SVC_READ: secs.append(readlist(*SVC_READ[s["slug"]], "../"))
    ps = [p for p in PJ.PROJECTS if any(svc == s["slug"] and a in (p["app"], p.get("also")) for a, _, svc in PJ.APPS)]
    if ps: secs.append(cards(ps, "../", "Real projects, <b>start to finish.</b>"))
    if s["slug"] in SERVICE_VIDEOS:
        vids, h = SERVICE_VIDEOS[s["slug"]]; at = SERVICE_VIDEO_AFTER.get(s["slug"])
        i = next((n + 1 for n, x in enumerate(secs) if isinstance(x, tuple) and x[0] == at), 1)
        secs.insert(i, vblock(vids, "../", h)); PAGE_VIDEOS[path] = vids
    if s["slug"] == "turf-repair":  # no repair jobs in the catalog yet: point at the work hub by type
        secs.append(cards([next(p for p in PJ.PROJECTS if p["app"] == a) for a, _, _ in PJ.APPS], "../", "Our work, <b>by type of job.</b>", "Real installs"))
    page(path, t, desc, s["nav"], s["h1"], s["lede"], s["img"], secs,
         [svc, crumbs([("AJ Turf", ""), (s["title"], path)])] + [vobj(v) for v in vids], rel, ogt, s["slug"], list(s.get("photos", ())) + PC.SERVICE.get(s["slug"], []), s.get("faq", ""))
    urls.append(path)

# City FAQ with real numbers (Muse 11/18 item 3): the format winning the money queries. Public facts only.
def city_faq(a):
    return (f"<details><summary>How much does artificial turf cost in {a}?</summary><p>Most installs in {a} run $9 to $15 a square foot, installed. "
            f"New installs start at 1,000 square feet, so a 1,000 square foot yard lands between about $9,000 and $15,000, depending on the turf and what the site needs underneath. "
            f"The exact price comes after a free onsite estimate: one written number, never a price promised on the spot.</p></details>"
            f"<details><summary>What does a putting green cost in {a}?</summary><p>The same $9 to $15 a square foot range, greens included. "
            f"Every green gets a shaped, compacted base, a putting surface plus fringe cut and seamed by hand, and a play test before handoff. <a href='../putting-greens/'>How we build a green</a>.</p></details>"
            f"<details><summary>Do you repair turf in {a} that someone else installed?</summary><p>Yes. Repairs start with a free onsite assessment and have no minimum job size. <a href='../turf-repair/'>What we fix</a>.</p></details>")

# Neighborhood pages (Muse 11/18 item 4 + addenda). Tier 1 = real proof on file; Tier 2 = service-area only, no job claims.
# Never print customer names, street addresses, plat details or home values on these pages.
HOOD = [
 dict(city="Marco Island", slug="marco-beach", name="Marco Beach", tier=1, img="green-waterfront",
      local="Marco Beach is the island's canal grid: waterfront lots with docks and pools, salt air and full sun, and plenty of yards with an older lawn or green that's starting to show its age.",
      notes=[("Canal-front <b>yards.</b>", "<p>On a canal lot, turf has to drain fast after a summer storm and hold its edges in sandy island soil. We build on a compacted base that drains and glue the turf to a poured concrete border with no spikes. Florida's turf rule keeps synthetic turf 10 feet back from the water, and we run that setback math on site before design. <a href='../../guide/artificial-turf-near-a-canal-setbacks-and-rules/'>How the setback works</a>.</p>"),
             ("Work we've <b>done here.</b>", "<p>We've restored a <a href='../../work/marco-island-canal-front-putting-green/'>backyard putting green on a canal-front lot in Marco Beach</a>, video included, and we've built a <a href='../../work/marco-island-canal-front-lawn/'>canal-front lawn on Marco Island</a>.</p>")]),
 dict(city="Naples", slug="old-naples", name="Old Naples", img="courtyard",
      local="Old Naples runs from the beach avenues to the bay, with historic cottages, rebuilt estates and courtyard gardens on tight, walkable lots.",
      notes=[("Small lots, <b>finished edges.</b>", "<p>On a close-set lot, every edge shows. We cut turf tight to pavers, walls and pool decks, glue it to a concrete border, and hide the seams, so a courtyard or side yard looks designed, not patched in. <a href='../../pool-and-paver-turf/'>Turf around pools and pavers</a>.</p>")]),
 dict(city="Naples", slug="aqualane-shores", name="Aqualane Shores", img="waterfront",
      local="Aqualane Shores is almost all canal-front: deep-water lots with docks and seawalls, where the back yard runs straight to the water.",
      notes=[("Turf to the <b>seawall setback.</b>", "<p>Florida's turf rule keeps synthetic turf 10 feet back from the water line, so on a canal lot the design starts with that measurement. We measure it on site, then build a lawn or a green that drains fast and holds up to salt air. <a href='../../guide/artificial-turf-near-a-canal-setbacks-and-rules/'>How the setback works</a>.</p>")]),
 dict(city="Naples", slug="port-royal", name="Port Royal", img="green-canal",
      local="Port Royal sits on Naples Bay and the Gulf, and most of its homes are on the water, with estate lots, pools and long views down the canals.",
      notes=[("Built for <b>estate yards.</b>", "<p>Large waterfront lots are where a backyard putting green and a pool-side lawn earn their keep. We shape the base for a true roll, frame the green with fringe, and keep the turf 10 feet back from the water, as Florida's turf rule requires. If your property has a community review, we prepare the application with the product specs and submit it for you.</p>")]),
 dict(city="Marco Island", slug="hideaway-beach", name="Hideaway Beach", img="green-waterfront",
      local="Hideaway Beach is Marco Island's gated enclave at the north end of the island, with Gulf-front and bayfront homes, salt spray and full sun.",
      notes=[("Gated community, <b>handled.</b>", "<p>In a gated community, the install is as much logistics as turf: access, approvals and working cleanly around neighbors. We prepare the architectural review application with the product specs and install details, and submit it for you. On the beach side, a glued edge with no spikes holds up to salt air and sandy soil.</p>")]),
 dict(city="Naples", slug="park-shore-moorings", name="Park Shore and The Moorings", img="pool-deck",
      local="Park Shore and The Moorings are a grid of Gulf-access canals and older homes, and many of them are being remodeled or rebuilt right now, yards included.",
      notes=[("Remodel or <b>rebuild.</b>", "<p>If the house is being redone, the yard is the last piece. We work after the builder, tear out tired grass, build a compacted base that drains, and finish with turf glued to a concrete border. Canal lots keep the turf 10 feet back from the water under Florida's turf rule.</p>")]),
 dict(city="Naples", slug="pelican-bay", name="Pelican Bay", img="backyard-green",
      local="Pelican Bay's single-family neighborhoods, from Bay Colony to The Strand, sit behind the beach and the berm, with landscaped lots, pools and lanais.",
      notes=[("For the <b>single-family homes.</b>", "<p>We work on single-family yards: lawns, pool surrounds and backyard greens off the lanai. Where an architectural review applies, we prepare the application with the product specs and submit it for you. <a href='../../guide/can-my-hoa-stop-me-from-installing-artificial-turf/'>How HOA rules and Florida law fit together</a>.</p>")]),
 dict(city="Estero", slug="miromar-lakes", name="Miromar Lakes", img="backyard-wide",
      local="Miromar Lakes is built around a large freshwater lake and a golf course, so most yards face the water, and a backyard green is a natural fit.",
      notes=[("Lakefront and <b>golf.</b>", "<p>A lakefront lot needs turf that drains fast and holds its edges, and a golfer's yard needs a green that rolls true. We build both on a compacted base, with the green framed in fringe and play-tested before handoff. Florida's turf rule keeps synthetic turf 10 feet back from the water, and we measure that on site.</p>")]),
 dict(city="Estero", slug="wildblue", name="WildBlue", img="backyard-green",
      local="WildBlue is a newer community built around large navigable lakes, and many homeowners there are still finishing their yards.",
      notes=[("Finishing a <b>new yard.</b>", "<p>New construction often leaves compacted fill and builder sod that can struggle in its first summer. We take it out, build a base that drains, and finish the yard with turf glued to a concrete border. Most new communities need architectural review first, and we prepare the application and submit it for you.</p>")]),
]
HOODS_OF = {}
for h_ in HOOD: HOODS_OF.setdefault(h_["city"], []).append(h_)

# 6: nearest existing job pages per city (SWFL jobs first), shown as cards above the reviews
_SW = ["lehigh-acres-backyard-putting-green", "southwest-florida-backyard-lawn", "marco-island-canal-front-lawn", "marco-island-canal-front-putting-green"]
NEAR = {"Fort Myers": _SW, "Cape Coral": _SW, "Lehigh Acres": _SW, "Sanibel": _SW,
        "Naples": _SW[::-1], "Estero": _SW[::-1], "Bonita Springs": _SW[::-1], "Marco Island": _SW[::-1]}
for a in AREAS:
    slug, county, img, local = CITY[a]
    path = slug + "/"
    secs = [
      (f"Turf in <b>{a}.</b>", f"<p>{local}</p><p>AJ Turf installs artificial turf lawns, pet turf, putting greens and turf around pools and pavers for homes in {a} and across {county}. Most installs run $9 to $15 a square foot, greens included. Every job starts with a free onsite estimate: we measure and photograph in person, then follow up with one exact written price.</p>"
         "<ul>" + "".join(f'<li><b><a href="../{x["slug"]}/" style="color:inherit">{x["title"]}</a></b></li>' for x in SERVICES) + "</ul>"),
      ("HOAs and <b>Florida law.</b>", "<p>A 2025 Florida law (HB 683) directed the Florida Department of Environmental Protection to set statewide standards for synthetic turf on single-family lots of an acre or less. Those standards (Rule 62-308.100) took effect in May 2026, and local governments can't ban turf that meets them. An HOA can't restrict turf it can't see (§720.3045), but a visible front yard can still need architectural review. We prepare that application with the product specs and install details, and submit it to your HOA for you. <a href='../guide/can-my-hoa-stop-me-from-installing-artificial-turf/'>How the two laws work</a>.</p>"),
      ("Built for <b>this climate.</b>", METHOD + "<p>Turf in full summer sun does get hotter than grass. We'll bring samples and talk through shade, product choice and placement before you decide.</p>"),
    ]
    fx = CITY_FOCUS.get(a)
    if fx: secs[0:1] = fx["secs"]
    vids = []
    ps = [p for p in PJ.PROJECTS if p["city"].startswith(a + ",")]
    if ps: secs.insert(3 if fx else 1, cards(ps, "../", f"Projects in <b>{a}.</b>"))  # focus pages: after the waterfront section
    if a in CITY_VIDEOS:
        vids, h = CITY_VIDEOS[a]; secs.insert(1, vblock(vids, "../", h)); PAGE_VIDEOS[path] = vids
    secs.append(pstrip(PC.CITY[a], "../", link=True))
    near = [p for s_ in NEAR[a] for p in PJ.PROJECTS if p["slug"] == s_ and p not in ps]
    if near: secs.append(cards(near, "../", f"Jobs near <b>{a}.</b>", "Nearby"))
    if a in HOODS_OF:
        secs.append((f"Neighborhoods we serve in <b>{a}.</b>", "<ul>" + "".join(f'<li><a href="{h["slug"]}/">Artificial turf in {h["name"]}</a></li>' for h in HOODS_OF[a]) + "</ul>"))
    rel = [(x["nav"], x["slug"] + "/") for x in SERVICES] + [(b, CITY[b][0] + "/") for b in AREAS if b != a]
    biz = dict(org()); biz["@id"] = BASE + path + "#area"; biz["areaServed"] = {"@type": "City", "name": a + ", FL"}
    fx = fx or {}
    page(path, fx.get("title", f"Artificial Turf & Putting Greens, {a} FL | AJ Turf"),
         fx.get("desc", f"Turf lawns, pet turf and putting greens for {a} homes, installed with a glued concrete border and no spikes. Free onsite estimate."),
         a, fx.get("h1", f"Turf in<br><b>{a}.</b>"), fx.get("lede", f"Artificial turf, pet turf and putting greens for {a} homes. Free onsite estimate, then one exact price."),
         img, secs, [biz, crumbs([("AJ Turf", ""), (a, path)])] + [vobj(v) for v in vids], rel, f"Artificial turf and putting greens in {a}", slug, faq=city_faq(a))
    urls.append(path)

COST_TABLE = ("<table><thead><tr><th>Project</th><th>Installed price</th><th>Notes</th></tr></thead><tbody>"
    "<tr><td>Artificial turf lawn</td><td>$9 to $15 / sq ft</td><td>New installs start at 1,000 sq ft</td></tr>"
    "<tr><td>Backyard putting green</td><td>$9 to $15 / sq ft</td><td>Putting surface plus fringe, play-tested before handoff</td></tr>"
    "<tr><td>Pet turf</td><td>$9 to $15 / sq ft</td><td>Drainage-first base, pet-friendly infill</td></tr>"
    "<tr><td>Pool and paver turf</td><td>$9 to $15 / sq ft</td><td>Glued edges, cut tight to the stone</td></tr>"
    "<tr><td>Turf repair</td><td>Priced per job</td><td>Free onsite assessment, no minimum job size</td></tr>"
    "</tbody></table><p>The exact price comes after a free onsite estimate: one written number, never a price promised on the spot.</p>")
for h in HOOD:
    a = h["city"]; cslug = CITY[a][0]; path = f"{cslug}/{h['slug']}/"; n = h["name"]
    secs = [(f"Turf in <b>{n}.</b>", f"<p>{h['local']}</p><p>AJ Turf installs artificial turf lawns, backyard putting greens, pet turf and turf around pools and pavers in {n} and across {a}. "
             "Every job starts with a free onsite estimate: we measure and photograph in person, then follow up with one exact written price.</p>"
             "<ul>" + "".join(f'<li><b><a href="../../{x["slug"]}/" style="color:inherit">{x["title"]}</a></b></li>' for x in SERVICES) + "</ul>")]
    secs += h["notes"]
    secs += [(f"What it <b>costs.</b>", COST_TABLE), ("How we <b>build it.</b>", METHOD)]
    secs.append(("Keep <b>exploring.</b>", f"<ul><li><a href='../'>Artificial turf in {a}</a></li><li><a href='../../putting-greens/'>Backyard putting greens</a></li>"
                 "<li><a href='../../pet-turf/'>Pet turf</a></li><li><a href='../../turf-repair/'>Turf repair</a></li>"
                 "<li><a href='../../guide/how-much-does-artificial-turf-cost-in-southwest-florida/'>What artificial turf costs in Southwest Florida</a></li></ul>"))
    rel = [(x["nav"], x["slug"] + "/") for x in SERVICES] + [(a, cslug + "/")] + [(o["name"], f"{cslug}/{o['slug']}/") for o in HOODS_OF[a] if o is not h]
    biz = dict(org()); biz["@id"] = BASE + path + "#area"; biz["areaServed"] = {"@type": "Place", "name": f"{n}, {a}, FL"}
    page(path, f"Artificial Turf & Putting Greens in {n}, {a} | AJ Turf",
         f"Turf lawns, putting greens and pet turf for {n} homes in {a}. $9 to $15 a square foot installed, glued concrete border, no spikes. Free onsite estimate.",
         f'<a href="../../{cslug}/">{a}</a> / {n}', f"Turf in<br><b>{n}.</b>", f"Artificial turf and backyard putting greens for {n} homes. Free onsite estimate, then one exact price.",
         h["img"], secs, [biz, crumbs([("AJ Turf", ""), (a, cslug + "/"), (n, path)])], rel, f"Artificial turf in {n}, {a}", cslug, faq=city_faq(n).replace("../", "../../"))
    urls.append(path)

# Our Work: the proof hub YouTube descriptions and bios point to. A CTA band follows every 3 cards.
OW_TITLE, OW_H = "Recent Work — Watch Our Installs | AJ Turf, Southwest Florida", "Real installs,<br><b>on video.</b>"
groups = [OUR_WORK[i:i + 3] for i in range(0, len(OUR_WORK), 3)]
page("our-work/", OW_TITLE, "Watch real AJ Turf installs: whole-property tours, a putting green built start to finish, and the install method on the job. Free onsite estimate.",
     "Our work", OW_H, "Walk finished yards and watch the method on real jobs. When you're ready, we'll measure yours for free.", "green-canal-tiki",
     [cards([p for p in PJ.PROJECTS if a in (p["app"], p.get("also"))], "../", h, "By type of job") for a, h, _ in PJ.APPS] + [vblock(g, "../", h) for g, h in zip(groups, ["Watch the <b>installs.</b>", "More <b>jobs.</b>", "Start to <b>finish.</b>"])],
     [crumbs([("AJ Turf", ""), ("Our work", "our-work/")])] + [vobj(v) for v in OUR_WORK],
     [(x["nav"], x["slug"] + "/") for x in SERVICES] + [(a, CITY[a][0] + "/") for a in AREAS[:3]], "Real AJ Turf installs, on video", "our-work")
PAGE_VIDEOS["our-work/"] = OUR_WORK
urls.append("our-work/")

# /videos/: every channel upload, grouped. Plays in YouTube's own player, so each play counts on the channel (Jereme 10/13).
def vgroup(v):
    t = VIDEOS[v][0].lower()
    if any(k in t for k in ("method", "putting green", "first job", "how we")): return 1
    if any(k in t for k in ("dog", "pet", "rooftop", "commercial")): return 2
    return 0
VGROUPS = ["Project walkthroughs & <b>tours.</b>", "How we <b>install.</b>", "Pet turf & <b>specialty.</b>"]
VGROUP_SVC = [("Artificial turf lawns", "artificial-turf-installation"), ("Putting greens", "putting-greens"), ("Pet turf", "pet-turf")]
_vids = sorted((v for v in VIDEOS if v not in HIDDEN), key=lambda v: VIDEOS[v][3], reverse=True)
_vsec = "".join(
    f'<section class="work"><header><h2>{h}</h2><a class="mono" href="../{VGROUP_SVC[i][1]}/" style="color:var(--turf)">{VGROUP_SVC[i][0]} →</a></header><div class="vgrid">'
    + "".join(vcard(v, "../", job=True) for v in _vids if vgroup(v) == i) + "</div>" + (vcta() if n == 0 else "") + "</section>"
    for n, (i, h) in enumerate((i, h) for i, h in enumerate(VGROUPS) if any(vgroup(v) == i for v in _vids)))
_vschema = {"@context": "https://schema.org", "@graph": [org(), crumbs([("AJ Turf", ""), ("Videos", "videos/")]),
            {"@type": "CollectionPage", "name": "AJ Turf videos", "url": BASE + "videos/"}] + [vobj(v) for v in _vids]}
os.makedirs("videos", exist_ok=True)
open("videos/index.html", "w", encoding="utf-8").write(head("Artificial Turf Install Videos | AJ Turf, Southwest Florida",
    "Watch real AJ Turf installs: finished-yard tours, the install method on the job, a putting green built start to finish, and pet turf.",
    "videos/", 1, _vschema, "AJ Turf on video", "our-work") + f"""
<header class="sub-hero" style="min-height:58vh"><img src="../img/green-canal-tiki.webp" alt="">
  <div class="in"><span class="mono crumbs"><a href="../">AJ Turf</a> / Videos</span><h1>Watch real installs,<br><b>start to finish.</b></h1>
  <p class="lede">Finished yards, the install method on the job, and builds from start to finish. Every video is ours, from our YouTube channel. <a class="mono" href="https://www.youtube.com/@AJTurf" target="_blank" rel="noopener" style="color:inherit;font-size:12px;white-space:nowrap">Subscribe on YouTube →</a></p>
  <p class="vid-cta" style="margin-top:28px;padding:0"><a class="book" href="{BOOK}" target="_blank" rel="noopener">Book a free estimate <span aria-hidden="true">→</span></a><a class="alt mono" href="tel:{PHONE_HREF}" style="color:var(--white)">Or call {PHONE}</a><a class="alt mono" href="sms:{PHONE_HREF}" style="color:var(--white)">Or text us</a></p></div></header>
<main>{_vsec}{vcta().replace('class="vid-cta"', 'class="vid-cta" style="padding-bottom:clamp(60px,8vw,110px)"')}</main>
""" + close(1))
PAGE_VIDEOS["videos/"] = _vids
urls.append("videos/")

# Project pages: one per staged set, application first, city as a label
def vmeta(p, sfx=""):
    # self-hosted clip (vid/w/<slug><sfx>.mp4, encoded from the staged master); poster + duration for the player and VideoObject
    mp4 = f"vid/w/{p['slug']}{sfx}.mp4"; base, w, h, _, _ = poster(p, sfx)
    d = float(subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", mp4], capture_output=True, text=True).stdout)
    return mp4, base + "-800.webp", round(d), w, h

def project_page(p):
    r, path = "../../", p["path"]
    t = re.sub(r"<[^>]+>", "", p["title"]).replace("&amp;", "&")
    app = next(h for a, h, _ in PJ.APPS if a == p["app"]); app_txt = re.sub(r"<[^>]+>", "", app).replace("&amp;", "&").rstrip(".")
    svc = next(x for a, _, x in PJ.APPS if a == p["app"])
    fin = [i for i in p["imgs"] if i[4] in "FD"]; pre = [i for i in p["imgs"] if i[4] in "BP"]
    graph = [org(), crumbs([("AJ Turf", ""), ("Our work", "our-work/"), (f"{t}, {p['city']}", path)])]
    body = ""
    if p.get("ba"):
        (bb, bw, bh, bbig), (ab, aw, ah, abig) = p["ba"]
        body += (f'<section class="work"><header><h2>Before &amp; <b>after.</b></h2><span class="mono" style="color:var(--stone)">Drag to compare</span></header>'
                 f'<div class="ba" style="--p:50%;aspect-ratio:{aw}/{ah}"><img src="{r}{ab}-{1600 if abig else 800}.webp" alt="After: {t.lower()} in {p["city"]}" loading="lazy">'
                 f'<div class="ba-b"><img src="{r}{bb}-{1600 if bbig else 800}.webp" alt="Before: the same view before the install" loading="lazy"></div>'
                 f'<span class="mono ba-l">Before</span><span class="mono ba-r">After</span>'
                 f'<input type="range" min="0" max="100" value="50" aria-label="Drag to compare before and after"></div>'
                 f'<p class="mono ba-cap">{p["slider"][2]}</p>{vcta()}</section>')
    if fin: body += (f'<section class="work"><header><h2>The finished <b>job.</b></h2><span class="mono" style="color:var(--stone)">Tap a photo to enlarge</span></header>'
             f'<div class="pgrid">{"".join(gfig(p, i, r, n, len(fin)) for n, i in enumerate(fin, 1))}</div>{vcta()}</section>')
    # held_silent: audio had to come off (private talk / music) and Jereme ruled no silent video (10/11) -> off the page until it has a cleared music bed
    clips = [(sfx, v) for sfx, v in (("", p.get("video")), ("-2", p.get("video2"))) if v and not (sfx == "" and p.get("held_silent"))]
    for sfx, v in clips:
        mp4, poster, sec, pw, ph = vmeta(p, sfx)
        body += ((f'<section class="work"><header><h2>On <b>video.</b></h2></header>' if sfx == "" or len(clips) == 1 else '<section class="work">') +
                 f'<div class="pvid"><video controls preload="none" playsinline '
                 f'poster="{r}{poster}" width="{pw}" height="{ph}" aria-label="{v[1]}: {t.lower()} in {p["city"]}"><source src="{r}{mp4}" type="video/mp4"></video>'
                 f'<p class="mono">{v[1]} · {p["city"]}</p></div>{vcta()}</section>')
        graph.append({"@type": "VideoObject", "name": f"{t}, {p['city']}: {v[1].lower()}", "description": p["blurb"],
                      "thumbnailUrl": BASE + poster, "contentUrl": BASE + mp4, "uploadDate": TODAY, "duration": f"PT{sec // 60}M{sec % 60}S"})
    if p.get("youtube"):
        body += vblock([p["youtube"]], r, "On <b>video.</b>"); graph.append(vobj(p["youtube"])); PAGE_VIDEOS[path] = [p["youtube"]]
    if pre:
        body += (f'<section class="work"><header><h2>Before &amp; <b>during.</b></h2><span class="mono" style="color:var(--stone)">Not the finished job</span></header>'
                 f'<div class="pgrid">{"".join(gfig(p, i, r, n, len(pre)) for n, i in enumerate(pre, 1))}</div>{vcta()}</section>')
    facts = f'<ul><li><b>Type of job:</b> {app_txt}</li><li><b>Where:</b> {p["city"]}</li>' + (f'<li><b>When:</b> {p["when"]}</li>' if p["when"] else "") + "</ul>"
    if svc: facts += f'<p><a href="{r}{svc}/" style="color:var(--turf)">More about {next(x["title"] for x in SERVICES if x["slug"] == svc).lower()} →</a></p>'
    body += f'<section class="prose"><h2>About this <b>job.</b></h2><div class="body"><p>{p["blurb"]}</p>{facts}</div></section>'
    more = [q for q in PJ.PROJECTS if q is not p and q["app"] == p["app"]][:4]
    if more: body += cards(more, r, f"More {app_txt.lower()}", "Keep looking")
    hb, hw, hh, hbig, _ = p["hero"]
    desc = f"{t} in {p['city']} by AJ Turf: photos{' and video' if (p.get('video') and not p.get('held_silent')) or p.get('youtube') else ''} from a real job. Free onsite estimate, then one exact price."
    html = head(f"{t}, {p['city']} | AJ Turf Project", desc, path, 2, {"@context": "https://schema.org", "@graph": graph}, f"{t}, {p['city']}", "proj-" + p["slug"]) + f'''
<header class="sub-hero">
  <img src="{r}{hb}-{1600 if hbig else 800}.webp" alt="" fetchpriority="high">
  <div class="in"><span class="mono crumbs"><a href="{r}">AJ Turf</a> / <a href="{r}our-work/">Our work</a> / {app_txt}</span>
    <h1>{p["title"]}<br><b>{p["city"]}.</b></h1><p class="lede">{p["blurb"]}</p>
    <p style="margin-top:28px"><a class="book" href="{BOOK}" target="_blank" rel="noopener">Book a free estimate <span aria-hidden="true">→</span></a></p></div>
</header>
<main>{body}</main>
''' + close(2)
    os.makedirs(path, exist_ok=True); open(path + "index.html", "w", encoding="utf-8").write(html)
    urls.append(path)
for p in PJ.PROJECTS: project_page(p)

# Turf Guide
from guide_content import GUIDES
from kb_pages import PILLAR as _PL, QUESTION_PILLAR as _QP
PILLAR_OF = {s: _PL[pl] for s, pl in _QP.items()}
def BEACH(r):  # Google's chosen install page: link it hard to the service pages and the near-page-one questions
    qs = "".join(f'<li><a href="{r}guide/{s}/">{gtitle(s)}</a></li>' for s in CLUSTER)
    return (f'<h2>Want it built this way?</h2><p>These are the steps behind our <a href="{r}artificial-turf-installation/">artificial turf installation</a> '
            f'in Southwest Florida, from Fort Myers to Naples. Turf already in and failing? See <a href="{r}turf-repair/">turf repair</a>: we fix installs '
            f'whoever put them in. Most installs run $9 to $15 a square foot, with one exact price after a free onsite estimate.</p>'
            f'<h2>Where we install</h2><ul>' + "".join(f'<li><a href="{r}{CITY[a][0]}/">Artificial turf installation in {a}</a></li>' for a in AREAS) + '</ul>'
            f'<h2>Common install questions</h2><ul>{qs}</ul>')
def REPAIR_CTA(r):
    return (f'<h2>Seeing this in your yard?</h2><p>That\'s what our <a href="{r}turf-repair/">artificial turf repair</a> service is for: '
            f'ripples, seams, washouts, drainage and odor problems fixed, whoever installed the turf, or a full re-install when a repair isn\'t worth it. '
            f'Every repair starts with a free onsite assessment, and repairs have no minimum job size.</p>')
def article(g):
    path = f"guide/{g['slug']}/"; r = "../../"
    faq = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": g["q"], "acceptedAnswer": {"@type": "Answer", "text": g["a"]}}]}
    art = {"@type": "Article", "headline": g["title"], "description": g["desc"], "datePublished": TODAY, "dateModified": TODAY,
           "author": {"@id": BASE + "#business"}, "publisher": {"@id": BASE + "#business"}, "mainEntityOfPage": BASE + path,
           "image": BASE + f"img/og/guide-{g['slug']}.jpg"}
    howto = []
    if g["slug"] == "how-artificial-turf-is-installed":  # GEO plan §2.2: HowTo on the install anchor, text = visible step text
        steps = _re.findall(r"<h2>\d\.\s*(.*?)</h2>\s*<p>(.*?)</p>", g["body"], _re.S)
        howto = [{"@type": "HowTo", "name": g["title"], "description": g["a"], "step": [{"@type": "HowToStep", "position": i + 1,
                  "name": _re.sub(r"<[^>]+>", "", n), "text": _re.sub(r"<[^>]+>", "", t)} for i, (n, t) in enumerate(steps)]}]
    schema = {"@context": "https://schema.org", "@graph": [org(), art, faq] + howto + [crumbs([("AJ Turf", ""), ("Turf Guide", "guide/")] + ([(PILLAR_OF[g["slug"]]["nav"], f"guide/{PILLAR_OF[g['slug']]['slug']}/")] if g["slug"] in PILLAR_OF else []) + [(g["title"], path)])]}
    others = "".join(f'<li><a href="{r}guide/{x["slug"]}/">{x["title"]}</a></li>' for x in GUIDES if x is not g)
    src = "".join(f"<li>{x}</li>" for x in g["sources"])
    html = head(g["seo"], g["desc"], path, 2, schema, g["title"], "guide-" + g["slug"]) + f"""
<header class="sub-hero" style="min-height:62vh">
  <img src="{r}img/{g['img']}.webp" alt="">
  <div class="in"><span class="mono crumbs"><a href="{r}">AJ Turf</a> / <a href="{r}guide/">Turf Guide</a></span>
    <h1 style="font-size:clamp(38px,5.6vw,84px)">{g['title']}</h1></div>
</header>
<div class="art-wrap"><main class="article">
  <p class="mono" style="color:var(--turf)">The short answer</p>
  <p class="short">{g['a']}</p>
  <div class="art-body">{g['body']}{BEACH(r) if g["slug"] == "how-artificial-turf-is-installed" else ""}</div>
  <div class="sources"><p class="mono">Sources</p><ul>{src}</ul><p class="mono" style="margin-top:14px">Updated {TODAY}</p></div>
</main>
<aside class="toc"><p class="mono">In this guide</p><ol>{"".join(f"<li>{_re.sub(r'<[^>]+>','',t)}</li>" for t in _re.findall(r"<h2>(.*?)</h2>", g["body"]))}</ol>
<a class="book" href="{BOOK}" target="_blank" rel="noopener" style="margin-top:26px;font-size:16px;padding:14px 20px">Free onsite estimate <span aria-hidden="true">→</span></a></aside></div>
{pstrip(PC.GUIDE[g["slug"]], r, "From real <b>jobs.</b>") if g["slug"] in PC.GUIDE else ""}
<section class="related"><span class="mono" style="color:var(--turf)">More from the Turf Guide</span><ul>{others}</ul></section>
""" + close(2)
    os.makedirs(path, exist_ok=True); open(path + "index.html", "w", encoding="utf-8").write(html)
    urls.append(path)
for g in (GUIDES if PUBLISH_GUIDE else []): article(g)

# ---- Turf Guide knowledge hub (GEO plan, Muse KB 10/13): hub -> 5 pillars -> question pages ----
import markdown as _md
from kb_pages import PILLARS, PILLAR, QUESTION_PILLAR
_KBI = json.load(open("kb_src/index.json", encoding="utf-8"))
AUTHOR = {"@type": "Person", "name": "Jereme Strange", "worksFor": {"@id": BASE + "#business"}}
PILLAR_SERVICE = {"turf-product-science": ("Pet turf", "pet-turf/"), "turf-installation": ("Artificial turf installation", "artificial-turf-installation/"),
                  "turf-ownership": ("Turf repair", "turf-repair/"), "buying-artificial-turf": ("Artificial turf installation", "artificial-turf-installation/"),
                  "artificial-turf-in-florida": ("Artificial turf in Fort Myers", "fort-myers/")}
QVIDEO = {"concrete-border-vs-spikes": ("aATUhfArpEY", "The method, <b>on a real job.</b>"),
          "best-artificial-turf-for-dogs-in-florida": ("VXatdDEOrdw", "A dog run, <b>on video.</b>"),
          "how-fast-does-a-turf-putting-green-roll": ("IhduTxos9As", "A green, <b>start to finish.</b>")}  # GEO plan §6.2: proof footage on its page
QPAGES = []  # (slug, title) of every question page, in pillar order, for the hub + pillars
_plain = lambda s: _re.sub(r"<[^>]+>", "", s)
_inline = lambda s: _md.markdown(s).removeprefix("<p>").removesuffix("</p>")

def kb_question(slug):
    src = open(f"kb_src/{slug}.md", encoding="utf-8").read()
    title = re.search(r"^# (.+)$", src, re.M).group(1).strip()
    answer = re.search(r"^\*\*The answer:\*\* (.+)$", src, re.M).group(1).strip()
    body = src.split("**The answer:**", 1)[1].split("\n", 1)[1]
    faq_md = body.split("## FAQ", 1)[1] if "## FAQ" in body else ""
    body = body.split("## Related questions")[0].split("## FAQ")[0]
    qa = re.findall(r"^\*\*(.+?\?)\*\*\n(.+?)(?=\n\n|\Z)", faq_md, re.M | re.S)
    return title, _inline(answer), _md.markdown(body, extensions=["tables"]), [(_inline(q), _inline(a.strip())) for q, a in qa]

def question_page(slug):
    title, answer, body_html, qa = kb_question(slug)
    meta = _KBI[slug]; p = PILLAR[QUESTION_PILLAR[slug]]
    path = f"guide/{slug}/"; r = "../../"
    faq_html = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in qa)
    graph = [org(), {"@type": "Article", "headline": title, "description": meta["Suggested meta description"], "datePublished": TODAY,
             "dateModified": TODAY, "author": AUTHOR, "publisher": {"@id": BASE + "#business"}, "mainEntityOfPage": BASE + path,
             "image": BASE + f"img/og/guide-{slug}.jpg"},
             crumbs([("AJ Turf", ""), ("Turf Guide", "guide/"), (p["nav"], f"guide/{p['slug']}/"), (title, path)])]
    vid = QVIDEO.get(slug)
    if vid: graph.append(vobj(vid[0])); PAGE_VIDEOS[path] = [vid[0]]
    if qa:
        graph.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": _plain(q), "acceptedAnswer": {"@type": "Answer", "text": _plain(a)}} for q, a in qa]})
    sibs = [(s, t) for s, t in QPAGES if s != slug and QUESTION_PILLAR[s] == p["slug"]][:3]
    svc = PILLAR_SERVICE[p["slug"]]
    rel = "".join(f'<li><a href="{r}guide/{s}/">{t}</a></li>' for s, t in sibs)
    rel += f'<li><a href="{r}guide/{p["slug"]}/">{p["title"].split(":")[0]}</a></li><li><a href="{r}{svc[1]}">{svc[0]}</a></li>'
    toc = "".join(f"<li>{_plain(t)}</li>" for t in _re.findall(r"<h2>(.*?)</h2>", body_html))
    faq_block = f'<div class="art-faq"><h2>Questions people <b>ask.</b></h2>{faq_html}</div>' if qa else ""
    page_html = head(meta["Suggested meta title"], meta["Suggested meta description"], path, 2, {"@context": "https://schema.org", "@graph": graph}, title, "guide-" + slug) + f"""
<header class="sub-hero" style="min-height:62vh">
  <img src="{r}img/{p['img']}.webp" alt="">
  <div class="in"><span class="mono crumbs"><a href="{r}">AJ Turf</a> / <a href="{r}guide/">Turf Guide</a> / <a href="{r}guide/{p['slug']}/">{p['nav']}</a></span>
    <h1 style="font-size:clamp(34px,5vw,74px)">{title}</h1></div>
</header>
<div class="art-wrap"><main class="article">
  <p class="byline mono">By Jereme Strange, AJ Turf · years on the manufacturing side of the turf industry, and years installing and repairing turf in Florida</p>
  <p class="mono" style="color:var(--turf)">The short answer</p>
  <p class="short">{answer}</p>
  <div class="art-body">{body_html}{REPAIR_CTA(r) if slug in REPAIR_Q else ""}</div>
  {faq_block}
  <p class="mono" style="margin-top:30px;color:var(--stone)">Updated {TODAY}</p>
</main>
<aside class="toc"><p class="mono">In this guide</p><ol>{toc}</ol>
<a class="book" href="{BOOK}" target="_blank" rel="noopener" style="margin-top:26px;font-size:16px;padding:14px 20px">Free onsite estimate <span aria-hidden="true">→</span></a></aside></div>
{vblock([vid[0]], r, vid[1]) if vid else ""}
<section class="related"><span class="mono" style="color:var(--turf)">Keep reading</span><ul>{rel}</ul></section>
""" + close(2)
    os.makedirs(path, exist_ok=True); open(path + "index.html", "w", encoding="utf-8").write(page_html)
    urls.append(path)

for p in PILLARS:  # question list per pillar: the existing guides + the new KB pages
    for s, pl in QUESTION_PILLAR.items():
        if pl == p["slug"]:
            t = next((x["title"] for x in GUIDES if x["slug"] == s), None) or re.search(r"^# (.+)$", open(f"kb_src/{s}.md", encoding="utf-8").read(), re.M).group(1)
            QPAGES.append((s, t))
for s in _KBI: question_page(s)

def pillar_page(p):
    path = f"guide/{p['slug']}/"; r = "../../"
    qs = [(s, t) for s, t in QPAGES if QUESTION_PILLAR[s] == p["slug"]]
    items = "".join(f'<li><a href="{r}guide/{s}/">{t}</a></li>' for s, t in qs)
    others = "".join(f'<li><a href="{r}guide/{x["slug"]}/">{x["title"].split(":")[0]}</a></li>' for x in PILLARS if x is not p)
    graph = [org(), crumbs([("AJ Turf", ""), ("Turf Guide", "guide/"), (p["nav"], path)]),
             {"@type": "CollectionPage", "name": p["title"], "url": BASE + path, "description": p["lead"], "author": AUTHOR,
              "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": BASE + f"guide/{s}/", "name": t} for i, (s, t) in enumerate(qs)]}}]
    toc = "".join(f"<li>{_plain(t)}</li>" for t in _re.findall(r"<h2>(.*?)</h2>", p["body"]))
    qblock = f'<div class="art-qs"><h2>Questions in this <b>section.</b></h2><ul>{items}</ul></div>' if qs else ""
    page_html = head(p["title"] + " | AJ Turf", p["lead"][:155], path, 2, {"@context": "https://schema.org", "@graph": graph}, p["title"].split(":")[0], "home") + f"""
<header class="sub-hero" style="min-height:58vh"><img src="{r}img/{p['img']}.webp" alt="">
  <div class="in"><span class="mono crumbs"><a href="{r}">AJ Turf</a> / <a href="{r}guide/">Turf Guide</a> / {p['nav']}</span><h1>{p['h1']}</h1></div></header>
<div class="art-wrap"><main class="article">
  <p class="byline mono">By Jereme Strange, AJ Turf</p>
  <p class="mono" style="color:var(--turf)">The short answer</p>
  <p class="short">{p['lead']}</p>
  <div class="art-body">{p['body']}</div>
  {qblock}
</main>
<aside class="toc"><p class="mono">In this section</p><ol>{toc}</ol>
<a class="book" href="{BOOK}" target="_blank" rel="noopener" style="margin-top:26px;font-size:16px;padding:14px 20px">Free onsite estimate <span aria-hidden="true">→</span></a></aside></div>
<section class="related"><span class="mono" style="color:var(--turf)">More of the Turf Guide</span><ul>{others}</ul></section>
""" + close(2)
    os.makedirs(path, exist_ok=True); open(path + "index.html", "w", encoding="utf-8").write(page_html)
    urls.append(path)
for p in PILLARS: pillar_page(p)

def _hub_item(p):
    qs = "".join(f'<li><a href="{s}/">{t}</a></li>' for s, t in QPAGES if QUESTION_PILLAR[s] == p["slug"])
    return (f'<li class="pillar"><a class="pillar-h" href="{p["slug"]}/"><span class="mono">{p["letter"]} · {p["nav"]}</span>'
            f'<h3>{p["h1"]}</h3><p>{p["lead"]}</p></a><ul>{qs}</ul></li>')
_hub_graph = [org(), crumbs([("AJ Turf", ""), ("Turf Guide", "guide/")]),
    {"@type": "CollectionPage", "name": "The AJ Turf Guide", "url": BASE + "guide/", "author": AUTHOR,
     "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": BASE + f"guide/{p['slug']}/", "name": p["title"]} for i, p in enumerate(PILLARS)]}}]
os.makedirs("guide", exist_ok=True)
open("guide/index.html", "w", encoding="utf-8").write(head("Turf Guide: Straight Answers About Artificial Turf | AJ Turf",
    "Everything about artificial turf in one place: what it's made of, how it should be installed, owning it, buying it, and Florida's rules. From a Fort Myers installer.", "guide/", 1,
    {"@context": "https://schema.org", "@graph": _hub_graph}, "The AJ Turf Guide", "home") + f"""
<header class="sub-hero" style="min-height:58vh"><img src="../img/backyard-wide.webp" alt="">
  <div class="in"><span class="mono crumbs"><a href="../">AJ Turf</a> / Turf Guide</span><h1>Straight answers<br>about <b>turf.</b></h1>
  <p class="lede">From both sides of the business: how turf is made and how it should be installed. Plain answers, real numbers, and the honest downsides.</p></div></header>
<main class="hub"><ul class="pillars">{"".join(_hub_item(p) for p in PILLARS)}</ul></main>
""" + close(1))
urls.append("guide/")

# privacy
os.makedirs("privacy", exist_ok=True)
open("privacy/index.html", "w", encoding="utf-8").write(head("Privacy | AJ Turf", "How AJ Turf handles information you share with us.", "privacy/", 1,
    {"@context": "https://schema.org", "@graph": [org()]}) + f'''
<main style="padding:160px clamp(20px,6vw,90px) 100px;max-width:820px">
<h1 style="font-family:var(--display);font-weight:300;font-size:56px;letter-spacing:-.04em">Privacy</h1>
<p style="margin-top:24px">When you book an estimate, call, or message us, we use your name, phone, email and address only to schedule and complete your estimate and project. We don't sell or share your information. This site uses Google Analytics to count visits and see which pages help people; it uses no advertising trackers. The chat assistant on this site is an AI; your chat messages are kept for 90 days so we can follow up, so please don't share anything sensitive in it. To ask about or remove your information, email <a href="mailto:{EMAIL}">{EMAIL}</a> or call {PHONE}.</p>
<p style="margin-top:16px" class="mono">Updated {TODAY}</p>
</main>''' + close(1))
urls.append("privacy/")

from html import escape as _esc
def vsite(v):
    t, d, sec, date, _, _ = VIDEOS[v]
    return (f"<video:video><video:thumbnail_loc>{BASE}img/vid/{v}.webp</video:thumbnail_loc><video:title>{_esc(t)}</video:title>"
            f"<video:description>{_esc(d)}</video:description><video:player_loc>https://www.youtube.com/embed/{v}</video:player_loc>"
            + (f"<video:duration>{sec}</video:duration>" if sec else "") + f"<video:publication_date>{date}</video:publication_date></video:video>")
open("sitemap.xml", "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">\n' +
    "".join(f"  <url><loc>{BASE}{u}</loc><lastmod>{TODAY}</lastmod>{''.join(vsite(v) for v in PAGE_VIDEOS.get(u, []))}</url>\n" for u in urls) + "</urlset>\n")
open("robots.txt", "w").write("User-agent: *\nAllow: /\n\n" + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in
    ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "PerplexityBot", "Google-Extended", "Applebot-Extended", "Bingbot"]) +
    f"Sitemap: {BASE}sitemap.xml\n")
open("llms.txt", "w", encoding="utf-8").write(f"""# AJ Turf

> Artificial turf, pet turf, putting greens, pool and paver turf, and turf repair for homes in Southwest Florida: {", ".join(AREAS)}.

## Key facts
- Service: residential artificial turf installation, commercial and event lawns, pet turf, backyard putting greens with fringe, turf around pools and pavers, turf repair and re-installs.
- Install method: screening-sand base compacted to 95% Standard Proctor (ASTM D698), 6-inch metal or plastic edging, a 3 x 3 x 3 inch poured concrete border inside it, a woven weed barrier over everything, turf glued to the border with 15-year-warrantied glue. No spikes through the turf (spikes only pin the barrier and seam tape underneath).
- Pricing: most installs run $9 to $15 a square foot, depending on the turf and the site, putting greens included. Free onsite estimate, measured and photographed in person, then one exact written price in a follow-up. No exact price is ever promised on the spot.
- Warranty: Turf carries the manufacturer's warranty for the product you choose (8 to 25 years depending on the product), covering UV stability and strength; installation is covered by AJ Turf's 1-year labor warranty. Quotes include a standard cut allowance because turf comes in 15-foot-wide rolls.
- Payments: 30% to schedule, 35% on the first day on site, 35% at completion. Accepted: cash, PayPal, Venmo, or card (card payments carry a 3% fee). No Zelle.
- Owner on site: Jereme Strange, the owner, is on site for every job.
- Background: new to the West Coast, not new to the industry. Years on the manufacturing side of turf, and years installing and repairing turf in Florida.
- Putting greens: a premium specialty. A shaped, compacted base, a putting surface plus fringe cut and seamed by hand, and every green play-tested before handoff.
- Maintenance: AJ Turf sells no maintenance or cleaning plans. Year one: the 1-year labor warranty covers install-caused issues (infill settling, matted traffic areas, lifting seams or edges). Damage or failures after that go to turf repair.
- Timeline: about two days per 1,000 square feet. Installs are typically scheduled within two weeks, or on the client's preferred date. New installs start at 1,000 square feet; repairs have no minimum.
- Hours: Monday to Saturday, 9 to 5.
- Contact: {PHONE}, {EMAIL}. Book: {BOOK}

## Turf knowledge base
- [Turf Guide]({BASE}guide/): index of every guide, in five sections
""" + "".join(f"- [{x['title']}]({BASE}guide/{x['slug']}/): {x['lead'][:140]}...\n" for x in PILLARS)
  + "".join(f"- [{t}]({BASE}guide/{s}/)\n" for s, t in QPAGES) + f"""- [Videos]({BASE}videos/): every AJ Turf install video, playing from the AJ Turf YouTube channel

## Pages
""" + "".join(f"- {BASE}{u}\n" for u in urls))

# og images: one branded 1200x630 card per page, rendered from HTML so it matches the site type
import pathlib
from playwright.sync_api import sync_playwright
cards = [("home", "hero-after", "Turf that looks like it<br>was <b>always there.</b>")]
cards += [(x["slug"], x["img"], SEO[x["slug"]][3]) for x in SERVICES]
cards += [(CITY[a][0], CITY[a][2], f"Artificial turf in<br><b>{a}.</b>") for a in AREAS]
cards += [("our-work", "green-canal-tiki", OW_H)]
cards += [("proj-" + p["slug"], p["hero"][0][4:] + ("-1600" if p["hero"][3] else "-800"), f'{p["title"]}<br><b>{p["city"]}.</b>') for p in PJ.PROJECTS]
cards += [("guide-" + g["slug"], g["img"], g["title"]) for g in (GUIDES if PUBLISH_GUIDE else [])]
cards += [("guide-" + s, PILLAR[QUESTION_PILLAR[s]]["img"], dict(QPAGES)[s]) for s in _KBI]
os.makedirs("img/og", exist_ok=True)
root = pathlib.Path(".").resolve().as_uri() + "/"
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
    for slug, img, h in cards:
        open("_og.html","w",encoding="utf-8").write(f"""<html><head><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,300;12..96,700&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>body{{margin:0;width:1200px;height:630px;position:relative;overflow:hidden;font-family:'Bricolage Grotesque'}}img.bg{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.g{{position:absolute;inset:0;background:linear-gradient(90deg,rgba(18,22,19,.92) 0%,rgba(18,22,19,.55) 55%,rgba(18,22,19,.1) 100%)}}
.in{{position:absolute;left:64px;top:56px;bottom:56px;right:64px;display:flex;flex-direction:column;justify-content:space-between;color:#FAFBF9}}
.m{{display:flex;align-items:center;gap:14px;font-weight:700;font-size:30px;letter-spacing:-.02em}}.m span{{color:#4FB4C3}}
h1{{margin:0;font-weight:300;font-size:78px;line-height:.95;letter-spacing:-.045em;max-width:900px}}h1 b{{font-weight:700}}
p{{margin:0;font:500 17px 'JetBrains Mono';letter-spacing:.12em;color:#4FB4C3}}</style></head>
<body><img class="bg" src="img/{img}.webp"><div class="g"></div><div class="in"><div class="m"><img src="img/mark.svg" width="54">AJ<span>/</span>TURF</div>
<div><h1>{h}</h1><p style="margin-top:22px">FREE ONSITE ESTIMATE · FORT MYERS TO NAPLES</p></div></div></body></html>""")
        pg.goto(root + "_og.html")
        pg.wait_for_load_state("networkidle"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        pg.screenshot(path=f"img/og/{slug}.jpg", type="jpeg", quality=86)
    b.close()
os.remove("_og.html")
# home page is hand-built: refresh its reviews block between the markers
_h = open("index.html", encoding="utf-8").read()
_h = re.sub(r'(href="style\.css|src="site\.js)(\?v=\w+)?"', lambda m: f'{m.group(1)}?v={ASSET_V}"', _h)
_h = re.sub(r'"sameAs": \[[^\]]*\]', lambda m: '"sameAs": ' + json.dumps(org()["sameAs"]), _h)
_h = re.sub(r"<!--FINDUS-->.*?<!--/FINDUS-->", lambda m: "<!--FINDUS-->" + FIND_US + "<!--/FINDUS-->", _h, flags=re.S)
_h = re.sub(r"<!--REVIEWS-->.*?<!--/REVIEWS-->", lambda m: "<!--REVIEWS-->" + reviews_block(6) + "<!--/REVIEWS-->", _h, flags=re.S)
open("index.html", "w", encoding="utf-8").write(_h)
print(len(urls), "urls,", len(cards), "og cards")
