# Generates service + city pages, sitemap, robots, llms.txt for the AJ Turf site.
# Run: python gen.py   (home page index.html is hand-built; this only writes the rest)
import json, os, datetime
from PIL import Image

BASE = "https://ajturffl.com/"  # ponytail: swap to the real domain when it exists
PHONE, PHONE_HREF = "305-762-9901", "+13057629901"
EMAIL = "ajturffl@gmail.com"
PUBLISH_GUIDE = True   # flip to True when Jereme approves the Turf Guide
BOOK = "https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ2DTv90ZIlO1yxFsxeEcVhJxtTSvLrjRpB3xc9llHbTBaQ1nFWr8KTX7mevE-Gx56R-V1wuX7ax"
TODAY = datetime.date.today().isoformat()
AREAS = ["Fort Myers", "Cape Coral", "Naples", "Estero", "Bonita Springs", "Sanibel", "Lehigh Acres"]

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
OUR_WORK = ["4j__CUFYhnQ", "3yovFZ8U0ns", "IhduTxos9As", "aATUhfArpEY", "LgpH3u-eJ6A", "HgPybt3IXWA"]
CITY_VIDEOS = {"Fort Myers": (["3yovFZ8U0ns"], "A finished Fort Myers <b>lawn.</b>")}  # geo-matched only: the video's city = the page's city
SERVICE_VIDEOS = {"putting-greens": (["IhduTxos9As"], "Watch one <b>go in.</b>"), "pool-and-paver-turf": (["LgpH3u-eJ6A"], "Waterfront, <b>on the job.</b>")}

def vcard(v, r):
    t, _, _, _, tall, cap = VIDEOS[v]
    return (f'<figure class="vid{"" if tall else " wide"}"><button class="yt" data-id="{v}" data-title="{t}" aria-label="Play video: {t}">'
            f'<img src="{r}img/vid/{v}.webp" alt="" loading="lazy"><span class="play"></span></button><figcaption class="cap mono">{cap}</figcaption></figure>')

def vcta():
    return f'<p class="vid-cta"><a class="book" href="{BOOK}" target="_blank" rel="noopener">Book a free estimate <span aria-hidden="true">→</span></a><a class="alt mono" href="tel:{PHONE_HREF}">Or call {PHONE}</a></p>'

def vblock(ids, r, h2):
    # no orphan video: the booking CTA sits directly under every player
    return (f'<section class="work"><header><h2>{h2}</h2></header><div class="strip">' + "".join(vcard(v, r) for v in ids) + "</div>" + vcta() + "</section>")

def vobj(v):
    t, d, s, date, _, _ = VIDEOS[v]
    return {"@type": "VideoObject", "name": t, "description": d, "thumbnailUrl": BASE + f"img/vid/{v}.webp", "uploadDate": date,
            "duration": f"PT{s // 60}M{s % 60}S", "embedUrl": f"https://www.youtube.com/embed/{v}"}

HOME_VIDEOS = ["4j__CUFYhnQ", "3yovFZ8U0ns", "aATUhfArpEY"]  # embedded by hand in index.html
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

def pstrip(items, r, h2="Real <b>jobs.</b>", style=' style="padding-top:clamp(70px,10vw,140px)"'):
    # every photo gallery ends at the booking CTA
    return (f'<section class="work"{style}><header><h2>{h2}</h2><span class="mono" style="color:var(--stone)">Drag to see more →</span></header>'
            f'<div class="strip">' + "".join(fig(x, r) for x in items) + "</div>" + vcta() + "</section>")

METHOD = ("<p>Every AJ Turf install is built the same way. We outline the area with 6-inch metal or plastic edging, "
          "pour a 3 x 3 x 3 inch concrete border along the inside of it, lay a weed barrier over everything, then glue the "
          "turf edges to the concrete with turf glue that carries a 15-year warranty.</p>"
          "<p>Most installers pin turf down with 6-inch steel spikes driven through the whole lawn. Spikes work loose, can hurt "
          "bare feet and paws, and tear the backing over time. A glued edge is safer and lasts longer.</p>")

