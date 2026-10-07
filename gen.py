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
AREAS = ["Fort Myers", "Cape Coral", "Naples", "Estero", "Bonita Springs", "Sanibel"]

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
<details><summary>What's the warranty?</summary><p>The turf carries its manufacturer's warranty, which depends on the product you pick, and our install labor is warrantied too. You'll see the exact terms before you sign.</p></details>
"""

SEO = {'artificial-turf-installation': ('Artificial Turf Lawns in Fort Myers &amp; Naples | AJ Turf', 'Artificial turf lawns, built to last', 'Green year round with no mowing or watering. Installed on a compacted base with a glued concrete border, no spikes. Free onsite estimate.', 'Artificial turf<br><b>lawns.</b>'), 'pet-turf': ('Pet Turf Installation in Fort Myers &amp; Naples | AJ Turf', 'Pet turf that drains, not smells', "Built drainage-first so Florida heat doesn't trap odor. Pet-friendly infill and glued edges with no spikes for paws. Free onsite estimate.", 'Pet turf that<br><b>drains.</b>'), 'putting-greens': ('Backyard Putting Greens in Fort Myers &amp; Naples | AJ Turf', 'Backyard putting greens with a true roll', 'Putting surface plus fringe, cut and seamed by hand, off the lanai or out by the water. Free onsite estimate and one exact price.', 'Backyard<br><b>putting greens.</b>'), 'pool-and-paver-turf': ('Turf for Pools &amp; Pavers in Fort Myers &amp; Naples | AJ Turf', 'Turf for pools and pavers', 'Turf strips between pavers and tight, glued borders around pool decks. Clean lines that look designed, not patched in. Free onsite estimate.', 'Pools &amp;<br><b>pavers.</b>'), 'turf-repair': ('Artificial Turf Repair in Fort Myers &amp; Naples | AJ Turf', 'Artificial turf repair and re-installs', 'Ripples, open seams, washouts and loose edges fixed, or a full re-install done right with a concrete border. Free onsite estimate.', 'Turf repair &amp;<br><b>re-installs.</b>')}

SERVICES = [
 dict(slug="artificial-turf-installation", nav="Lawns", title="Artificial Turf Installation", h1="Artificial turf <b>lawns.</b>",
      img="palm-yard", kw="artificial turf installation",
      lede="Front yards, back yards and side yards that stay green through a Florida August, with no mowing, watering or brown patches.",
      sections=[("Why homeowners <b>switch.</b>",
        "<p>Southwest Florida lawns fight heat, sandy soil, shade from palms and oaks, and watering restrictions. Turf ends the cycle of resodding, fertilizing and mowing, and it looks the same in March as it does in September.</p>"
        "<ul><li><b>No mowing or watering.</b> A rinse and a brush is the upkeep.</li><li><b>Stays green.</b> No brown patches from drought, grubs or chinch bugs.</li><li><b>Built to drain.</b> Rain goes through the turf and the compacted base, not across your patio.</li></ul>"),
       ("How we <b>build it.</b>", METHOD)]),
 dict(slug="pet-turf", nav="Pet turf", title="Pet Turf", h1="Pet <b>turf.</b>", img="side-garden", kw="pet turf",
      lede="Turf built for dogs: drainage first, pet-friendly infill, and a glued edge with no spikes for paws to find.",
      sections=[("Odor is a <b>base problem.</b>",
        "<p>In Florida heat and humidity, pet odor comes from what happens under the turf, not the blades. When urine can't drain, it sits in the base and smells. That's why we start with a compacted screening-sand base that drains, then add pet-friendly infill.</p>"
        "<ul><li><b>Drains fast.</b> Rinse the area and it washes through.</li><li><b>No spikes.</b> Nothing to work loose under running dogs.</li><li><b>No mud.</b> No dug-up patches or dirty paws after rain.</li></ul>"),
       ("How we <b>build it.</b>", METHOD)]),
 dict(slug="putting-greens", nav="Putting greens", title="Backyard Putting Greens", h1="Putting <b>greens.</b>", img="green-canal", kw="backyard putting green",
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
      lede="Ripples, open seams, washed-out bases and loose edges. We fix turf other crews put in, or pull it and do it right.",
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
document.addEventListener('click',e=>{{const a=e.target.closest('a');if(!a)return;if(a.href.includes('appointments/schedules'))gtag('event','generate_lead',{{method:'booking_link'}});else if(a.href.startsWith('tel:'))gtag('event','generate_lead',{{method:'phone_call'}});}});</script>
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
<footer class="mono"><span>AJ Turf · Southwest Florida</span><span class="foot-links">{svc}</span><span class="foot-links">{ar}</span><span class="foot-links"><a href="{r}guide/">Turf Guide</a><a href="{r}privacy/">Privacy</a><span>Mon–Sat 9–5</span></span></footer>
</body>
</html>'''

def org():
    return {"@type": "HomeAndConstructionBusiness", "@id": BASE + "#business", "name": "AJ Turf", "url": BASE,
            "telephone": "+1-" + PHONE, "email": EMAIL, "image": BASE + "img/og/home.jpg", "logo": BASE + "img/mark.svg",
            "areaServed": [{"@type": "City", "name": a + ", FL"} for a in AREAS],
            "openingHours": "Mo-Sa 09:00-17:00", "priceRange": "Free onsite estimate",
            "sameAs": ["https://www.instagram.com/aj.turf", "https://www.facebook.com/aj.turf", "https://www.houzz.com/pro/jereme-strange", "https://nextdoor.com/page/aj-turf-fort-myers-fl/"]}

def crumbs(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(items)]}

import re as _re
def faq_schema(html):
    qa = _re.findall(r"<summary>(.*?)</summary><p>(.*?)</p>", html)
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}

def page(path, title, desc, kicker, h1, lede, img, sections, schema_extra, related, og_title=None, og_slug="home"):
    depth = path.count("/")
    r = "../" * depth
    schema = {"@context": "https://schema.org", "@graph": [org()] + schema_extra + [faq_schema(FAQ_BLOCK)]}
    secs = "".join(f'<section class="prose"><h2>{h}</h2><div class="body">{b}</div></section>' for h, b in sections)
    rel = "".join(f'<li><a href="{r}{u}">{n}</a></li>' for n, u in related)
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
    page(path, t, desc, s["nav"], s["h1"], s["lede"], s["img"], s["sections"],
         [svc, crumbs([("AJ Turf", ""), (s["title"], path)])], rel, ogt, s["slug"])
    urls.append(path)

for a in AREAS:
    slug, county, img, local = CITY[a]
    path = slug + "/"
    secs = [
      (f"Turf in <b>{a}.</b>", f"<p>{local}</p><p>AJ Turf installs artificial turf lawns, pet turf, putting greens and turf around pools and pavers for homes in {a} and across {county}. Every job starts with a free onsite estimate: we measure in person and give you one exact written price.</p>"
         "<ul>" + "".join(f'<li><b><a href="../{x["slug"]}/" style="color:inherit">{x["title"]}</a></b></li>' for x in SERVICES) + "</ul>"),
      ("HOAs and <b>Florida law.</b>", "<p>A 2025 Florida law (HB 683) directed the state to set standards for synthetic turf on single-family lots of an acre or less, and limits local governments from banning turf that meets them. Many HOAs still ask for architectural review before you install. We'll give you the product specs and install details your HOA usually asks for.</p>"),
      ("Built for <b>this climate.</b>", METHOD + "<p>Turf in full summer sun does get hotter than grass. We'll bring samples and talk through shade, product choice and placement before you decide.</p>"),
    ]
    rel = [(x["nav"], x["slug"] + "/") for x in SERVICES] + [(b, CITY[b][0] + "/") for b in AREAS if b != a]
    biz = dict(org()); biz["@id"] = BASE + path + "#area"; biz["areaServed"] = {"@type": "City", "name": a + ", FL"}
    page(path, f"Artificial Turf & Putting Greens, {a} FL | AJ Turf",
         f"Turf lawns, pet turf and putting greens for {a} homes, installed with a glued concrete border and no spikes. Free onsite estimate.",
         a, f"Turf in<br><b>{a}.</b>", f"Artificial turf, pet turf and putting greens for {a} homes. Free onsite estimate, one exact price.",
         img, secs, [biz, crumbs([("AJ Turf", ""), (a, path)])], rel, f"Artificial turf and putting greens in {a}", slug)
    urls.append(path)

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
<p style="margin-top:24px">When you book an estimate, call, or message us, we use your name, phone, email and address only to schedule and complete your estimate and project. We don't sell or share your information. This site uses Google Analytics to count visits and see which pages help people; it uses no advertising trackers. To ask about or remove your information, email <a href="mailto:{EMAIL}">{EMAIL}</a> or call {PHONE}.</p>
<p style="margin-top:16px" class="mono">Updated {TODAY}</p>
</main>''' + close(1))
urls.append("privacy/")

open("sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{BASE}{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>\n")
open("robots.txt", "w").write("User-agent: *\nAllow: /\n\n" + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in
    ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "PerplexityBot", "Google-Extended", "Applebot-Extended", "Bingbot"]) +
    f"Sitemap: {BASE}sitemap.xml\n")
open("llms.txt", "w", encoding="utf-8").write(f"""# AJ Turf

> Artificial turf, pet turf, putting greens, pool and paver turf, and turf repair for homes in Southwest Florida: {", ".join(AREAS)}.

## Key facts
- Service: residential artificial turf installation, pet turf, backyard putting greens with fringe, turf around pools and pavers, turf repair and re-installs.
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
