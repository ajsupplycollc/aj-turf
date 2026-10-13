// AJ Turf site behavior shared by every page: arrow buttons + counter on side-scroll strips,
// and a full-screen viewer for the project-page photo grids. Plain JS, no dependencies.
(() => {
  // 0. phones: sticky Call / Text / Free estimate bar (Jereme 10/12 red team #3). Links reuse the
  // page's own tel/sms/booking hrefs, so the GA4 lead listener counts these taps too.
  const tel = document.querySelector('a[href^="tel:"]'), sms = document.querySelector('a[href^="sms:"]'),
        book = document.querySelector('a[href*="appointments/schedules"]');
  if (tel && sms && book) {
    const bar = document.createElement('nav');
    bar.className = 'mbar'; bar.setAttribute('aria-label', 'Contact AJ Turf');
    bar.innerHTML = `<a href="${tel.getAttribute('href')}">Call</a><a href="${sms.getAttribute('href')}">Text</a>` +
      `<a class="mbar-book" href="${book.getAttribute('href')}" target="_blank" rel="noopener">Free estimate</a>`;
    document.body.appendChild(bar);
  }

  // 1. strips: arrows + "3 / 12" instead of "drag to see more"
  document.querySelectorAll('.strip').forEach(strip => {
    const items = [...strip.children];
    if (items.length < 2) return;
    const nav = document.createElement('div');
    nav.className = 'snav';
    nav.innerHTML = '<button type="button" class="sbtn" aria-label="Previous">&#8592;</button><span class="mono scount"></span><button type="button" class="sbtn" aria-label="Next">&#8594;</button>';
    strip.after(nav);
    const [prev, count, next] = nav.children;
    const step = dir => {
      const i = current() + dir, t = items[Math.max(0, Math.min(items.length - 1, i))];
      strip.scrollTo({ left: t.offsetLeft - items[0].offsetLeft, behavior: 'smooth' });
    };
    const current = () => {
      const x = strip.scrollLeft;
      let best = 0;
      items.forEach((el, i) => { if (Math.abs(el.offsetLeft - items[0].offsetLeft - x) < Math.abs(items[best].offsetLeft - items[0].offsetLeft - x)) best = i; });
      return best;
    };
    const update = () => {
      const i = current(), end = strip.scrollLeft + strip.clientWidth >= strip.scrollWidth - 4;
      count.textContent = (end ? items.length : i + 1) + ' / ' + items.length;
      prev.disabled = strip.scrollLeft < 4; next.disabled = end;
      nav.hidden = strip.scrollWidth <= strip.clientWidth + 4;
    };
    prev.onclick = () => step(-1); next.onclick = () => step(1);
    // the card nearest the middle is "in focus"; the rest dim a touch (Jereme 10/13: easy to focus on what you want)
    const focus = () => {
      const mid = strip.getBoundingClientRect().left + strip.clientWidth / 2;
      let best = null, bd = 1e9;
      items.forEach(el => { const r = el.getBoundingClientRect(), dd = Math.abs(r.left + r.width / 2 - mid); if (dd < bd) { bd = dd; best = el; } });
      items.forEach(el => el.classList.toggle('in-focus', el === best));
    };
    strip.addEventListener('scroll', () => requestAnimationFrame(() => { update(); focus(); }), { passive: true });
    addEventListener('resize', update); addEventListener('load', () => { update(); focus(); }); update(); focus();
    // desktop: hover toward the left/right edge to glide that way; speed grows toward the edge, the middle 40% is still
    if (matchMedia('(hover:hover) and (pointer:fine)').matches) {
      // speed eases toward the target (no jumps when the cursor returns to the middle); snap is off on desktop (CSS)
      let v = 0, target = 0, raf = 0;
      const tick = () => {
        v += (target - v) * .12;
        if (Math.abs(v) < .2 && !target) { v = 0; raf = 0; return; }
        strip.scrollLeft += v; raf = requestAnimationFrame(tick);
      };
      strip.addEventListener('mousemove', e => {
        const r = strip.getBoundingClientRect(), x = (e.clientX - r.left) / r.width; // 0..1
        const edge = x < .3 ? -(.3 - x) / .3 : x > .7 ? (x - .7) / .3 : 0;
        target = Math.sign(edge) * edge * edge * 22; // gentle near the zone, quick at the edge
        if (!raf && target) raf = requestAnimationFrame(tick);
      });
      strip.addEventListener('mouseleave', () => { target = 0; });
    }
  });

  // 1a. pinned prints swing in the first time they scroll into view (CSS does the swing)
  const prints = document.querySelectorAll('.print');
  if (prints.length && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (!e.isIntersecting) return;
      const el = e.target, i = [...el.closest('ul,.steps')?.querySelectorAll('.print') || []].indexOf(el);
      setTimeout(() => el.classList.add('in'), Math.max(0, i % 3) * 90); // slight stagger when several land at once
      io.unobserve(el);
    }), { rootMargin: '0px 0px -12% 0px' });
    prints.forEach(p => io.observe(p));
  } else prints.forEach(p => p.classList.add('in'));

  // 1b. ballpark calculator. Range comes ONLY from the public $9-$15/sq ft band and shows live, no gate
  // (Muse D2 10/13: the range is already public; the quick form below stays the lead capture).
  // Repairs get no number: they start with an onsite assessment.
  const LO = 9, HI = 15, TYPES = ['Lawn', 'Pet turf', 'Putting green', 'Pool & pavers', 'Repair'];
  const money = n => '$' + n.toLocaleString('en-US');
  const range = sq => [Math.ceil(sq * LO / 10) * 10, Math.floor(sq * HI / 10) * 10]; // rounding stays inside the band
  document.querySelectorAll('.calc').forEach(c => {
    const t0 = TYPES.includes(c.dataset.type) ? c.dataset.type : 'Lawn';
    const book = document.querySelector('a[href*="appointments/schedules"]');
    c.innerHTML = `<div><span class="mono" style="color:var(--turf)">Ballpark calculator</span><h2>What would it <b>cost?</b></h2>
      <p class="calc-note">Ballparks only — your exact price comes from a free onsite measurement.</p></div>
      <form class="calc-f" onsubmit="return false">
        <label>Project<select name="type">${TYPES.map(t => `<option${t === t0 ? ' selected' : ''}>${t}</option>`).join('')}</select></label>
        <label class="calc-sq">About how many square feet?<span><input name="sqr" type="range" min="100" max="5000" step="50" value="500" aria-label="Square feet slider"><input name="sq" type="number" min="100" max="5000" step="10" value="500" inputmode="numeric" aria-label="Square feet"></span></label>
        <p class="calc-out" role="status" aria-live="polite"></p>
        ${book ? `<a class="book" href="${book.getAttribute('href')}" target="_blank" rel="noopener">Get your exact price, free <span aria-hidden="true">→</span></a>` : ''}
      </form>`;
    const f = c.querySelector('form'), out = f.querySelector('.calc-out'), F = f.elements;
    const sq = () => Math.max(100, Math.min(5000, +F.sq.value || 100));
    const show = () => {
      const rep = F.type.value === 'Repair';
      f.querySelector('.calc-sq').hidden = rep;
      if (rep) out.textContent = 'Repairs start with a free onsite assessment — exact price on site.';
      else { const [a, b] = range(sq()); out.textContent = `Ballpark: ${money(a)}–${money(b)}`; }
    };
    let told = false;  // one GA4 event per visit when someone actually uses it
    const used = () => { show(); if (!told && window.gtag) { gtag('event', 'calculator_use'); told = true; } };
    F.sqr.oninput = () => { F.sq.value = F.sqr.value; used(); };
    F.sq.oninput = () => { F.sqr.value = sq(); used(); };
    F.type.onchange = used;
    show();
  });

  // 2. project galleries: tap a photo -> full screen, arrows / swipe / keys to flip
  const grids = document.querySelectorAll('.pgrid');
  if (!grids.length) return;
  const d = document.createElement('dialog');
  d.className = 'lb';
  d.innerHTML = '<button type="button" class="lb-x" aria-label="Close">&#215;</button><button type="button" class="lb-p" aria-label="Previous photo">&#8592;</button><figure><img alt=""><figcaption class="mono"></figcaption></figure><button type="button" class="lb-n" aria-label="Next photo">&#8594;</button>';
  document.body.append(d);
  const img = d.querySelector('img'), cap = d.querySelector('figcaption');
  let set = [], at = 0;
  const show = i => {
    at = (i + set.length) % set.length;
    const b = set[at], t = b.querySelector('img');
    img.src = b.dataset.full; img.alt = t.alt;
    cap.textContent = (b.parentElement.querySelector('figcaption')?.textContent || '') + '  ·  ' + (at + 1) + ' / ' + set.length;
  };
  grids.forEach(g => g.addEventListener('click', e => {
    const b = e.target.closest('.zoom'); if (!b) return;
    set = [...g.querySelectorAll('.zoom')]; show(set.indexOf(b)); d.showModal();
  }));
  d.querySelector('.lb-x').onclick = () => d.close();
  d.querySelector('.lb-p').onclick = () => show(at - 1);
  d.querySelector('.lb-n').onclick = () => show(at + 1);
  d.addEventListener('click', e => { if (e.target === d) d.close(); });
  d.addEventListener('keydown', e => { if (e.key === 'ArrowLeft') show(at - 1); if (e.key === 'ArrowRight') show(at + 1); });
  let x0 = null;
  d.addEventListener('touchstart', e => { x0 = e.touches[0].clientX; }, { passive: true });
  d.addEventListener('touchend', e => { if (x0 === null) return; const dx = e.changedTouches[0].clientX - x0; if (Math.abs(dx) > 40) show(at + (dx < 0 ? 1 : -1)); x0 = null; });

})();
