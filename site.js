// AJ Turf site behavior shared by every page: arrow buttons + counter on side-scroll strips,
// and a full-screen viewer for the project-page photo grids. Plain JS, no dependencies.
(() => {
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
    strip.addEventListener('scroll', () => requestAnimationFrame(update), { passive: true });
    addEventListener('resize', update); addEventListener('load', update); update();
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