FAQ_BLOCK = """<details><summary>How do you price a yard?</summary><p>In person. We measure on site and give you one exact written price, and the estimate is free. Turf comes in 15-foot-wide rolls, so every quote includes a standard allowance for cuts around your yard's shape.</p></details>
<details><summary>How long does an install take?</summary><p>About two days for every 1,000 square feet, depending on the site.</p></details>
<details><summary>How do payments work?</summary><p>30% to put your install on the schedule, 35% on the first day on site, and the last 35% when the job is done and you've walked it with us.</p></details>
<details><summary>Why a concrete border instead of spikes?</summary><p>Spikes driven through a lawn can work loose, hurt bare feet and paws, and tear the turf backing. Gluing the turf edge to a poured concrete border holds it down without anything sticking up, and it lasts longer.</p></details>
<details><summary>What happens to my sprinklers?</summary><p>Existing sprinkler heads are capped and left in place, not ripped out. That keeps your system intact, and a quick run of water is an easy way to rinse and cool the turf on hot days.</p></details>
<details><summary>What's the warranty?</summary><p>Turf carries the manufacturer's warranty for the product you choose (8, 16 or 25 years depending on the product), covering UV stability and strength; installation is covered by AJ Turf's 1-year labor warranty. You'll see the exact warranty for your product before you sign.</p></details>
"""

SEO = {'artificial-turf-installation': ('Artificial Turf Lawns in Fort Myers &amp; Naples | AJ Turf', 'Artificial turf lawns, built to last', 'Green year round with no mowing or watering. Installed on a compacted base with a glued concrete border, no spikes. Free onsite estimate.', 'Artificial turf<br><b>lawns.</b>'), 'pet-turf': ('Pet Turf Installation in Fort Myers &amp; Naples | AJ Turf', 'Pet turf that drains, not smells', "Built drainage-first so Florida heat doesn't trap odor. Pet-friendly infill and glued edges with no spikes for paws. Free onsite estimate.", 'Pet turf that<br><b>drains.</b>'), 'putting-greens': ('Backyard Putting Greens in Fort Myers &amp; Naples | AJ Turf', 'Backyard putting greens with a true roll', 'Putting surface plus fringe, cut and seamed by hand, off the lanai or out by the water. Free onsite estimate and one exact price.', 'Backyard<br><b>putting greens.</b>'), 'pool-and-paver-turf': ('Turf for Pools &amp; Pavers in Fort Myers &amp; Naples | AJ Turf', 'Turf for pools and pavers', 'Turf strips between pavers and tight, glued borders around pool decks. Clean lines that look designed, not patched in. Free onsite estimate.', 'Pools &amp;<br><b>pavers.</b>'), 'turf-repair': ('Artificial Turf Repair in Fort Myers &amp; Naples | AJ Turf', 'Artificial turf repair and re-installs', 'Ripples, open seams, washouts and loose edges fixed, or a full re-install done right with a concrete border. Free onsite estimate.', 'Turf repair &amp;<br><b>re-installs.</b>')}

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
      sections=[("Built like a <b>green.</b>",
        "<p>A good green is about the base. We shape and compact it so the ball rolls true, then install a short putting surface surrounded by a slightly taller fringe turf, the same way a course frames a green.</p>"
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
      lede="Ripples, open seams, washed-out bases and loose edges. We fix turf other crews put in, or pull it and do it right. Free onsite assessment, an exact price on the spot, and no minimum job size.",
      sections=[("What we <b>fix.</b>",
        "<ul><li><b>Ripples and wrinkles.</b> Re-stretched and re-secured.</li><li><b>Open or visible seams.</b> Re-cut and re-taped.</li><li><b>Dips and washouts.</b> Base rebuilt and compacted.</li><li><b>Loose edges.</b> Secured, or re-done with a concrete border.</li></ul>"
        "<p>Sometimes a repair isn't worth it. If the base or the turf itself has failed, we'll tell you straight and quote a full re-install instead.</p>"),
       ("How we <b>rebuild.</b>", METHOD)]),
]

CITY = {
 "Fort Myers": ("fort-myers", "Lee County", "hero-after",
   "Fort Myers yards deal with sandy soil, summer downpours and shade from mature trees. Turf on a compacted, draining base handles all three."),
 "Cape Coral": ("cape-coral", "Lee County", "waterfront",
   "Cape Coral is canal country. Waterfront lots, seawalls and pool cages are where turf and putting greens make the biggest difference."),
 "Naples": ("naples", "Collier County", "courtyard",
   "Naples homes and HOA communities expect a finished, high-end look. Tight edges, hidden seams and a natural-looking turf matter here."),
 "Estero": ("estero", "Lee County", "backyard-green",
   "Estero's newer communities often mean HOA review before anything changes in the yard. We help you put the approval request together."),
 "Bonita Springs": ("bonita-springs", "Lee County", "pool-deck",
   "Between Fort Myers and Naples, Bonita Springs yards range from golf communities to waterfront lots, both a natural fit for putting greens and pool-side turf."),
 "Lehigh Acres": ("lehigh-acres", "Lee County", "backyard-wide",
   "Just east of Fort Myers, Lehigh Acres yards sit on sandy soil where keeping grass green through summer is a constant fight. Turf on a compacted, draining base ends that."),
 "Sanibel": ("sanibel", "Lee County", "palm-yard",
   "On a barrier island, salt air, sandy soil and storm recovery shape what holds up. A glued edge with no spikes is a sturdy choice for island yards."),
}

def head(title, desc, path, depth, schema, og_title=None, og_slug="home"):
    r = "../" * depth
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-EFM29XK9QK"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-EFM29XK9QK');
document.addEventListener('click',e=>{{const y=e.target.closest('.yt');if(y){{const f=document.createElement('iframe');f.src='https://www.youtube-nocookie.com/embed/'+y.dataset.id+'?autoplay=1&playsinline=1&rel=0';f.allow='autoplay; encrypted-media; picture-in-picture; fullscreen';f.allowFullscreen=true;f.title=y.dataset.title;y.replaceWith(f);gtag('event','video_play',{{video_title:y.dataset.title}});return}}const a=e.target.closest('a');if(!a)return;if(a.href.includes('appointments/schedules'))gtag('event','generate_lead',{{method:'booking_link'}});else if(a.href.startsWith('tel:'))gtag('event','generate_lead',{{method:'phone_call'}});}});</script>
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
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,300;12..96,500;12..96,700&family=Hanken+Grotesk:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}style.css">
<script type="application/ld+json">{json.dumps(schema)}</script>
</head>
<body>
<nav class="nav solid" id="nav">
  <a class="mark" href="{r}"><img src="{r}img/mark.svg" alt="" width="34" height="34">AJ<span>/</span>TURF</a>
  <div class="mid mono"><a href="{r}#method">Method</a><a href="{r}#work">Work</a><a href="{r}#services">Services</a><a href="{r}guide/">Turf Guide</a></div>
  <a class="cta mono" href="#book">Free estimate</a>
</nav>'''

def close(depth):
    r = "../" * depth
    svc = "".join(f'<a href="{r}{s["slug"]}/">{s["nav"]}</a>' for s in SERVICES)
    ar = "".join(f'<a href="{r}{CITY[a][0]}/">{a}</a>' for a in AREAS)
    return f'''<section class="close" id="book">
  <img src="{r}img/green-canal.webp" alt="" loading="lazy">
  <div class="in">
    <h2>See it in<br><b>your yard.</b></h2>
    <div><p style="max-width:380px;margin-bottom:24px">Book a free onsite estimate. We'll measure, bring samples you can feel, and leave you with one exact price.</p>
      <a class="book" href="{BOOK}" target="_blank" rel="noopener">Book a free estimate <span aria-hidden="true">→</span></a>
      <a class="alt mono" href="tel:{PHONE_HREF}">Or call {PHONE}</a></div>
  </div>
</section>
<footer class="mono"><span>AJ Turf · Southwest Florida</span><span class="foot-links">{svc}</span><span class="foot-links">{ar}</span><span class="foot-links"><a href="{r}our-work/">Our work</a><a href="{r}guide/">Turf Guide</a><a href="{r}privacy/">Privacy</a><span>Mon–Sat 9–5</span></span><span class="foot-links"><a href="https://www.instagram.com/aj.turf" rel="me noopener" target="_blank">Instagram</a><a href="https://www.facebook.com/aj.turf" rel="me noopener" target="_blank">Facebook</a><a href="https://www.youtube.com/@AJTurf" rel="me noopener" target="_blank">YouTube</a></span></footer>
<script src="https://ajturf-chat.sam-947.workers.dev/widget.js" defer></script>
</body>
</html>'''

def org():
    return {"@type": "HomeAndConstructionBusiness", "@id": BASE + "#business", "name": "AJ Turf", "url": BASE,
            "telephone": "+1-" + PHONE, "email": EMAIL, "image": BASE + "img/og/home.jpg", "logo": BASE + "img/mark.svg",
            "areaServed": [{"@type": "City", "name": a + ", FL"} for a in AREAS],
            "openingHours": "Mo-Sa 09:00-17:00", "priceRange": "Free onsite estimate",
            "sameAs": ["https://www.instagram.com/aj.turf", "https://www.facebook.com/aj.turf", "https://www.youtube.com/@AJTurf", "https://www.houzz.com/pro/jereme-strange", "https://nextdoor.com/page/aj-turf-fort-myers-fl/", "https://www.thumbtack.com/fl/fort-myers/artificial-turf-installation/aj-turf/service/592250557913456653"]}

def crumbs(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(items)]}

import re as _re
def faq_schema(html):
    qa = _re.findall(r"<summary>(.*?)</summary><p>(.*?)</p>", html)
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}

def page(path, title, desc, kicker, h1, lede, img, sections, schema_extra, related, og_title=None, og_slug="home", photos=()):
    depth = path.count("/")
    r = "../" * depth
    schema = {"@context": "https://schema.org", "@graph": [org()] + schema_extra + [faq_schema(FAQ_BLOCK)]}
    secs = "".join(x if isinstance(x, str) else f'<section class="prose"><h2>{x[0]}</h2><div class="body">{x[1]}</div></section>' for x in sections)
    rel = "".join(f'<li><a href="{r}{u}">{n}</a></li>' for n, u in related)
    if photos: secs += pstrip(photos, r)
    html = head(title, desc, path, depth, schema, og_title, og_slug) + f'''
<header class="sub-hero">
  <img src="{r}img/{img}.webp" alt="">
  <div class="in"><span class="mono crumbs"><a href="{r}">AJ Turf</a> / {kicker}</span>
    <h1>{h1}</h1><p class="lede">{lede}</p>
    <p style="margin-top:28px"><a class="book" href="{BOOK}" target="_blank" rel="noopener">Book a free estimate <span aria-hidden="true">→</span></a></p></div>
</header>
<main>{secs}
<section class="split" style="grid-template-columns:minmax(0,1fr) minmax(0,1.3fr)"><div><span class="mono" style="color:var(--turf)">Questions</span><h2 style="margin-top:18px">Good to<br><b>know.</b></h2></div><div>
{FAQ_BLOCK}</div></section>
<section class="related"><span class="mono" style="color:var(--turf)">Keep looking</span><ul>{rel}</ul></section>
</main>
''' + close(depth)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    open(os.path.join(path, "index.html") if path.endswith("/") else path, "w", encoding="utf-8").write(html)

urls = [""]
for s in SERVICES:
    path = s["slug"] + "/"
    rel = [(x["nav"], x["slug"] + "/") for x in SERVICES if x is not s] + [(a, CITY[a][0] + "/") for a in AREAS[:3]]
    t, ogt, desc, _ = SEO[s["slug"]]
    svc = {"@type": "Service", "name": s["title"], "serviceType": s["kw"], "provider": {"@id": BASE + "#business"},
           "areaServed": [{"@type": "City", "name": a + ", FL"} for a in AREAS], "url": BASE + path}
    secs, vids = list(s["sections"]), []
    if s["slug"] in SERVICE_VIDEOS:
        vids, h = SERVICE_VIDEOS[s["slug"]]; secs.insert(1, vblock(vids, "../", h)); PAGE_VIDEOS[path] = vids
    page(path, t, desc, s["nav"], s["h1"], s["lede"], s["img"], secs,
         [svc, crumbs([("AJ Turf", ""), (s["title"], path)])] + [vobj(v) for v in vids], rel, ogt, s["slug"], list(s.get("photos", ())) + PC.SERVICE.get(s["slug"], []))
    urls.append(path)

for a in AREAS:
    slug, county, img, local = CITY[a]
    path = slug + "/"
    secs = [
      (f"Turf in <b>{a}.</b>", f"<p>{local}</p><p>AJ Turf installs artificial turf lawns, pet turf, putting greens and turf around pools and pavers for homes in {a} and across {county}. Every job starts with a free onsite estimate: we measure in person and give you one exact written price.</p>"
         "<ul>" + "".join(f'<li><b><a href="../{x["slug"]}/" style="color:inherit">{x["title"]}</a></b></li>' for x in SERVICES) + "</ul>"),
      ("HOAs and <b>Florida law.</b>", "<p>A 2025 Florida law (HB 683) directed the Florida Department of Environmental Protection to set statewide standards for synthetic turf on single-family lots of an acre or less. Those standards (Rule 62-308.100) took effect in May 2026, and local governments can't ban turf that meets them. Many HOAs still ask for architectural review before you install. We'll give you the product specs and install details your HOA usually asks for.</p>"),
      ("Built for <b>this climate.</b>", METHOD + "<p>Turf in full summer sun does get hotter than grass. We'll bring samples and talk through shade, product choice and placement before you decide.</p>"),
    ]
    vids = []
    if a in CITY_VIDEOS:
        vids, h = CITY_VIDEOS[a]; secs.insert(1, vblock(vids, "../", h)); PAGE_VIDEOS[path] = vids
    rel = [(x["nav"], x["slug"] + "/") for x in SERVICES] + [(b, CITY[b][0] + "/") for b in AREAS if b != a]
    biz = dict(org()); biz["@id"] = BASE + path + "#area"; biz["areaServed"] = {"@type": "City", "name": a + ", FL"}
    page(path, f"Artificial Turf & Putting Greens, {a} FL | AJ Turf",
         f"Turf lawns, pet turf and putting greens for {a} homes, installed with a glued concrete border and no spikes. Free onsite estimate.",
         a, f"Turf in<br><b>{a}.</b>", f"Artificial turf, pet turf and putting greens for {a} homes. Free onsite estimate, one exact price.",
         img, secs, [biz, crumbs([("AJ Turf", ""), (a, path)])] + [vobj(v) for v in vids], rel, f"Artificial turf and putting greens in {a}", slug, PC.CITY[a])
    urls.append(path)

# Our Work: the proof hub YouTube descriptions and bios point to. A CTA band follows every 3 cards.
OW_TITLE, OW_H = "Recent Work — Watch Our Installs | AJ Turf, Southwest Florida", "Real installs,<br><b>on video.</b>"
groups = [OUR_WORK[i:i + 3] for i in range(0, len(OUR_WORK), 3)]
page("our-work/", OW_TITLE, "Watch real AJ Turf installs: whole-property tours, a putting green built start to finish, and the install method on the job. Free onsite estimate.",
     "Our work", OW_H, "Walk finished yards and watch the method on real jobs. When you're ready, we'll measure yours for free.", "green-canal-tiki",
     [vblock(g, "../", h) for g, h in zip(groups, ["Watch the <b>installs.</b>", "More <b>jobs.</b>"])] + [pstrip(ids, "../", h) for h, ids in PC.OUR_WORK_RAILS],
     [crumbs([("AJ Turf", ""), ("Our work", "our-work/")])] + [vobj(v) for v in OUR_WORK],
     [(x["nav"], x["slug"] + "/") for x in SERVICES] + [(a, CITY[a][0] + "/") for a in AREAS[:3]], "Real AJ Turf installs, on video", "our-work")
PAGE_VIDEOS["our-work/"] = OUR_WORK
urls.append("our-work/")

# Turf Guide
from guide_content import GUIDES
def article(g):
    path = f"guide/{g['slug']}/"; r = "../../"
    faq = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": g["q"], "acceptedAnswer": {"@type": "Answer", "text": g["a"]}}]}
    art = {"@type": "Article", "headline": g["title"], "description": g["desc"], "datePublished": TODAY, "dateModified": TODAY,
           "author": {"@id": BASE + "#business"}, "publisher": {"@id": BASE + "#business"}, "mainEntityOfPage": BASE + path,
           "image": BASE + f"img/og/guide-{g['slug']}.jpg"}
    schema = {"@context": "https://schema.org", "@graph": [org(), art, faq, crumbs([("AJ Turf", ""), ("Turf Guide", "guide/"), (g["title"], path)])]}
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
  <div class="art-body">{g['body']}</div>
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
if PUBLISH_GUIDE:
  os.makedirs("guide", exist_ok=True)
items = "".join(f'<li><a href="{x["slug"]}/"><h3>{x["title"]}</h3><p>{x["desc"]}</p></a></li>' for x in GUIDES)
if PUBLISH_GUIDE: open("guide/index.html", "w", encoding="utf-8").write(head("Turf Guide: Straight Answers About Artificial Turf | AJ Turf",
    "Plain answers about artificial turf: how it's installed, what to ask an installer, heat, drainage, pets, HOAs and warranties.", "guide/", 1,
    {"@context": "https://schema.org", "@graph": [org(), crumbs([("AJ Turf", ""), ("Turf Guide", "guide/")])]}, "The AJ Turf Guide", "home") + f"""
<header class="sub-hero" style="min-height:58vh"><img src="../img/backyard-wide.webp" alt="">
  <div class="in"><span class="mono crumbs"><a href="../">AJ Turf</a> / Turf Guide</span><h1>Straight answers<br>about <b>turf.</b></h1>
  <p class="lede">What homeowners ask us most, answered plainly and backed by real product data and research.</p></div></header>
<main class="guide-list"><ul>{items}</ul></main>
""" + close(1))
if PUBLISH_GUIDE: urls.append("guide/")

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
            f"<video:duration>{sec}</video:duration><video:publication_date>{date}</video:publication_date></video:video>")
open("sitemap.xml", "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">\n' +
    "".join(f"  <url><loc>{BASE}{u}</loc><lastmod>{TODAY}</lastmod>{''.join(vsite(v) for v in PAGE_VIDEOS.get(u, []))}</url>\n" for u in urls) + "</urlset>\n")
open("robots.txt", "w").write("User-agent: *\nAllow: /\n\n" + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in
    ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "PerplexityBot", "Google-Extended", "Applebot-Extended", "Bingbot"]) +
    f"Sitemap: {BASE}sitemap.xml\n")
open("llms.txt", "w", encoding="utf-8").write(f"""# AJ Turf

> Artificial turf, pet turf, putting greens, pool and paver turf, and turf repair for homes in Southwest Florida: {", ".join(AREAS)}.

## Key facts
- Service: residential artificial turf installation, commercial and event lawns, pet turf, backyard putting greens with fringe, turf around pools and pavers, turf repair and re-installs.
- Install method: 6-inch metal or plastic edging, a 3 x 3 x 3 inch poured concrete border inside it, full weed barrier, turf glued to the border with 15-year-warrantied glue. No 6-inch steel spikes through the lawn.
- Pricing: free onsite estimate, measured in person, one exact written price. Quotes include a standard cut allowance because turf comes in 15-foot-wide rolls.
- Payments: 30% to schedule, 35% on the first day on site, 35% at completion.
- Timeline: about two days per 1,000 square feet.
- Hours: Monday to Saturday, 9 to 5.
- Contact: {PHONE}, {EMAIL}. Book: {BOOK}

## Pages
""" + "".join(f"- {BASE}{u}\n" for u in urls))

# og images: one branded 1200x630 card per page, rendered from HTML so it matches the site type
import pathlib
from playwright.sync_api import sync_playwright
cards = [("home", "hero-after", "Turf that looks like it<br>was <b>always there.</b>")]
cards += [(x["slug"], x["img"], SEO[x["slug"]][3]) for x in SERVICES]
cards += [(CITY[a][0], CITY[a][2], f"Artificial turf in<br><b>{a}.</b>") for a in AREAS]
cards += [("our-work", "green-canal-tiki", OW_H)]
cards += [("guide-" + g["slug"], g["img"], g["title"]) for g in (GUIDES if PUBLISH_GUIDE else [])]
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
print(len(urls), "urls,", len(cards), "og cards")
