async function renderMermaidInContainer(container) {
  if (typeof mermaid === 'undefined') return;
  const diagrams = (window.App && App.presentation) ? App.presentation.mermaidDiagrams : {};
  const els = container.querySelectorAll('.mermaid-diagram');
  for (const el of els) {
    const key = el.getAttribute('data-diagram');
    if (el.getAttribute('data-processed')) continue;
    const src = diagrams[key];
    if (!src) continue;
    try {
      const id = 'mmd-' + Math.random().toString(36).slice(2, 9);
      const { svg } = await mermaid.render(id, src);
      el.innerHTML = svg;
      el.setAttribute('data-processed', 'true');
    } catch (e) {
      console.warn('Mermaid:', e);
      el.innerHTML = '<div style="color:#f85149;font-size:0.8rem;padding:8px">Diagram error</div>';
    }
  }
}

window.ThemeManager = {
  init() {
    const saved = localStorage.getItem('aetherix-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    this.updateIcon(saved);
  },
  toggle() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('aetherix-theme', next);
    this.updateIcon(next);
    if (typeof App !== 'undefined' && App.initCosmos) App.initCosmos();
  },
  updateIcon(theme) {
    const btn = document.getElementById('theme-toggle');
    if (btn) btn.innerHTML = theme === 'dark' ? '\u2600\uFE0F' : '\uD83C\uDF19';
  }
};

window.DropdownManager = {
  init() {
    document.querySelectorAll('.topnav-dropdown').forEach(dd => {
      dd.addEventListener('mouseenter', () => {
        dd.querySelector('.topnav-dropdown-menu')?.classList.add('show');
      });
      dd.addEventListener('mouseleave', () => {
        dd.querySelector('.topnav-dropdown-menu')?.classList.remove('show');
      });
    });
    document.querySelectorAll('.topnav-dropdown-item').forEach(item => {
      item.addEventListener('click', () => {
        document.querySelectorAll('.topnav-dropdown-menu.show').forEach(d => d.classList.remove('show'));
      });
    });
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.topnav-dropdown')) {
        document.querySelectorAll('.topnav-dropdown-menu.show').forEach(d => d.classList.remove('show'));
      }
    });
    const hamburger = document.getElementById('hamburger-btn');
    if (hamburger) {
      hamburger.addEventListener('click', () => {
        document.getElementById('mobile-menu')?.classList.toggle('open');
      });
    }
    document.querySelectorAll('.topnav-mobile-link').forEach(link => {
      link.addEventListener('click', () => {
        document.getElementById('mobile-menu')?.classList.remove('open');
      });
    });
  }
};

window.Router = {
  init() {
    document.querySelectorAll('[data-route]').forEach(el => {
      el.addEventListener('click', (e) => {
        e.preventDefault();
        const route = el.getAttribute('data-route');
        if (route) this.navigate(route);
      });
    });
    window.addEventListener('hashchange', () => this.handleHash());
    this.handleHash();
  },
  navigate(route) {
    window.location.hash = '#' + route;
  },
  handleHash() {
    const hash = window.location.hash.slice(1) || 'welcome';
    const route = hash.split('/')[0];
    document.querySelectorAll('.tab').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    let target = document.querySelector('.page[data-route="' + route + '"]');
    if (!target) target = document.getElementById(route);
    if (target) target.classList.add('active');
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    document.querySelectorAll('[data-route="' + route + '"]').forEach(l => l.classList.add('active'));
    document.querySelectorAll('li[data-route]').forEach(l => {
      l.classList.toggle('active', l.getAttribute('data-route') === route);
    });
    document.getElementById('mobile-menu')?.classList.remove('open');
    document.querySelectorAll('.dropdown-menu').forEach(d => d.classList.remove('show'));
    if (route === 'presentation') {
      document.body.classList.add('pres-active');
      App.presentation.init();
    } else {
      document.body.classList.remove('pres-active');
    }
    if (route === 'dashboard') {
      App.ensureDashboard();
    }
    if (hash.startsWith('presentation/')) {
      const slideNum = parseInt(hash.split('/')[1]);
      if (slideNum >= 1 && slideNum <= App.presentation.slides.length) App.presentation.goTo(slideNum - 1);
    }
    if (target) renderMermaidInContainer(target);
    window.scrollTo(0, 0);
  }
};

window.App = (() => {
  const charts = {};
  const bundles = [];
  const cosmosCanvas = document.getElementById('cosmos-canvas');
  const cosmosCtx = cosmosCanvas ? cosmosCanvas.getContext('2d') : null;

  function $(id) { return document.getElementById(id); }
  function fmt(n, d) { return Number(n).toFixed(d === undefined ? 2 : d); }
  function fmtKm(km) { return fmt(km / 1e6, 1) + 'M km'; }
  function fmtTime(sec) {
    if (sec < 60) return fmt(sec, 1) + 's';
    if (sec < 3600) return fmt(sec / 60, 1) + ' min';
    return fmt(sec / 3600, 2) + ' hrs';
  }
  function destroyChart(id) { if (charts[id]) { charts[id].destroy(); delete charts[id]; } }

  function toast(msg, type) {
    type = type || 'info';
    const el = document.createElement('div');
    el.className = 'toast toast-' + type;
    el.textContent = msg;
    const c = $('toast-container');
    if (c) { c.appendChild(el); setTimeout(() => { if (el.parentNode) el.remove(); }, 3200); }
  }

  const chartTheme = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: '#8892aa', font: { size: 11, family: "'Inter', sans-serif" }, padding: 14, usePointStyle: true, pointStyleWidth: 8 } },
      tooltip: { backgroundColor: 'rgba(8,16,40,0.92)', borderColor: 'rgba(60,100,180,0.2)', borderWidth: 1, titleColor: '#e4eaf5', bodyColor: '#8892aa', titleFont: { weight: '600' }, padding: 10, cornerRadius: 8 }
    },
    scales: {
      x: { grid: { color: 'rgba(60,100,180,0.08)' }, ticks: { color: '#4a5270', font: { size: 10 } } },
      y: { grid: { color: 'rgba(60,100,180,0.08)' }, ticks: { color: '#4a5270', font: { size: 10 } } }
    }
  };

  // --- COSMOS CANVAS ---
  let stars = [];
  let shootingStars = [];
  let nebulae = [];
  let planets = [];
  let particles = [];
  let blackHole = null;

  function initCosmos() {
    if (!cosmosCtx) return;
    resizeCosmos();
    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
    const w = cosmosCanvas.width, h = cosmosCanvas.height;
    stars = [];
    shootingStars = [];
    nebulae = [];
    planets = [];
    particles = [];
    blackHole = null;

    const starCount = isDark ? 1000 : 800;
    for (let i = 0; i < starCount; i++) {
      const colorRoll = Math.random();
      let sr, sg, sb;
      if (isDark) {
        if (colorRoll < 0.1) { sr = 180; sg = 200; sb = 255; }
        else if (colorRoll < 0.2) { sr = 255; sg = 220; sb = 180; }
        else if (colorRoll < 0.25) { sr = 255; sg = 180; sb = 180; }
        else { sr = 200; sg = 210; sb = 240; }
      } else {
        if (colorRoll < 0.1) { sr = 30; sg = 50; sb = 160; }
        else if (colorRoll < 0.2) { sr = 160; sg = 110; sb = 20; }
        else if (colorRoll < 0.25) { sr = 180; sg = 40; sb = 40; }
        else if (colorRoll < 0.35) { sr = 0; sg = 140; sb = 180; }
        else if (colorRoll < 0.45) { sr = 100; sg = 60; sb = 200; }
        else { sr = 40; sg = 60; sb = 140; }
      }
      stars.push({
        x: Math.random() * w,
        y: Math.random() * h,
        r: Math.random() * (isDark ? 1.8 : 2.2) + (isDark ? 0.3 : 0.5),
        a: Math.random() * (isDark ? 0.7 : 0.85) + (isDark ? 0.15 : 0.35),
        speed: Math.random() * 0.0008 + 0.0001,
        phase: Math.random() * Math.PI * 2,
        cr: sr, cg: sg, cb: sb
      });
    }

    const nebulaCount = isDark ? 16 : 10;
    const nebulaColors = [
      [124, 92, 247], [200, 76, 255], [0, 212, 255], [255, 107, 53],
      [0, 184, 148], [255, 80, 120], [100, 140, 255], [200, 160, 50],
      [80, 200, 160], [255, 140, 80], [140, 100, 220], [60, 180, 200]
    ];
    for (let i = 0; i < nebulaCount; i++) {
      nebulae.push({
        x: Math.random() * w,
        y: Math.random() * h,
        r: 120 + Math.random() * 350,
        color: nebulaColors[i % nebulaColors.length],
        alpha: (isDark ? 0.02 : 0.04) + Math.random() * (isDark ? 0.025 : 0.04),
        dx: (Math.random() - 0.5) * 0.2,
        dy: (Math.random() - 0.5) * 0.12,
        pulse: Math.random() * Math.PI * 2,
        pulseSpeed: 0.0003 + Math.random() * 0.0005
      });
    }

    blackHole = {
      x: w * 0.82 + (Math.random() - 0.5) * w * 0.15,
      y: h * 0.18 + (Math.random() - 0.5) * h * 0.1,
      r: 18 + Math.random() * 14,
      accretionAngle: 0
    };

    const planetDefs = [
      { color: [255, 107, 53], ringColor: [255, 160, 100], size: 6, hasRing: false },
      { color: [80, 140, 200], ringColor: [180, 200, 230], size: 9, hasRing: true },
      { color: [200, 180, 140], ringColor: [220, 200, 160], size: 11, hasRing: true },
      { color: [180, 140, 100], ringColor: [200, 170, 130], size: 12, hasRing: false },
      { color: [160, 200, 180], ringColor: [180, 220, 200], size: 7, hasRing: false },
      { color: [220, 180, 100], ringColor: [240, 200, 130], size: 10, hasRing: true },
      { color: [140, 100, 180], ringColor: [160, 130, 200], size: 8, hasRing: true },
      { color: [200, 120, 100], ringColor: [220, 150, 130], size: 7, hasRing: false },
    ];
    planetDefs.forEach((pd, i) => {
      const px = w * (0.05 + (i / planetDefs.length) * 0.9) + (Math.random() - 0.5) * 80;
      const py = h * (0.1 + Math.random() * 0.8);
      planets.push({
        baseX: px, baseY: py,
        r: pd.size,
        color: pd.color,
        ringColor: pd.ringColor,
        hasRing: pd.hasRing,
        phase: Math.random() * Math.PI * 2,
        bobSpeed: 0.0002 + Math.random() * 0.0003,
        bobAmount: 2 + Math.random() * 4,
        glowAlpha: 0.08 + Math.random() * 0.06
      });
    });

    const particleCount = isDark ? 160 : 120;
    for (let i = 0; i < particleCount; i++) {
      const hue = Math.random();
      let pr, pg, pb;
      if (hue < 0.33) { pr = 0; pg = 212; pb = 255; }
      else if (hue < 0.66) { pr = 124; pg = 92; pb = 247; }
      else { pr = 200; pg = 76; pb = 255; }
      particles.push({
        x: Math.random() * w,
        y: Math.random() * h,
        r: 0.5 + Math.random() * 1.5,
        a: 0.1 + Math.random() * 0.3,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.2,
        cr: pr, cg: pg, cb: pb,
        pulse: Math.random() * Math.PI * 2,
        pulseSpeed: 0.001 + Math.random() * 0.002
      });
    }

    animateCosmos();
  }

  function resizeCosmos() {
    if (!cosmosCanvas) return;
    cosmosCanvas.width = window.innerWidth;
    cosmosCanvas.height = window.innerHeight;
  }

  function spawnShootingStar() {
    if (Math.random() > 0.02 || shootingStars.length > 10) return;
    const angle = Math.PI * 0.1 + Math.random() * Math.PI * 0.35;
    const startX = Math.random() * cosmosCanvas.width;
    const startY = Math.random() * cosmosCanvas.height * 0.5;
    const colors = [
      [200, 220, 255], [255, 200, 150], [150, 200, 255], [200, 255, 200]
    ];
    const c = colors[Math.floor(Math.random() * colors.length)];
    shootingStars.push({
      x: startX,
      y: startY,
      len: 80 + Math.random() * 180,
      speed: 5 + Math.random() * 10,
      angle: angle,
      life: 1,
      decay: 0.008 + Math.random() * 0.012,
      cr: c[0], cg: c[1], cb: c[2],
      sparks: []
    });
  }

  function animateCosmos() {
    if (!cosmosCtx) return;
    const w = cosmosCanvas.width, h = cosmosCanvas.height;
    cosmosCtx.clearRect(0, 0, w, h);
    const now = Date.now();
    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';

    if (!isDark) {
      const bgGrad = cosmosCtx.createLinearGradient(0, 0, 0, h);
      bgGrad.addColorStop(0, 'rgba(15, 25, 60, 0.18)');
      bgGrad.addColorStop(0.5, 'rgba(20, 30, 70, 0.12)');
      bgGrad.addColorStop(1, 'rgba(15, 25, 60, 0.18)');
      cosmosCtx.fillStyle = bgGrad;
      cosmosCtx.fillRect(0, 0, w, h);
    }

    nebulae.forEach(n => {
      n.x += n.dx;
      n.y += n.dy;
      if (n.x < -n.r) n.x = w + n.r;
      if (n.x > w + n.r) n.x = -n.r;
      if (n.y < -n.r) n.y = h + n.r;
      if (n.y > h + n.r) n.y = -n.r;
      const pulseAlpha = n.alpha * (0.8 + 0.2 * Math.sin(now * n.pulseSpeed + n.pulse));
      const grad = cosmosCtx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r);
      grad.addColorStop(0, `rgba(${n.color[0]},${n.color[1]},${n.color[2]},${pulseAlpha})`);
      grad.addColorStop(0.4, `rgba(${n.color[0]},${n.color[1]},${n.color[2]},${pulseAlpha * 0.5})`);
      grad.addColorStop(1, 'transparent');
      cosmosCtx.fillStyle = grad;
      cosmosCtx.fillRect(n.x - n.r, n.y - n.r, n.r * 2, n.r * 2);
    });

    if (blackHole) {
      const bh = blackHole;
      bh.accretionAngle += 0.008;

      const diskR = bh.r * 4;
      const diskGrad = cosmosCtx.createRadialGradient(bh.x, bh.y, bh.r * 1.2, bh.x, bh.y, diskR);
      diskGrad.addColorStop(0, 'rgba(255, 140, 50, 0.15)');
      diskGrad.addColorStop(0.3, 'rgba(200, 80, 255, 0.08)');
      diskGrad.addColorStop(0.6, 'rgba(0, 180, 255, 0.04)');
      diskGrad.addColorStop(1, 'transparent');
      cosmosCtx.fillStyle = diskGrad;
      cosmosCtx.beginPath();
      cosmosCtx.arc(bh.x, bh.y, diskR, 0, Math.PI * 2);
      cosmosCtx.fill();

      cosmosCtx.save();
      cosmosCtx.translate(bh.x, bh.y);
      cosmosCtx.rotate(bh.accretionAngle);
      cosmosCtx.scale(1, 0.35);
      for (let ring = 0; ring < 3; ring++) {
        const rr = bh.r * (1.8 + ring * 0.9);
        const ringAlpha = 0.15 - ring * 0.04;
        cosmosCtx.beginPath();
        cosmosCtx.arc(0, 0, rr, 0, Math.PI * 2);
        cosmosCtx.strokeStyle = `rgba(${180 + ring * 30}, ${100 - ring * 20}, 255, ${ringAlpha})`;
        cosmosCtx.lineWidth = 1.5 - ring * 0.3;
        cosmosCtx.stroke();
      }
      cosmosCtx.restore();

      cosmosCtx.save();
      cosmosCtx.translate(bh.x, bh.y);
      cosmosCtx.rotate(-bh.accretionAngle * 0.6);
      cosmosCtx.scale(1, 0.35);
      for (let ring = 0; ring < 2; ring++) {
        const rr = bh.r * (2.2 + ring * 1.0);
        cosmosCtx.beginPath();
        cosmosCtx.arc(0, 0, rr, 0, Math.PI * 2);
        cosmosCtx.strokeStyle = `rgba(255, ${160 + ring * 40}, ${80 + ring * 40}, 0.08)`;
        cosmosCtx.lineWidth = 1;
        cosmosCtx.stroke();
      }
      cosmosCtx.restore();

      const bhGrad = cosmosCtx.createRadialGradient(bh.x, bh.y, 0, bh.x, bh.y, bh.r);
      bhGrad.addColorStop(0, 'rgba(0, 0, 0, 1)');
      bhGrad.addColorStop(0.7, 'rgba(0, 0, 0, 0.95)');
      bhGrad.addColorStop(1, 'rgba(30, 10, 50, 0.4)');
      cosmosCtx.fillStyle = bhGrad;
      cosmosCtx.beginPath();
      cosmosCtx.arc(bh.x, bh.y, bh.r, 0, Math.PI * 2);
      cosmosCtx.fill();

      const lensR = bh.r * 2.5;
      const lensGrad = cosmosCtx.createRadialGradient(bh.x, bh.y, bh.r, bh.x, bh.y, lensR);
      lensGrad.addColorStop(0, 'rgba(255, 200, 100, 0.06)');
      lensGrad.addColorStop(1, 'transparent');
      cosmosCtx.fillStyle = lensGrad;
      cosmosCtx.beginPath();
      cosmosCtx.arc(bh.x, bh.y, lensR, 0, Math.PI * 2);
      cosmosCtx.fill();
    }

    stars.forEach(s => {
      const twinkle = 0.4 + 0.6 * Math.sin(now * s.speed + s.phase);
      cosmosCtx.beginPath();
      cosmosCtx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      cosmosCtx.fillStyle = `rgba(${s.cr}, ${s.cg}, ${s.cb}, ${s.a * twinkle})`;
      cosmosCtx.fill();
      if (s.r > 1.4 && s.a > 0.5) {
        const glowR = s.r * 3;
        const gGrad = cosmosCtx.createRadialGradient(s.x, s.y, s.r, s.x, s.y, glowR);
        gGrad.addColorStop(0, `rgba(${s.cr}, ${s.cg}, ${s.cb}, ${s.a * twinkle * 0.15})`);
        gGrad.addColorStop(1, 'transparent');
        cosmosCtx.fillStyle = gGrad;
        cosmosCtx.beginPath();
        cosmosCtx.arc(s.x, s.y, glowR, 0, Math.PI * 2);
        cosmosCtx.fill();
      }
    });

    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0) p.x = w;
      if (p.x > w) p.x = 0;
      if (p.y < 0) p.y = h;
      if (p.y > h) p.y = 0;
      const pa = p.a * (0.5 + 0.5 * Math.sin(now * p.pulseSpeed + p.pulse));
      const pGrad = cosmosCtx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 4);
      pGrad.addColorStop(0, `rgba(${p.cr}, ${p.cg}, ${p.cb}, ${pa})`);
      pGrad.addColorStop(1, 'transparent');
      cosmosCtx.fillStyle = pGrad;
      cosmosCtx.beginPath();
      cosmosCtx.arc(p.x, p.y, p.r * 4, 0, Math.PI * 2);
      cosmosCtx.fill();
      cosmosCtx.beginPath();
      cosmosCtx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      cosmosCtx.fillStyle = `rgba(${p.cr}, ${p.cg}, ${p.cb}, ${pa * 2})`;
      cosmosCtx.fill();
    });

    planets.forEach(pl => {
      const bob = Math.sin(now * pl.bobSpeed + pl.phase) * pl.bobAmount;
      const px = pl.baseX;
      const py = pl.baseY + bob;

      const planetGlow = cosmosCtx.createRadialGradient(px, py, pl.r, px, py, pl.r * 5);
      planetGlow.addColorStop(0, `rgba(${pl.color[0]}, ${pl.color[1]}, ${pl.color[2]}, ${pl.glowAlpha})`);
      planetGlow.addColorStop(1, 'transparent');
      cosmosCtx.fillStyle = planetGlow;
      cosmosCtx.beginPath();
      cosmosCtx.arc(px, py, pl.r * 5, 0, Math.PI * 2);
      cosmosCtx.fill();

      const bodyGrad = cosmosCtx.createRadialGradient(
        px - pl.r * 0.3, py - pl.r * 0.3, pl.r * 0.1,
        px, py, pl.r
      );
      bodyGrad.addColorStop(0, `rgba(${Math.min(255, pl.color[0] + 60)}, ${Math.min(255, pl.color[1] + 60)}, ${Math.min(255, pl.color[2] + 60)}, 0.9)`);
      bodyGrad.addColorStop(0.7, `rgba(${pl.color[0]}, ${pl.color[1]}, ${pl.color[2]}, 0.85)`);
      bodyGrad.addColorStop(1, `rgba(${Math.floor(pl.color[0] * 0.4)}, ${Math.floor(pl.color[1] * 0.4)}, ${Math.floor(pl.color[2] * 0.4)}, 0.8)`);
      cosmosCtx.fillStyle = bodyGrad;
      cosmosCtx.beginPath();
      cosmosCtx.arc(px, py, pl.r, 0, Math.PI * 2);
      cosmosCtx.fill();

      if (pl.hasRing) {
        cosmosCtx.save();
        cosmosCtx.translate(px, py);
        cosmosCtx.scale(1, 0.3);
        cosmosCtx.beginPath();
        cosmosCtx.arc(0, 0, pl.r * 2.2, 0, Math.PI * 2);
        cosmosCtx.strokeStyle = `rgba(${pl.ringColor[0]}, ${pl.ringColor[1]}, ${pl.ringColor[2]}, 0.35)`;
        cosmosCtx.lineWidth = 2;
        cosmosCtx.stroke();
        cosmosCtx.beginPath();
        cosmosCtx.arc(0, 0, pl.r * 1.8, 0, Math.PI * 2);
        cosmosCtx.strokeStyle = `rgba(${pl.ringColor[0]}, ${pl.ringColor[1]}, ${pl.ringColor[2]}, 0.2)`;
        cosmosCtx.lineWidth = 3;
        cosmosCtx.stroke();
        cosmosCtx.restore();
      }
    });

    spawnShootingStar();
    shootingStars = shootingStars.filter(s => {
      s.life -= s.decay;
      if (s.life <= 0) return false;
      s.x += Math.cos(s.angle) * s.speed;
      s.y += Math.sin(s.angle) * s.speed;
      const tailX = s.x - Math.cos(s.angle) * s.len;
      const tailY = s.y - Math.sin(s.angle) * s.len;
      const grad = cosmosCtx.createLinearGradient(tailX, tailY, s.x, s.y);
      grad.addColorStop(0, 'transparent');
      grad.addColorStop(0.5, `rgba(${s.cr}, ${s.cg}, ${s.cb}, ${s.life * 0.25})`);
      grad.addColorStop(1, `rgba(255, 255, 255, ${s.life * 0.9})`);
      cosmosCtx.beginPath();
      cosmosCtx.moveTo(tailX, tailY);
      cosmosCtx.lineTo(s.x, s.y);
      cosmosCtx.strokeStyle = grad;
      cosmosCtx.lineWidth = 2;
      cosmosCtx.stroke();
      const headGrad = cosmosCtx.createRadialGradient(s.x, s.y, 0, s.x, s.y, 6);
      headGrad.addColorStop(0, `rgba(255, 255, 255, ${s.life * 0.9})`);
      headGrad.addColorStop(0.5, `rgba(${s.cr}, ${s.cg}, ${s.cb}, ${s.life * 0.4})`);
      headGrad.addColorStop(1, 'transparent');
      cosmosCtx.fillStyle = headGrad;
      cosmosCtx.beginPath();
      cosmosCtx.arc(s.x, s.y, 6, 0, Math.PI * 2);
      cosmosCtx.fill();
      if (Math.random() < 0.4) {
        s.sparks.push({
          x: s.x + (Math.random() - 0.5) * 6,
          y: s.y + (Math.random() - 0.5) * 6,
          r: 0.5 + Math.random(),
          life: 0.6 + Math.random() * 0.4,
          decay: 0.02 + Math.random() * 0.03
        });
      }
      s.sparks = s.sparks.filter(sp => {
        sp.life -= sp.decay;
        if (sp.life <= 0) return false;
        cosmosCtx.beginPath();
        cosmosCtx.arc(sp.x, sp.y, sp.r * sp.life, 0, Math.PI * 2);
        cosmosCtx.fillStyle = `rgba(${s.cr}, ${s.cg}, ${s.cb}, ${sp.life * 0.6})`;
        cosmosCtx.fill();
        return true;
      });
      return true;
    });

    requestAnimationFrame(animateCosmos);
  }

  // --- LIVE TICKER ---
  let tickerInterval;
  function initTicker() {
    updateTicker();
    tickerInterval = setInterval(updateTicker, 4000);
  }

  function updateTicker() {
    const items = [];
    const dist = AetherixEngine.Orbital.earthMarsDistance(Math.random() * 360, 180 + Math.random() * 360);
    const lt = AetherixEngine.Orbital.lightTime(dist);
    const rate = AetherixEngine.Orbital.estimateDataRate(dist);
    items.push({ label: 'EARTH\u2013MARS', value: fmtKm(dist), color: 'var(--accent)' });
    items.push({ label: 'LIGHT TIME', value: fmt(lt / 60, 1) + ' min', color: 'var(--quantum)' });
    items.push({ label: 'DATA RATE', value: fmt(rate, 1) + ' Mbps', color: 'var(--success)' });
    items.push({ label: 'QKD KEY RATE', value: fmt(AetherixEngine.QKD.keyRate(225e6), 0) + ' bps', color: 'var(--nebula)' });
    const qkd = AetherixEngine.QKD.bb84(100, 0.02);
    items.push({ label: 'QBER', value: fmt(qkd.qber * 100, 2) + '%', color: qkd.secure ? 'var(--success)' : 'var(--danger)' });
    const el = $('live-ticker');
    if (el) {
      el.innerHTML = items.map(i => `<div class="ticker-item"><span class="ticker-dot" style="background:${i.color};box-shadow:0 0 6px ${i.color}"></span>${i.label}: <strong style="color:${i.color}">${i.value}</strong></div>`).join('');
    }
  }

  // --- NETWORK TOPOLOGY CANVAS ---
  const networkTopology = {
    'mars.surface.rover-01': ['mars.areo.alpha', 'mars.polar.gamma'],
    'mars.surface.base-alpha': ['mars.areo.alpha', 'mars.polar.gamma'],
    'mars.areo.alpha': ['mars.surface.rover-01', 'mars.polar.gamma', 'transit.esl4.relay', 'earth.leo.constellation'],
    'mars.polar.gamma': ['mars.surface.rover-01', 'mars.areo.alpha', 'transit.esl4.relay'],
    'transit.esl4.relay': ['mars.areo.alpha', 'mars.polar.gamma', 'earth.leo.constellation', 'earth.dsn.goldstone'],
    'earth.leo.constellation': ['mars.areo.alpha', 'transit.esl4.relay', 'earth.dsn.goldstone'],
    'earth.dsn.goldstone': ['transit.esl4.relay', 'earth.leo.constellation', 'earth.control.moc'],
    'earth.control.moc': ['earth.dsn.goldstone']
  };

  const nodePositions = {};
  let topoAnimFrame;
  let topoParticles = [];

  function initTopology() {
    const canvas = $('topologyCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    const w = rect.width, h = rect.height;

    const tiers = {
      'mars.surface.rover-01': 4, 'mars.surface.base-alpha': 4,
      'mars.areo.alpha': 3, 'mars.polar.gamma': 3,
      'transit.esl4.relay': 2,
      'earth.leo.constellation': 1,
      'earth.dsn.goldstone': 0.5, 'earth.control.moc': 0
    };

    const nodeNames = Object.keys(networkTopology);
    const tierCounts = {};
    nodeNames.forEach(n => {
      const t = tiers[n] || 0;
      if (!tierCounts[t]) tierCounts[t] = [];
      tierCounts[t].push(n);
    });

    const tierKeys = Object.keys(tierCounts).sort((a, b) => b - a);
    tierKeys.forEach(tier => {
      const nodes = tierCounts[tier];
      const y = h * 0.1 + (tierKeys.indexOf(tier) / (tierKeys.length - 1)) * h * 0.8;
      nodes.forEach((n, i) => {
        const xSpacing = w / (nodes.length + 1);
        nodePositions[n] = { x: xSpacing * (i + 1), y };
      });
    });

    for (let i = 0; i < 20; i++) {
      topoParticles.push({
        progress: Math.random(),
        speed: 0.001 + Math.random() * 0.003,
        edge: Math.floor(Math.random() * Object.keys(networkTopology).length)
      });
    }

    drawTopology(ctx, w, h);
  }

  function drawTopology(ctx, w, h) {
    ctx.clearRect(0, 0, w, h);

    const edges = [];
    Object.entries(networkTopology).forEach(([from, neighbors]) => {
      neighbors.forEach(to => {
        const key = [from, to].sort().join('|');
        if (!edges.find(e => e.key === key)) edges.push({ from, to, key });
      });
    });

    edges.forEach(edge => {
      const a = nodePositions[edge.from], b = nodePositions[edge.to];
      if (!a || !b) return;
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.strokeStyle = 'rgba(60, 100, 180, 0.15)';
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    topoParticles.forEach(p => {
      if (p.edge >= edges.length) p.edge = 0;
      const edge = edges[p.edge];
      const a = nodePositions[edge.from], b = nodePositions[edge.to];
      if (!a || !b) return;
      p.progress += p.speed;
      if (p.progress > 1) { p.progress = 0; p.edge = Math.floor(Math.random() * edges.length); }
      const px = a.x + (b.x - a.x) * p.progress;
      const py = a.y + (b.y - a.y) * p.progress;
      const grad = ctx.createRadialGradient(px, py, 0, px, py, 4);
      grad.addColorStop(0, 'rgba(0, 212, 255, 0.8)');
      grad.addColorStop(1, 'rgba(0, 212, 255, 0)');
      ctx.beginPath();
      ctx.arc(px, py, 4, 0, Math.PI * 2);
      ctx.fillStyle = grad;
      ctx.fill();
    });

    Object.entries(nodePositions).forEach(([name, pos]) => {
      const tier = name.includes('mars.surface') ? 'mars' : name.includes('mars') ? '#ff8855' : name.includes('transit') ? 'quantum' : name.includes('leo') ? 'accent' : '#00b894';
      const colors = {
        'mars': { fill: 'rgba(255,107,53,0.15)', stroke: '#ff6b35', text: '#ff6b35' },
        '#ff8855': { fill: 'rgba(255,136,85,0.12)', stroke: '#ff8855', text: '#ff8855' },
        'quantum': { fill: 'rgba(124,92,247,0.15)', stroke: '#7c5cf7', text: '#7c5cf7' },
        'accent': { fill: 'rgba(0,212,255,0.12)', stroke: '#00d4ff', text: '#00d4ff' },
        '#00b894': { fill: 'rgba(0,184,148,0.12)', stroke: '#00b894', text: '#00b894' }
      };
      const c = colors[tier] || colors['accent'];

      ctx.beginPath();
      ctx.arc(pos.x, pos.y, 10, 0, Math.PI * 2);
      ctx.fillStyle = c.fill;
      ctx.fill();
      ctx.strokeStyle = c.stroke;
      ctx.lineWidth = 1.5;
      ctx.stroke();

      ctx.beginPath();
      ctx.arc(pos.x, pos.y, 3, 0, Math.PI * 2);
      ctx.fillStyle = c.stroke;
      ctx.fill();

      const label = name.split('.').slice(-1)[0];
      ctx.font = '9px Inter, sans-serif';
      ctx.fillStyle = c.text;
      ctx.textAlign = 'center';
      ctx.fillText(label, pos.x, pos.y + 22);
    });

    topoAnimFrame = requestAnimationFrame(() => drawTopology(ctx, w, h));
  }

  // --- DASHBOARD ---
  function initDashboard() {
    const scenarios = AetherixEngine.LinkBudget.marsScenarios();
    const container = $('dashboard-scenarios');
    if (!container) return;
    container.innerHTML = '';
    const labels = { minimum: 'Minimum Distance (55M km)', average: 'Average (225M km)', maximum: 'Maximum Distance (390M km)' };
    const colors = { minimum: 'success', average: 'accent', maximum: 'danger' };
    for (const [key, s] of Object.entries(scenarios)) {
      container.innerHTML += `
        <div class="card stat-card ${colors[key]} animate-in stagger-${Object.keys(scenarios).indexOf(key) + 1}">
          <div class="card-title"><span class="ct-dot"></span> ${labels[key]}</div>
          <div class="card-value">${fmt(s.linkMarginDb)} <span class="card-unit">dB margin</span></div>
          <div class="link-budget-bar">
            <div class="lb-bar-segment" style="width:${Math.min(50, Math.max(5, (s.eirpDbm + 60) / 2))}%;background:rgba(0,212,255,0.3)">EIRP</div>
            <div class="lb-bar-segment" style="width:${Math.min(40, Math.max(5, Math.abs(s.freeSpaceLossDb) / 8))}%;background:rgba(248,81,73,0.25)">FSPL</div>
            <div class="lb-bar-segment" style="width:${Math.min(30, Math.max(3, (s.receiverAntennaGainDb) / 4))}%;background:rgba(63,185,80,0.3)">Rx</div>
          </div>
          <div class="result-row"><span class="result-label">Rx Power</span><span class="result-value">${fmt(s.receivedPowerDbm)} dBm</span></div>
          <div class="result-row"><span class="result-label">EIRP</span><span class="result-value">${fmt(s.eirpDbm)} dBm</span></div>
          <div class="result-row"><span class="result-label">FSPL</span><span class="result-value">${fmt(s.freeSpaceLossDb)} dB</span></div>
          <div class="result-row"><span class="result-label">Light Time</span><span class="result-value">${fmt(s.lightTimeMinutes)} min</span></div>
          <div style="margin-top:10px"><span class="badge ${s.linkStatus === 'POSITIVE' ? 'success' : 'danger'}">${s.linkStatus}</span></div>
        </div>`;
    }

    const timeline = AetherixEngine.Orbital.distanceTimeline(780);
    destroyChart('dashTimeline');
    const chartEl = $('dashTimelineChart');
    if (!chartEl) return;
    const ctx = chartEl.getContext('2d');
    charts.dashTimeline = new Chart(ctx, {
      type: 'line',
      data: {
        labels: timeline.map(t => t.day),
        datasets: [
          { label: 'Distance (M km)', data: timeline.map(t => t.distanceMKm), borderColor: '#00d4ff', backgroundColor: 'rgba(0,212,255,0.05)', fill: true, tension: 0.4, pointRadius: 0, borderWidth: 2 },
          { label: 'Data Rate (Mbps)', data: timeline.map(t => t.dataRateMbps), borderColor: '#3fb950', backgroundColor: 'rgba(63,185,80,0.05)', fill: true, tension: 0.4, pointRadius: 0, borderWidth: 1.5, yAxisID: 'y1' }
        ]
      },
      options: { ...chartTheme, scales: { ...chartTheme.scales, x: { ...chartTheme.scales.x, title: { display: true, text: 'Day of Synodic Period', color: '#4a5270' } }, y: { ...chartTheme.scales.y, title: { display: true, text: 'Distance (M km)', color: '#00d4ff' } }, y1: { ...chartTheme.scales.y, title: { display: true, text: 'Data Rate (Mbps)', color: '#3fb950' }, position: 'right', grid: { drawOnChartArea: false } } } }
    });
  }

  // --- LINK BUDGET ---
  const linkBudget = {
    loadScenario(scenario) {
      const dist = { minimum: 55, average: 225, maximum: 390 };
      $('lb-distance').value = dist[scenario];
      this.calculate();
    },
    calculate() {
      const distanceKm = parseFloat($('lb-distance').value) * 1e6;
      const result = AetherixEngine.LinkBudget.calculate({
        distanceKm,
        txPowerWatts: parseFloat($('lb-tx-power').value),
        txApertureM: parseFloat($('lb-tx-aperture').value),
        rxApertureM: parseFloat($('lb-rx-aperture').value),
        dataRateMbps: parseFloat($('lb-data-rate').value),
        requiredSnrDb: parseFloat($('lb-snr').value)
      });
      const sc = result.linkStatus === 'POSITIVE' ? 'var(--success)' : 'var(--danger)';
      $('lb-result').style.display = 'block';
      $('lb-result-content').innerHTML = `
        <div style="text-align:center;padding:16px 0;margin-bottom:14px;border:1px solid ${sc};border-radius:var(--radius-lg);background:${result.linkStatus === 'POSITIVE' ? 'var(--success-dim)' : 'var(--danger-dim)'}">
          <div style="font-size:2.2rem;font-weight:800;color:${sc};font-family:var(--font-mono)">${fmt(result.linkMarginDb)} dB</div>
          <div style="font-size:0.75rem;color:var(--text-secondary);margin-top:4px;letter-spacing:2px">LINK MARGIN</div>
        </div>
        <div class="link-budget-bar">
          <div class="lb-bar-segment" style="width:25%;background:rgba(0,212,255,0.25);color:#00d4ff">EIRP ${fmt(result.eirpDbm)}</div>
          <div class="lb-bar-segment" style="width:45%;background:rgba(248,81,73,0.2);color:#f85149">FSPL ${fmt(result.freeSpaceLossDb)}</div>
          <div class="lb-bar-segment" style="width:30%;background:rgba(63,185,80,0.25);color:#3fb950">Rx ${fmt(result.receivedPowerDbm)}</div>
        </div>
        <div class="result-row"><span class="result-label">Distance</span><span class="result-value">${fmtKm(result.distanceKm)}</span></div>
        <div class="result-row"><span class="result-label">One-Way Light Time</span><span class="result-value">${fmtTime(result.lightTimeSeconds)}</span></div>
        <div class="result-row"><span class="result-label">EIRP</span><span class="result-value">${fmt(result.eirpDbm)} dBm</span></div>
        <div class="result-row"><span class="result-label">Free Space Loss</span><span class="result-value">${fmt(result.freeSpaceLossDb)} dB</span></div>
        <div class="result-row"><span class="result-label">Received Power</span><span class="result-value">${fmt(result.receivedPowerDbm)} dBm</span></div>
        <div class="result-row"><span class="result-label">Data Rate</span><span class="result-value">${fmt(result.dataRateMbps)} Mbps</span></div>
        <div class="result-row"><span class="result-label">Status</span><span class="badge ${result.linkStatus === 'POSITIVE' ? 'success' : 'danger'} ${result.linkStatus === 'POSITIVE' ? 'badge-pulse' : ''}">${result.linkStatus}</span></div>`;
      this.drawChart();
      toast('Link budget calculated \u2014 margin: ' + fmt(result.linkMarginDb) + ' dB', result.linkStatus === 'POSITIVE' ? 'success' : 'error');
    },
    drawChart() {
      $('lb-chart-card').style.display = 'block';
      const distances = [], margins = [], rxPowers = [];
      for (let d = 54; d <= 401; d += 4) {
        distances.push(d);
        const r = AetherixEngine.LinkBudget.calculate({ distanceKm: d * 1e6 });
        margins.push(r.linkMarginDb);
        rxPowers.push(r.receivedPowerDbm);
      }
      destroyChart('lbChart');
      charts.lbChart = new Chart($('lbChart').getContext('2d'), {
        type: 'line',
        data: { labels: distances, datasets: [
          { label: 'Link Margin (dB)', data: margins, borderColor: '#00d4ff', tension: 0.4, pointRadius: 0, borderWidth: 2 },
          { label: 'Rx Power (dBm)', data: rxPowers, borderColor: '#ff6b35', tension: 0.4, pointRadius: 0, borderWidth: 1.5 }
        ]},
        options: { ...chartTheme, scales: { ...chartTheme.scales, x: { ...chartTheme.scales.x, title: { display: true, text: 'Distance (M km)', color: '#4a5270' } } } }
      });
    }
  };

  // --- ROUTING ---
  const routing = {
    decide() {
      const node = $('rt-current-node').value;
      const dest = $('rt-destination').value;
      const neighbors = networkTopology[node] || [];
      const linkQualities = {};
      neighbors.forEach(n => { linkQualities[n] = 0.4 + Math.random() * 0.6; });
      const state = { currentNode: node, neighbors, linkQualities, bufferOccupancy: parseFloat($('rt-buffer').value) / 100, bundlePriority: parseInt($('rt-priority').value), bundleSizeMb: 500, bundleDeadlineHours: 168, destination: dest };
      const decision = AetherixEngine.Routing.selectAction(state);
      $('rt-result').style.display = 'block';
      $('rt-route-visual').style.display = 'none';
      const ac = { FORWARD: 'accent', STORE: 'warning', DROP: 'danger' };
      $('rt-result-content').innerHTML = `
        <div style="text-align:center;padding:16px 0;margin-bottom:14px">
          <div class="badge ${ac[decision.action]}" style="font-size:1.1rem;padding:8px 24px">${decision.action}</div>
          ${decision.nextHop ? `<div style="margin-top:10px;font-size:0.8rem;color:var(--text-secondary)">Next Hop: <strong style="color:var(--text-primary)">${decision.nextHop}</strong></div>` : ''}
        </div>
        <div class="result-row"><span class="result-label">Confidence</span><span class="result-value">${fmt(decision.confidence * 100, 1)}%</span></div>
        <div class="result-row"><span class="result-label">Reasoning</span><span class="result-value" style="font-family:var(--font);font-size:0.85rem;color:var(--text-secondary)">${decision.reasoning}</span></div>
        <div style="margin-top:14px"><div style="font-size:0.7rem;color:var(--text-muted);margin-bottom:8px;letter-spacing:1px">LINK QUALITIES</div>
        ${neighbors.map(n => `<div class="result-row"><span class="result-label">${n}</span><div style="display:flex;align-items:center;gap:8px"><div style="width:60px;height:5px;border-radius:3px;background:rgba(var(--accent-rgb),0.1);overflow:hidden"><div style="height:100%;width:${linkQualities[n] * 100}%;background:${linkQualities[n] > 0.7 ? 'var(--success)' : linkQualities[n] > 0.5 ? 'var(--accent)' : 'var(--warning)'};border-radius:3px"></div></div><span class="result-value">${fmt(linkQualities[n] * 100, 1)}%</span></div></div>`).join('')}</div>`;
      toast('Routing decision: ' + decision.action + (decision.nextHop ? ' \u2192 ' + decision.nextHop : ''), 'quantum');

      destroyChart('routingChart');
      const rtChartEl = $('routingChart');
      if (rtChartEl) {
        $('rt-chart-card').style.display = 'block';
        const actions = ['FORWARD', 'STORE', 'DROP', 'SPLIT'];
        const confidences = actions.map(a => {
          const s = { ...state };
          const d = AetherixEngine.Routing.selectAction(s);
          return a === decision.action ? decision.confidence * 100 : Math.max(0, (decision.confidence * 100) * (0.2 + Math.random() * 0.5));
        });
        const colors = ['#388bfd', '#d29922', '#f85149', '#a371f7'];
        charts.routingChart = new Chart(rtChartEl.getContext('2d'), {
          type: 'bar',
          data: {
            labels: actions,
            datasets: [{ label: 'Confidence (%)', data: confidences, backgroundColor: colors.map(c => c + '99'), borderColor: colors, borderWidth: 2 }]
          },
          options: {
            indexAxis: 'y', responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false }, title: { display: true, text: 'Agent Confidence by Action', color: '#c9d1d9' } },
            scales: {
              x: { min: 0, max: 100, title: { display: true, text: 'Confidence %', color: '#8b949e' }, ticks: { color: '#8b949e' }, grid: { color: 'rgba(139,148,158,0.1)' } },
              y: { ticks: { color: '#c9d1d9', font: { weight: 'bold' } }, grid: { display: false } }
            }
          }
        });
      }
    },
    simulateFullRoute() {
      const src = $('rt-current-node').value, dest = $('rt-destination').value;
      const route = this.findRoute(src, dest);
      if (!route) { toast('No route found', 'error'); return; }
      const sim = AetherixEngine.Routing.simulateRoute(route, { priority: parseInt($('rt-priority').value), sizeMb: 500, deadlineHours: 168 });
      $('rt-route-visual').style.display = 'block';
      $('rt-result').style.display = 'none';
      const nodeDots = route.map((n, i) => {
        const step = sim.steps.find(s => s.step === i + 1);
        let cls = 'active';
        if (step) { if (step.action === 'DROP') cls = 'drop'; else if (step.action === 'STORE') cls = 'store'; }
        if (i === route.length - 1 && sim.delivered) cls = 'delivered';
        return `<div class="route-node"><div class="route-node-dot ${cls}">${i + 1}</div><div class="route-node-label">${n.split('.').slice(-1)[0]}</div></div>`;
      }).join('<div class="route-arrow active"></div>');
      $('rt-route-content').innerHTML = `
        <div class="route-visual">${nodeDots}</div>
        <div class="grid grid-4" style="margin-top:18px">
          <div class="card stat-card ${sim.delivered ? 'success' : 'danger'}"><div class="card-title">Status</div><div class="card-value">${sim.delivered ? 'DELIVERED' : 'FAILED'}</div></div>
          <div class="card stat-card accent"><div class="card-title">Total Delay</div><div class="card-value">${fmtTime(sim.totalDelay)}</div></div>
          <div class="card stat-card mars"><div class="card-title">Hops</div><div class="card-value">${sim.totalHops}</div></div>
          <div class="card stat-card quantum"><div class="card-title">Reward</div><div class="card-value">${fmt(sim.reward, 4)}</div></div>
        </div>
        <div style="margin-top:14px"><div class="table-wrapper"><table><thead><tr><th>Step</th><th>Node</th><th>Action</th><th>Next Hop</th><th>Delay</th><th>Conf</th></tr></thead><tbody>
        ${sim.steps.map(s => `<tr><td>${s.step}</td><td>${s.node}</td><td><span class="badge ${s.action === 'FORWARD' ? 'accent' : s.action === 'STORE' ? 'warning' : 'danger'}">${s.action}</span></td><td>${s.nextHop || '\u2014'}</td><td>${fmtTime(s.delaySec)}</td><td>${fmt(s.confidence * 100, 1)}%</td></tr>`).join('')}
        </tbody></table></div></div>`;
      toast(sim.delivered ? 'Bundle delivered via ' + sim.totalHops + ' hops' : 'Delivery failed', sim.delivered ? 'success' : 'error');
    },
    findRoute(src, dest) {
      const visited = new Set();
      const queue = [[src]];
      while (queue.length > 0) {
        const path = queue.shift();
        const node = path[path.length - 1];
        if (node === dest) return path;
        if (visited.has(node)) continue;
        visited.add(node);
        for (const n of (networkTopology[node] || [])) { if (!visited.has(n)) queue.push([...path, n]); }
      }
      return null;
    }
  };

  // --- QKD ---
  const qkd = {
    init() {
      const distances = [
        { name: 'LEO (500 km)', km: 500 },
        { name: 'GEO (36,000 km)', km: 36000 },
        { name: 'Lunar (384,000 km)', km: 384000 },
        { name: 'Mars (225M km)', km: 225000000 }
      ];
      let html = '<div class="table-wrapper"><table><thead><tr><th>Link</th><th>Distance</th><th>Key Rate</th></tr></thead><tbody>';
      distances.forEach(d => {
        const rate = AetherixEngine.QKD.keyRate(d.km);
        html += `<tr><td>${d.name}</td><td>${fmtKm(d.km)}</td><td>${rate > 1000 ? fmt(rate / 1000, 1) + ' kbps' : fmt(rate, 1) + ' bps'}</td></tr>`;
      });
      html += '</tbody></table></div>';
      const el = $('qkd-key-rates');
      if (el) el.innerHTML = html;
    },
    run(errorOverride) {
      const protocol = $('qkd-protocol').value;
      const numQubits = parseInt($('qkd-num-qubits').value);
      const error = errorOverride !== undefined ? errorOverride : parseFloat($('qkd-error').value) / 100;
      let result = protocol === 'bb84' ? AetherixEngine.QKD.bb84(numQubits, error) : AetherixEngine.QKD.e91(numQubits, error);
      this.renderResult(result);
    },
    runEavesdropper() { this.run(0.25); },
    renderResult(r) {
      $('qkd-result').style.display = 'block';
      const aliceBits = r.aliceKeyPreview, bobBits = r.bobKeyPreview;
      let keyDisplay = '<div style="margin-bottom:8px;font-size:0.7rem;color:var(--text-muted);letter-spacing:1px">SIFTED KEY \u2014 FIRST 40 BITS</div><div class="key-display">';
      for (let i = 0; i < aliceBits.length; i++) {
        const match = aliceBits[i] === bobBits[i];
        keyDisplay += `<span class="key-bit ${match ? 'match' : 'mismatch'}">${aliceBits[i]}</span>`;
      }
      keyDisplay += '</div>';

      const steps = r.protocol === 'BB84' ? [
        { title: 'Quantum Transmission', desc: 'Alice prepares ' + r.rawQubits + ' qubits in random bases' },
        { title: 'Measurement', desc: 'Bob measures each qubit in random basis' },
        { title: 'Basis Reconciliation', desc: 'Public comparison \u2014 ' + r.siftedKeyLength + ' matching bases' },
        { title: 'QBER Estimation', desc: 'Error rate: ' + fmt(r.qber * 100, 2) + '% (threshold: 11%)' },
        { title: r.secure ? 'Key Confirmed Secure' : 'EAVESDROPPER DETECTED', desc: r.secure ? 'Privacy amplification applied' : 'QBER exceeds security threshold \u2014 aborting' }
      ] : [
        { title: 'Entangled Pair Distribution', desc: r.rawPairs + ' Bell pairs generated and distributed' },
        { title: 'Independent Measurement', desc: 'Alice and Bob randomly choose measurement bases' },
        { title: 'Key Sifting', desc: r.siftedKeyLength + ' matching basis measurements retained' },
        { title: 'Bell Test', desc: 'Bell parameter S = ' + (r.bellViolation || 'N/A') + ' (classical limit: 2.0)' },
        { title: r.secure ? 'Key Verified via Entanglement' : 'EAVESDROPPER DETECTED', desc: r.secure ? 'Device-independent security confirmed' : 'Bell inequality not violated \u2014 aborting' }
      ];

      $('qkd-result-content').innerHTML = `
        <div style="text-align:center;padding:16px 0;margin-bottom:14px;border:1px solid ${r.secure ? 'var(--success)' : 'var(--danger)'};border-radius:var(--radius-lg);background:${r.secure ? 'var(--success-dim)' : 'var(--danger-dim)'}">
          <div style="font-size:1.6rem;font-weight:800;color:${r.secure ? 'var(--success)' : 'var(--danger)'};font-family:var(--font-mono)">${r.status}</div>
          <div style="font-size:0.8rem;color:var(--text-secondary);margin-top:4px">${r.protocol} Protocol \u00b7 ${r.errors} bit errors</div>
        </div>
        <div class="protocol-steps">${steps.map((s, i) => `<div class="protocol-step"><div class="protocol-step-num">${i + 1}</div><div class="protocol-step-content"><div class="protocol-step-title">${s.title}</div><div class="protocol-step-desc">${s.desc}</div></div></div>`).join('')}</div>
        <div class="result-row"><span class="result-label">Sifted Key Length</span><span class="result-value">${r.siftedKeyLength} bits</span></div>
        <div class="result-row"><span class="result-label">Efficiency</span><span class="result-value">${fmt(r.efficiency * 100, 1)}%</span></div>
        <div class="result-row"><span class="result-label">QBER</span><span class="result-value" style="color:${r.qber < 0.11 ? 'var(--success)' : 'var(--danger)'}">${fmt(r.qber * 100, 2)}%</span></div>
        ${r.bellViolation ? `<div class="result-row"><span class="result-label">Bell Parameter</span><span class="result-value">${r.bellViolation} <span style="font-size:0.7rem;color:var(--text-muted)">(S > 2 = quantum)</span></span></div>` : ''}
        <div style="margin-top:14px">${keyDisplay}</div>
        <div style="display:flex;gap:6px;margin-top:8px"><span class="key-bit match" style="font-size:0.55rem;width:auto;padding:2px 8px;border-radius:3px">Match</span><span class="key-bit mismatch" style="font-size:0.55rem;width:auto;padding:2px 8px;border-radius:3px">Mismatch</span></div>`;
      toast(r.protocol + ' simulation complete \u2014 ' + r.status, r.secure ? 'quantum' : 'error');

      destroyChart('qkdChart');
      const qkdChartEl = $('qkdChart');
      if (qkdChartEl) {
        $('qkd-chart-card').style.display = 'block';
        const errorRates = [];
        const keyLengths = [];
        const qberLine = [];
        for (let e = 0; e <= 25; e += 1) {
          errorRates.push(e);
          const sim = AetherixEngine.QKD.bb84(numQubits, e / 100);
          keyLengths.push(sim.secure ? sim.siftedKeyLength : 0);
          qberLine.push(11);
        }
        charts.qkdChart = new Chart(qkdChartEl.getContext('2d'), {
          type: 'bar',
          data: {
            labels: errorRates.map(e => e + '%'),
            datasets: [
              { label: 'Secret Key Length (bits)', data: keyLengths, backgroundColor: keyLengths.map(k => k > 0 ? 'rgba(56,139,253,0.6)' : 'rgba(248,81,73,0.3)'), borderColor: keyLengths.map(k => k > 0 ? '#388bfd' : '#f85149'), borderWidth: 1 },
              { label: 'Security Threshold (11%)', data: qberLine, type: 'line', borderColor: '#f85149', borderDash: [5, 5], borderWidth: 2, pointRadius: 0, fill: false, yAxisID: 'y1' }
            ]
          },
          options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { position: 'top', labels: { color: '#8b949e', font: { size: 11 } } }, title: { display: true, text: 'Key Length vs Channel Error Rate', color: '#c9d1d9' } },
            scales: {
              x: { title: { display: true, text: 'Channel Error Rate', color: '#8b949e' }, ticks: { color: '#8b949e' }, grid: { color: 'rgba(139,148,158,0.1)' } },
              y: { title: { display: true, text: 'Secret Key Bits', color: '#8b949e' }, ticks: { color: '#8b949e' }, grid: { color: 'rgba(139,148,158,0.1)' } },
              y1: { position: 'right', title: { display: true, text: 'QBER Threshold (%)', color: '#f85149' }, min: 0, max: 25, ticks: { color: '#f85149' }, grid: { display: false } }
            }
          }
        });
      }
    }
  };

  // --- ORBITAL ---
  const orbital = {
    calculate() {
      const startDay = parseInt($('orb-start-day').value);
      const duration = parseInt($('orb-duration').value);
      const timeline = AetherixEngine.Orbital.distanceTimeline(duration);
      const windows = AetherixEngine.Orbital.contactWindows(startDay, duration);

      destroyChart('orbTimeline');
      const chartEl = $('orbTimelineChart');
      if (!chartEl) return;
      charts.orbTimeline = new Chart(chartEl.getContext('2d'), {
        type: 'line',
        data: { labels: timeline.map(t => t.day), datasets: [
          { label: 'Distance (M km)', data: timeline.map(t => t.distanceMKm), borderColor: '#00d4ff', fill: false, tension: 0.4, pointRadius: 0, borderWidth: 2 },
          { label: 'Light Time (min)', data: timeline.map(t => t.lightTimeMin), borderColor: '#ff6b35', fill: false, tension: 0.4, pointRadius: 0, borderWidth: 1.5, yAxisID: 'y1' }
        ]},
        options: { ...chartTheme, scales: { ...chartTheme.scales, x: { ...chartTheme.scales.x, title: { display: true, text: 'Day', color: '#4a5270' } }, y: { ...chartTheme.scales.y, title: { display: true, text: 'Distance (M km)', color: '#00d4ff' } }, y1: { ...chartTheme.scales.y, title: { display: true, text: 'Light Time (min)', color: '#ff6b35' }, position: 'right', grid: { drawOnChartArea: false } } } }
      });

      const totalHours = windows.reduce((s, w) => s + w.durationHours, 0);
      const avgDist = windows.length > 0 ? windows.reduce((s, w) => s + w.distanceKm, 0) / windows.length : 0;
      const avgRate = windows.length > 0 ? windows.reduce((s, w) => s + w.maxDataRateMbps, 0) / windows.length : 0;

      $('orb-stats-content').innerHTML = `<div class="grid grid-4">
        <div><div style="font-size:0.7rem;color:var(--text-muted);letter-spacing:1px">CONTACT WINDOWS</div><div style="font-size:1.4rem;font-weight:700;font-family:var(--font-mono);color:var(--accent)">${windows.length}</div></div>
        <div><div style="font-size:0.7rem;color:var(--text-muted);letter-spacing:1px">TOTAL HOURS</div><div style="font-size:1.4rem;font-weight:700;font-family:var(--font-mono);color:var(--quantum)">${fmt(totalHours, 1)}</div></div>
        <div><div style="font-size:0.7rem;color:var(--text-muted);letter-spacing:1px">AVG DISTANCE</div><div style="font-size:1.4rem;font-weight:700;font-family:var(--font-mono);color:var(--mars)">${fmt(avgDist / 1e6, 1)}M km</div></div>
        <div><div style="font-size:0.7rem;color:var(--text-muted);letter-spacing:1px">AVG DATA RATE</div><div style="font-size:1.4rem;font-weight:700;font-family:var(--font-mono);color:var(--success)">${fmt(avgRate, 1)} Mbps</div></div>
      </div>`;

      let tableHtml = '';
      if (windows.length > 0) {
        tableHtml = '<div class="table-wrapper"><table><thead><tr><th>Day</th><th>Duration</th><th>Distance</th><th>Data Rate</th><th>Elevation</th></tr></thead><tbody>';
        windows.slice(0, 20).forEach(w => {
          tableHtml += `<tr><td>${w.day}</td><td>${fmt(w.durationHours, 1)} hrs</td><td>${fmt(w.distanceMKm, 1)}M km</td><td>${fmt(w.maxDataRateMbps, 1)} Mbps</td><td>${fmt(w.elevationDeg, 1)}\u00b0</td></tr>`;
        });
        if (windows.length > 20) tableHtml += `<tr><td colspan="5" style="text-align:center;color:var(--text-muted)">... and ${windows.length - 20} more windows</td></tr>`;
        tableHtml += '</tbody></table></div>';
      } else {
        tableHtml = '<div class="empty-state"><div class="icon">&#9788;</div>No contact windows \u2014 solar conjunction blackout</div>';
      }
      $('orb-windows-content').innerHTML = tableHtml;
      toast(windows.length + ' contact windows found over ' + duration + ' days', 'info');
    }
  };

  // --- BUNDLE ---
  const bundle = {
    create() {
      const b = AetherixEngine.Bundle.create({
        source: $('bndl-source').value, destination: $('bndl-dest').value,
        priority: parseInt($('bndl-priority').value), sizeMb: parseFloat($('bndl-size').value),
        deadlineHours: parseFloat($('bndl-deadline').value), lifetimeDays: parseFloat($('bndl-lifetime').value)
      });
      bundles.push(b);
      this.renderBundle(b);
      this.renderList();
      toast('Bundle ' + b.id + ' created (' + fmt(b.sizeMb, 0) + ' MB, ' + b.priorityName + ')', 'success');
      return b;
    },
    createAndRoute() {
      const b = this.create();
      const route = routing.findRoute(b.source, b.destination);
      if (route) {
        const sim = AetherixEngine.Routing.simulateRoute(route, { priority: b.priority, sizeMb: b.sizeMb, deadlineHours: b.deadlineHours });
        let html = '<div style="margin-top:18px"><div class="card-title"><span class="ct-dot"></span> Route Simulation</div><div class="route-visual">';
        route.forEach((n, i) => {
          const step = sim.steps.find(s => s.step === i + 1);
          let cls = 'active';
          if (step) { if (step.action === 'DROP') cls = 'drop'; else if (step.action === 'STORE') cls = 'store'; }
          if (i === route.length - 1 && sim.delivered) cls = 'delivered';
          html += `<div class="route-node"><div class="route-node-dot ${cls}">${i + 1}</div><div class="route-node-label">${n.split('.').slice(-1)[0]}</div></div>`;
          if (i < route.length - 1) html += '<div class="route-arrow active"></div>';
        });
        html += '</div>';
        html += `<div style="margin-top:14px;text-align:center"><span class="badge ${sim.delivered ? 'success' : 'danger'}">${sim.delivered ? 'DELIVERED' : 'FAILED'}</span> <span style="color:var(--text-secondary);font-size:0.8rem">${fmtTime(sim.totalDelay)} \u00b7 ${sim.totalHops} hops \u00b7 Reward: ${fmt(sim.reward, 4)}</span></div></div>`;
        $('bndl-result-content').insertAdjacentHTML('beforeend', html);
      }

      const bndlRouteCard = $('bndl-route-card');
      if (bndlRouteCard && route) {
        bndlRouteCard.style.display = 'block';
        const tierColors = { 'earth': '#388bfd', 'transit': '#a371f7', 'mars': '#f78166' };
        let routeHtml = '<div style="display:flex;align-items:center;flex-wrap:wrap;gap:6px;margin-bottom:16px">';
        route.forEach((n, i) => {
          const tier = n.startsWith('earth') ? 'earth' : n.startsWith('transit') ? 'transit' : 'mars';
          const step = sim.steps.find(s => s.step === i + 1);
          let bg = tierColors[tier] || '#388bfd';
          let cls = '';
          if (step) { if (step.action === 'DROP') cls = 'opacity:0.4;'; else if (step.action === 'STORE') cls = 'border-style:dashed;'; }
          if (i === route.length - 1 && sim.delivered) bg = '#3fb950';
          routeHtml += `<div style="padding:6px 14px;border-radius:8px;border:2px solid ${bg};background:${bg}22;font-size:0.8rem;font-weight:600;${cls}">${n.split('.').slice(-1)[0]}</div>`;
          if (i < route.length - 1) routeHtml += '<div style="color:var(--text-muted);font-size:0.7rem">&#8594;</div>';
        });
        routeHtml += '</div>';
        routeHtml += `<div style="display:flex;gap:16px;font-size:0.85rem;color:var(--text-secondary)"><span><strong style="color:var(--text-primary)">${sim.totalHops}</strong> hops</span><span><strong style="color:var(--text-primary)">${fmtTime(sim.totalDelay)}</strong> total delay</span><span>Delivery: <span class="badge ${sim.delivered ? 'success' : 'danger'}">${sim.delivered ? 'SUCCESS' : 'FAILED'}</span></span></div>`;
        $('bndl-route-visual').innerHTML = routeHtml;
      }
    },
    renderBundle(b) {
      const pc = ['danger', 'mars', 'accent', 'warning', 'quantum'];
      $('bndl-result').style.display = 'block';
      $('bndl-result-content').innerHTML = `
        <div style="text-align:center;padding:10px 0;margin-bottom:14px">
          <div style="font-size:1.4rem;font-weight:700;font-family:var(--font-mono);color:var(--accent)">${b.id}</div>
          <span class="badge ${pc[b.priority]}">${b.priorityName}</span>
        </div>
        <div class="result-row"><span class="result-label">Source</span><span class="result-value" style="font-family:var(--font)">${b.source}</span></div>
        <div class="result-row"><span class="result-label">Destination</span><span class="result-value" style="font-family:var(--font)">${b.destination}</span></div>
        <div class="result-row"><span class="result-label">Payload</span><span class="result-value">${fmt(b.sizeMb, 0)} MB</span></div>
        <div class="result-row"><span class="result-label">Deadline</span><span class="result-value">${b.deadlineHours} hrs</span></div>
        <div class="result-row"><span class="result-label">Lifetime</span><span class="result-value">${b.lifetimeDays} days</span></div>
        <div class="result-row"><span class="result-label">Status</span><span class="badge accent badge-pulse">${b.status}</span></div>`;
    },
    renderList() {
      if (bundles.length === 0) { $('bndl-list').innerHTML = '<div class="empty-state"><div class="icon">&#9638;</div>No bundles created yet</div>'; return; }
      const pc = ['danger', 'mars', 'accent', 'warning', 'quantum'];
      let html = '<div class="table-wrapper"><table><thead><tr><th>ID</th><th>Source</th><th>Dest</th><th>Priority</th><th>Size</th><th>Status</th></tr></thead><tbody>';
      bundles.forEach(b => { html += `<tr><td style="color:var(--accent)">${b.id}</td><td>${b.source.split('.').slice(-1)[0]}</td><td>${b.destination.split('.').slice(-1)[0]}</td><td><span class="badge ${pc[b.priority]}">${b.priorityName}</span></td><td>${fmt(b.sizeMb, 0)} MB</td><td><span class="badge accent">${b.status}</span></td></tr>`; });
      html += '</tbody></table></div>';
      $('bndl-list').innerHTML = html;
    }
  };

  // --- MISSION ---
  const mission = {
    run() {
      const startDay = parseInt($('msn-start').value);
      const duration = parseInt($('msn-duration').value);
      const bundleCount = parseInt($('msn-bundles').value);
      toast('Running Mars Mission simulation...', 'quantum');
      const result = AetherixEngine.Mission.runScenario({ startDay, durationDays: duration, bundleCount });
      $('msn-results').style.display = 'block';

      $('msn-stats').innerHTML = `
        <div class="card stat-card accent animate-in stagger-1"><div class="card-title">Contact Windows</div><div class="card-value">${result.contactWindows.length}<span class="card-unit"> windows</span></div></div>
        <div class="card stat-card mars animate-in stagger-2"><div class="card-title">Avg Distance</div><div class="card-value">${fmt(result.avgDistanceMKm, 1)}<span class="card-unit"> M km</span></div></div>
        <div class="card stat-card success animate-in stagger-3"><div class="card-title">Total Data</div><div class="card-value">${fmt(result.totalDataTransferGB, 1)}<span class="card-unit"> GB</span></div></div>
        <div class="card stat-card quantum animate-in stagger-4"><div class="card-title">Bundles</div><div class="card-value">${result.totalBundles}<span class="card-unit"> (${fmt(result.totalVolumeMb / 1024, 1)} GB)</span></div></div>`;

      destroyChart('msnChart');
      destroyChart('msnBundleChart');

      charts.msnChart = new Chart($('msnChart').getContext('2d'), {
        type: 'line',
        data: { labels: result.timeline.map(t => t.day), datasets: [
          { label: 'Distance (M km)', data: result.timeline.map(t => t.distanceMKm), borderColor: '#00d4ff', tension: 0.4, pointRadius: 0, borderWidth: 2 },
          { label: 'Data Rate (Mbps)', data: result.timeline.map(t => t.dataRateMbps), borderColor: '#3fb950', tension: 0.4, pointRadius: 0, borderWidth: 1.5, yAxisID: 'y1' }
        ]},
        options: { ...chartTheme, scales: { ...chartTheme.scales, x: { ...chartTheme.scales.x, title: { display: true, text: 'Day', color: '#4a5270' } }, y: { ...chartTheme.scales.y, title: { display: true, text: 'Distance (M km)', color: '#00d4ff' } }, y1: { ...chartTheme.scales.y, title: { display: true, text: 'Mbps', color: '#3fb950' }, position: 'right', grid: { drawOnChartArea: false } } } }
      });

      charts.msnBundleChart = new Chart($('msnBundleChart').getContext('2d'), {
        type: 'doughnut',
        data: { labels: result.bundles.map(b => b.name), datasets: [{ data: result.bundles.map(b => b.volumeMb), backgroundColor: ['#f85149', '#ff6b35', '#00d4ff', '#d29922', '#7c5cf7'], borderColor: '#0c1530', borderWidth: 2 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { color: '#8892aa', font: { size: 10 }, padding: 8, usePointStyle: true } } } }
      });

      const sim = result.routingSimulation;
      $('msn-routing').innerHTML = `
        <div style="text-align:center;margin-bottom:14px"><span class="badge ${sim.delivered ? 'success' : 'danger'}" style="font-size:0.9rem;padding:5px 16px">${sim.delivered ? 'DELIVERED' : 'FAILED'}</span></div>
        <div class="result-row"><span class="result-label">Total Delay</span><span class="result-value">${fmtTime(sim.totalDelay)}</span></div>
        <div class="result-row"><span class="result-label">Hops</span><span class="result-value">${sim.totalHops}</span></div>
        <div class="result-row"><span class="result-label">Reward</span><span class="result-value">${fmt(sim.reward, 4)}</span></div>
        <div style="margin-top:12px"><div class="table-wrapper"><table><thead><tr><th>#</th><th>Node</th><th>Action</th><th>Delay</th></tr></thead><tbody>
        ${sim.steps.map(s => `<tr><td>${s.step}</td><td>${s.node.split('.').slice(-1)[0]}</td><td><span class="badge ${s.action === 'FORWARD' ? 'accent' : s.action === 'STORE' ? 'warning' : 'danger'}">${s.action}</span></td><td>${fmtTime(s.delaySec)}</td></tr>`).join('')}
        </tbody></table></div></div>`;

      const c = result.qkdClean, e = result.qkdEavesdropped;
      $('msn-qkd').innerHTML = `<div class="grid grid-2" style="gap:14px">
        <div><div style="font-size:0.8rem;font-weight:600;margin-bottom:10px">Secure Channel</div>
          <div style="padding:16px;border:1px solid var(--success);border-radius:var(--radius-lg);background:var(--success-dim);text-align:center">
            <span class="badge success badge-pulse">${c.status}</span>
            <div style="margin-top:10px;font-size:0.8rem;color:var(--text-secondary)">QBER: <strong style="color:var(--success)">${fmt(c.qber * 100, 2)}%</strong> \u00b7 Key: ${c.siftedKeyLength} bits</div>
          </div></div>
        <div><div style="font-size:0.8rem;font-weight:600;margin-bottom:10px">Eavesdropper Present</div>
          <div style="padding:16px;border:1px solid var(--danger);border-radius:var(--radius-lg);background:var(--danger-dim);text-align:center">
            <span class="badge danger">${e.status}</span>
            <div style="margin-top:10px;font-size:0.8rem;color:var(--text-secondary)">QBER: <strong style="color:var(--danger)">${fmt(e.qber * 100, 2)}%</strong> \u00b7 Key: ${e.siftedKeyLength} bits</div>
          </div></div>
      </div>`;
      toast('Mars Mission simulation complete \u2014 ' + result.totalBundles + ' bundles, ' + fmt(result.totalDataTransferGB, 1) + ' GB', 'success');
    }
  };

  // --- DTN ENGINE ---
  const dtnEngine = {
    runLTP() {
      const payload = parseInt($('ltp-payload').value);
      const mtu = parseInt($('ltp-mtu').value);
      const loss = parseInt($('ltp-loss').value) / 100;
      const result = LTP.simulateTransfer(payload, mtu, loss);
      const el = $('ltp-result');
      const content = $('ltp-result-content');
      el.style.display = 'block';
      const statusColor = result.retransmitted === 0 ? 'var(--success)' : result.retransmitted < 5 ? 'var(--accent)' : 'var(--mars)';
      content.innerHTML = `
        <div class="result-grid">
          <div class="result-item"><span class="result-label">Total Segments</span><span class="result-value">${result.segments}</span></div>
          <div class="result-item"><span class="result-label">Segments Sent</span><span class="result-value">${result.sent}</span></div>
          <div class="result-item"><span class="result-label">Segments Lost</span><span class="result-value" style="color:${result.lost > 0 ? 'var(--mars)' : 'var(--success)'}">${result.lost}</span></div>
          <div class="result-item"><span class="result-label">Retransmissions</span><span class="result-value" style="color:${statusColor}">${result.retransmitted}</span></div>
          <div class="result-item"><span class="result-label">Transfer Efficiency</span><span class="result-value">${result.efficiency}%</span></div>
          <div class="result-item"><span class="result-label">Red/Gnd Model</span><span class="result-value">Full RED (reliable)</span></div>
        </div>
        <div style="margin-top:14px;font-size:0.85rem;color:var(--text-secondary)">
          LTP segments payload into ${mtu}-byte blocks. Checkpoint at offset 0 enables report-based retransmission.
          Loss rate ${Math.round(loss * 100)}% resulted in ${result.retransmitted} retransmissions.
        </div>`;
      $('ltp-charts').style.display = 'block';
      destroyChart('ltpChart');
      destroyChart('ltpEffChart');
      charts.ltpChart = new Chart($('ltpChart').getContext('2d'), {
        type: 'bar',
        data: { labels: ['Original', 'Sent (incl. retrans)', 'Lost', 'Retransmitted', 'Received'],
          datasets: [{ label: 'Segments', data: [result.segments, result.sent, result.lost, result.retransmitted, result.segments],
            backgroundColor: ['rgba(0,212,255,0.7)', 'rgba(0,184,148,0.7)', 'rgba(255,107,53,0.7)', 'rgba(255,80,120,0.7)', 'rgba(63,185,80,0.7)'],
            borderColor: ['#00d4ff', '#00b894', '#ff6b35', '#ff5078', '#3fb950'], borderWidth: 1 }] },
        options: { ...chartTheme, plugins: { ...chartTheme.plugins, legend: { display: false } } }
      });
      charts.ltpEffChart = new Chart($('ltpEffChart').getContext('2d'), {
        type: 'doughnut',
        data: { labels: ['Useful Data', 'Overhead (Retrans)'],
          datasets: [{ data: [parseFloat(result.efficiency), Math.max(0, 100 - parseFloat(result.efficiency))],
            backgroundColor: ['rgba(0,212,170,0.8)', 'rgba(255,107,53,0.6)'], borderColor: ['#00d4aa', '#ff6b35'], borderWidth: 2 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { color: '#8892aa', font: { size: 11 }, padding: 12, usePointStyle: true } } } }
      });
    },
    loadPolicies() {
      const grid = $('policy-grid');
      if (!grid) return;
      grid.innerHTML = Policy.POLICIES.map(p => `
        <div class="card">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <span style="font-weight:600;color:var(--accent)">${p.id}</span>
            <span class="badge ${p.action === 'forward' ? 'badge success' : p.action === 'drop' ? 'badge mars' : 'badge nebula'}" style="font-size:0.7rem;padding:2px 8px">${p.action.toUpperCase()}</span>
          </div>
          <div style="font-weight:600;margin-bottom:4px">${p.name}</div>
          <div style="font-size:0.8rem;color:var(--text-secondary)">IF ${p.condition} \u2192 ${p.action} to ${p.target}</div>
        </div>`).join('');
    },
    evaluatePolicy() {
      const priority = parseInt($('pol-priority').value);
      const buffer = parseInt($('pol-buffer').value);
      const quality = parseInt($('pol-quality').value) / 100;
      const result = Policy.evaluate({ priority, buffer, linkQuality: quality, destTier: 1, currentTier: 4 });
      const el = $('pol-result');
      const color = result.action === 'forward' ? 'var(--success)' : result.action === 'drop' ? 'var(--mars)' : 'var(--nebula)';
      el.innerHTML = `<div style="padding:12px;background:rgba(255,255,255,0.03);border-radius:8px;border-left:3px solid ${color}">
        <div style="font-weight:600;color:${color};text-transform:uppercase">${result.action}</div>
        <div style="font-size:0.85rem;color:var(--text-secondary);margin-top:4px">Target: ${result.target}${result.matched ? ' \u2014 matched by ' + result.matched.id + ' (' + result.matched.name + ')' : ' \u2014 no policy matched (default)'}</div>
      </div>`;
    }
  };

  // --- RF BUDGET ---
  const rfBudget = {
    calculate() {
      const band = $('rf-band').value;
      const freq = RFBudget.BANDS[band];
      const distance = parseFloat($('rf-distance').value) * 1e6;
      const txPower = parseFloat($('rf-tx-power').value);
      const txDish = parseFloat($('rf-tx-dish').value);
      const rxDish = parseFloat($('rf-rx-dish').value);
      const dataRate = parseFloat($('rf-rate').value);
      const r = RFBudget.calculate({
        frequency_hz: freq, distance_km: distance,
        tx_power_watts: txPower, tx_diameter_m: txDish, rx_diameter_m: rxDish,
        data_rate_bps: dataRate, bandwidth_hz: dataRate * 2
      });
      const el = $('rf-result');
      const content = $('rf-result-content');
      el.style.display = 'block';
      const mColor = r.margin_db > 3 ? 'var(--success)' : r.margin_db > 0 ? 'var(--accent)' : 'var(--mars)';
      content.innerHTML = `
        <div class="result-grid">
          <div class="result-item"><span class="result-label">Band</span><span class="result-value">${band}</span></div>
          <div class="result-item"><span class="result-label">Frequency</span><span class="result-value">${(freq / 1e9).toFixed(1)} GHz</span></div>
          <div class="result-item"><span class="result-label">FSPL</span><span class="result-value">${r.fspl_db.toFixed(1)} dB</span></div>
          <div class="result-item"><span class="result-label">EIRP</span><span class="result-value">${r.eirp_dbm.toFixed(1)} dBm</span></div>
          <div class="result-item"><span class="result-label">Rx Power</span><span class="result-value">${r.rx_power_dbm.toFixed(1)} dBm</span></div>
          <div class="result-item"><span class="result-label">System Temp</span><span class="result-value">${r.tSys_k.toFixed(0)} K</span></div>
          <div class="result-item"><span class="result-label">Eb/N0</span><span class="result-value">${r.eb_n0_db.toFixed(1)} dB</span></div>
          <div class="result-item"><span class="result-label">Link Margin</span><span class="result-value" style="color:${mColor}">${r.margin_db > 0 ? '+' : ''}${r.margin_db.toFixed(1)} dB</span></div>
        </div>
        <div style="margin-top:14px;font-size:0.85rem;color:var(--text-secondary)">
          ${r.margin_db > 3 ? '\u2713 Link CLOSED with comfortable margin.' : r.margin_db > 0 ? '\u26A0 Link marginally closed \u2014 consider lower data rate.' : '\u2717 Link NOT closed \u2014 insufficient margin. Reduce data rate or increase power/aperture.'}
        </div>`;
      $('rf-charts').style.display = 'block';
      destroyChart('rfChart');
      destroyChart('rfMarginChart');
      charts.rfChart = new Chart($('rfChart').getContext('2d'), {
        type: 'bar',
        data: { labels: ['Tx Power', 'Tx Gain', 'FSPL', 'Rx Gain', 'Rx Power', 'Eb/N0', 'Margin'],
          datasets: [{
            label: 'dB / dBm',
            data: [10 * Math.log10(txPower * 1000), r.eirp_dbm - 10 * Math.log10(txPower * 1000), -r.fspl_db,
              r.rx_power_dbm - r.eirp_dbm + r.fspl_db, r.rx_power_dbm, r.eb_n0_db, r.margin_db],
            backgroundColor: ['rgba(0,212,255,0.7)', 'rgba(0,184,148,0.7)', 'rgba(255,107,53,0.7)',
              'rgba(0,184,148,0.7)', 'rgba(0,212,255,0.7)', 'rgba(124,92,247,0.7)',
              r.margin_db > 3 ? 'rgba(63,185,80,0.7)' : r.margin_db > 0 ? 'rgba(210,153,34,0.7)' : 'rgba(255,80,120,0.7)'],
            borderColor: ['#00d4ff', '#00b894', '#ff6b35', '#00b894', '#00d4ff', '#7c5cf7',
              r.margin_db > 3 ? '#3fb950' : r.margin_db > 0 ? '#d29922' : '#ff5078'], borderWidth: 1
          }] },
        options: { ...chartTheme, plugins: { ...chartTheme.plugins, legend: { display: false } },
          scales: { ...chartTheme.scales, y: { ...chartTheme.scales.y, title: { display: true, text: 'dB', color: '#4a5270' } } } }
      });
      charts.rfMarginChart = new Chart($('rfMarginChart').getContext('2d'), {
        type: 'doughnut',
        data: { labels: ['Required Eb/N0', 'Margin'],
          datasets: [{ data: [Math.max(0, r.eb_n0_db - r.margin_db), Math.max(0, r.margin_db)],
            backgroundColor: ['rgba(124,92,247,0.7)', r.margin_db > 3 ? 'rgba(63,185,80,0.8)' : r.margin_db > 0 ? 'rgba(210,153,34,0.8)' : 'rgba(255,80,120,0.8)'],
            borderColor: ['#7c5cf7', r.margin_db > 3 ? '#3fb950' : r.margin_db > 0 ? '#d29922' : '#ff5078'], borderWidth: 2 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { color: '#8892aa', font: { size: 11 }, padding: 12, usePointStyle: true } } } }
      });
    }
  };

  // --- SIMULATION ---
  const simulation = {
    run() {
      const config = {
        duration_hours: parseFloat($('sim-duration').value),
        step_seconds: parseFloat($('sim-step').value),
        bundle_rate: parseFloat($('sim-rate').value),
        seed: parseInt($('sim-seed').value)
      };
      const result = Simulation.run(config);
      $('sim-results').style.display = 'block';
      $('sim-stats').innerHTML = [
        { label: 'Total Bundles', value: result.total, color: 'var(--accent)' },
        { label: 'Delivered', value: result.delivered, color: 'var(--success)' },
        { label: 'Dropped', value: result.dropped, color: 'var(--mars)' },
        { label: 'Delivery Ratio', value: (result.deliveryRatio * 100).toFixed(1) + '%', color: result.deliveryRatio > 0.7 ? 'var(--success)' : 'var(--accent)' }
      ].map(s => `<div class="card stat-card"><div class="metric-value" style="color:${s.color}">${s.value}</div><div class="metric-label">${s.label}</div></div>`).join('');
      $('sim-details').innerHTML = `
        <div class="result-grid">
          <div class="result-item"><span class="result-label">Simulation Steps</span><span class="result-value">${result.steps}</span></div>
          <div class="result-item"><span class="result-label">Stored (deferred)</span><span class="result-value">${result.stored}</span></div>
          <div class="result-item"><span class="result-label">Avg Delay</span><span class="result-value">${result.avgDelayMinutes.toFixed(1)} min</span></div>
          <div class="result-item"><span class="result-label">Avg Hops</span><span class="result-value">${result.avgHops.toFixed(1)}</span></div>
        </div>`;
      destroyChart('simChart');
      destroyChart('simPriorityChart');
      charts.simChart = new Chart($('simChart').getContext('2d'), {
        type: 'line',
        data: { labels: result.timeline.map(t => t.hour + 'h'),
          datasets: [
            { label: 'Delivery Ratio', data: result.timeline.map(t => (t.deliveryRatio * 100).toFixed(1)),
              borderColor: '#00d4ff', tension: 0.4, pointRadius: 1, borderWidth: 2, fill: true,
              backgroundColor: 'rgba(0,212,255,0.08)' },
            { label: 'Delivered', data: result.timeline.map(t => t.delivered),
              borderColor: '#3fb950', tension: 0.4, pointRadius: 0, borderWidth: 1.5 },
            { label: 'Dropped', data: result.timeline.map(t => t.dropped),
              borderColor: '#ff6b35', tension: 0.4, pointRadius: 0, borderWidth: 1.5 }
          ] },
        options: { ...chartTheme, scales: { ...chartTheme.scales,
          x: { ...chartTheme.scales.x, title: { display: true, text: 'Time (hours)', color: '#4a5270' } },
          y: { ...chartTheme.scales.y, title: { display: true, text: 'Count / %', color: '#4a5270' } } } }
      });
      charts.simPriorityChart = new Chart($('simPriorityChart').getContext('2d'), {
        type: 'bar',
        data: { labels: result.priorityNames,
          datasets: [
            { label: 'Generated', data: result.priorityCounts, backgroundColor: 'rgba(0,212,255,0.5)', borderColor: '#00d4ff', borderWidth: 1 },
            { label: 'Delivered', data: result.priorityDelivered, backgroundColor: 'rgba(63,185,80,0.6)', borderColor: '#3fb950', borderWidth: 1 }
          ] },
        options: { ...chartTheme, scales: { ...chartTheme.scales,
          x: { ...chartTheme.scales.x }, y: { ...chartTheme.scales.y, title: { display: true, text: 'Bundles', color: '#4a5270' } } } }
      });
    }
  };

  // --- STUDY RESOURCES ---
  const study = {
    learningObjectives: [
      {
        id: 'dtn',
        title: 'LO1: Delay-Tolerant Networking',
        color: '#00d4ff',
        icon: '&#9672;',
        summary: 'Bundle Protocol v7, store-and-forward, custody transfer, convergence layers, RFC 9171, CCSDS 735.1-B-1',
        resources: [
          { type: 'RFC', title: 'RFC 9171 \u2014 Bundle Protocol Version 7', url: 'https://www.rfc-editor.org/rfc/rfc9171', badge: 'MUST READ' },
          { type: 'RFC', title: 'RFC 4838 \u2014 DTN Architecture', url: 'https://www.rfc-editor.org/rfc/rfc4838', badge: 'ESSENTIAL' },
          { type: 'RFC', title: 'RFC 5326 \u2014 Licklider Transmission Protocol', url: 'https://www.rfc-editor.org/rfc/rfc5326', badge: 'IMPORTANT' },
          { type: 'Standard', title: 'CCSDS 734.2-B-1 \u2014 DTN Architecture (Blue Book)', url: 'https://public.ccsds.org/Pubs/734x2b1.pdf', badge: 'CCSDS' },
          { type: 'Standard', title: 'CCSDS 735.1-B-1 \u2014 Bundle Protocol (Blue Book)', url: 'https://public.ccsds.org/Pubs/735x1b1.pdf', badge: 'CCSDS' },
          { type: 'Paper', title: 'Burleigh et al. \u2014 "DTN: An Approach to Interplanetary Internet" (2003)', url: 'https://doi.org/10.1109/MCOM.2003.1204759', badge: 'FOUNDATIONAL' },
          { type: 'Paper', title: 'Fall \u2014 "A Delay-Tolerant Network Architecture" (2003)', url: 'https://dl.acm.org/doi/10.1145/863955.863960', badge: 'FOUNDATIONAL' },
          { type: 'Video', title: 'NASA DTN Overview', url: 'https://www.youtube.com/results?search_query=nasa+delay+tolerant+networking', badge: 'YOUTUBE' },
          { type: 'Software', title: 'ION-DTN \u2014 Reference BPv7 Implementation', url: 'https://sourceforge.net/projects/ion-dtn/', badge: 'HANDS-ON' }
        ]
      },
      {
        id: 'quantum',
        title: 'LO2: Quantum Communication',
        color: '#7c5cf7',
        icon: '&#10023;',
        summary: 'BB84, E91, QKD, quantum repeaters, entanglement, post-quantum cryptography, QBER threshold',
        resources: [
          { type: 'Paper', title: 'Bennett & Brassard \u2014 "Quantum Cryptography" (1984)', url: 'https://www.researchgate.net/publication/215639057', badge: 'MUST READ' },
          { type: 'Paper', title: 'Ekert \u2014 "Quantum Cryptography Based on Bell\'s Theorem" (1991)', url: 'https://doi.org/10.1103/PhysRevLett.67.661', badge: 'MUST READ' },
          { type: 'Paper', title: 'Liao et al. \u2014 "Satellite-to-Ground QKD" \u2014 Nature (2017)', url: 'https://doi.org/10.1038/nature23655', badge: 'HIGH' },
          { type: 'Paper', title: 'Bedington et al. \u2014 "Progress in Satellite QKD" (2017)', url: 'https://doi.org/10.1038/s41534-017-0031-5', badge: 'HIGH' },
          { type: 'Standard', title: 'NIST FIPS 203 \u2014 ML-KEM (CRYSTALS-Kyber)', url: 'https://csrc.nist.gov/pubs/fips/203/final', badge: 'NIST' },
          { type: 'Standard', title: 'NIST FIPS 204 \u2014 ML-DSA (CRYSTALS-Dilithium)', url: 'https://csrc.nist.gov/pubs/fips/204/final', badge: 'NIST' },
          { type: 'Standard', title: 'ETSI QKD Standards Series', url: 'https://www.etsi.org/committee/1434-quantum-key-distribution', badge: 'ETSI' },
          { type: 'Video', title: 'PBS Space Time \u2014 "Quantum Key Distribution"', url: 'https://www.youtube.com/watch?v=UIwKjGrjXfg', badge: 'YOUTUBE' },
          { type: 'Course', title: 'TU Delft \u2014 "Quantum Internet & Quantum Computers" (edX)', url: 'https://www.edx.org/course/quantum-internet-and-quantum-computers-how-will-they-change-the-world', badge: 'FREE COURSE' },
          { type: 'Tool', title: 'IBM Quantum \u2014 Free Quantum Computer Access', url: 'https://quantum.ibm.com/', badge: 'HANDS-ON' }
        ]
      },
      {
        id: 'space',
        title: 'LO3: Space-Based Infrastructure',
        color: '#ff6b35',
        icon: '&#9883;',
        summary: '5-tier topology, DSN, Lagrange points, areostationary orbit, optical/RF hybrid, solar conjunction',
        resources: [
          { type: 'Doc', title: 'NASA Deep Space Network (DSN) \u2014 Official Site', url: 'https://deepspace.jpl.nasa.gov/', badge: 'OFFICIAL' },
          { type: 'Doc', title: 'DSN Telecommunications Link Design Handbook (810-005)', url: 'https://deepspace.jpl.nasa.gov/dsndocs/810-005/', badge: 'DSN BIBLE' },
          { type: 'Standard', title: 'CCSDS 141.0-B-1 \u2014 Optical Communications Physical Layer', url: 'https://public.ccsds.org/Pubs/141x0b1.pdf', badge: 'CCSDS' },
          { type: 'Standard', title: 'CCSDS 142.0-B-2 \u2014 Space Link Identification (LNIS v5)', url: 'https://public.ccsds.org/Pubs/142x0b2.pdf', badge: 'CCSDS' },
          { type: 'Paper', title: 'Boroson et al. \u2014 "LLCD Overview and Results" (2014)', url: 'https://doi.org/10.1117/12.2045508', badge: 'HIGH' },
          { type: 'Paper', title: 'Biswas et al. \u2014 "DSOC" (2018)', url: 'https://doi.org/10.1117/12.2296426', badge: 'HIGH' },
          { type: 'Video', title: 'PBS Space Time \u2014 "Lagrange Points Explained"', url: 'https://www.youtube.com/watch?v=mxpVbU5FH0s', badge: 'YOUTUBE' },
          { type: 'Video', title: 'NASA \u2014 Deep Space Optical Communications (DSOC)', url: 'https://www.youtube.com/results?search_query=deep+space+optical+communications+NASA', badge: 'YOUTUBE' }
        ]
      },
      {
        id: 'orbital',
        title: 'LO4: Orbital Mechanics',
        color: '#00d4aa',
        icon: '&#9788;',
        summary: 'Keplerian elements, synodic period, contact windows, Doppler shift, JPL Horizons, light-time calculation',
        resources: [
          { type: 'Tool', title: 'JPL Horizons \u2014 Precise Ephemeris System', url: 'https://ssd.jpl.nasa.gov/horizons/app.html', badge: 'MUST USE' },
          { type: 'Tool', title: 'NASA Eyes on the Solar System \u2014 3D Visualization', url: 'https://eyes.nasa.gov/', badge: 'INTERACTIVE' },
          { type: 'Tool', title: 'GMAT \u2014 NASA General Mission Analysis Tool (Free)', url: 'https://software.nasa.gov/software/GSFC-54099', badge: 'SOFTWARE' },
          { type: 'Book', title: 'Vallado \u2014 "Fundamentals of Astrodynamics" (2013)', url: 'https://www.amazon.com/Fundamentals-Astrodynamics-Applications-David-Vallado/dp/1881883183', badge: 'TEXTBOOK' },
          { type: 'Video', title: 'CrashCourse \u2014 "Orbital Mechanics" Full Course', url: 'https://www.youtube.com/watch?v=J1lRLElluEQ', badge: 'YOUTUBE' },
          { type: 'Video', title: 'ScienceClic \u2014 "Hohmann Transfer Orbits"', url: 'https://www.youtube.com/watch?v=GsXppO8pI-8', badge: 'YOUTUBE' },
          { type: 'Course', title: 'CU Boulder \u2014 Spacecraft Dynamics (Coursera)', url: 'https://www.coursera.org/learn/spacecraft-dynamics-kinetics', badge: 'FREE AUDIT' }
        ]
      },
      {
        id: 'radiation',
        title: 'LO5: Radiation-Hardened Computing',
        color: '#f85149',
        icon: '&#9888;',
        summary: 'Single-event upsets, error correction (Hamming, Reed-Solomon, LDPC), TMR, CCSDS channel coding',
        resources: [
          { type: 'Standard', title: 'CCSDS 131.0-B-4 \u2014 TM Synchronization and Channel Coding', url: 'https://public.ccsds.org/Pubs/131x0b4e2.pdf', badge: 'CCSDS' },
          { type: 'Video', title: '3Blue1Brown \u2014 "Hamming Codes Explained"', url: 'https://www.youtube.com/watch?v=X8jsijhllOU', badge: 'YOUTUBE' },
          { type: 'Video', title: 'Radiation Effects on Electronics in Space', url: 'https://www.youtube.com/results?search_query=radiation+effects+electronics+space', badge: 'YOUTUBE' },
          { type: 'Doc', title: 'NASA Radiation Effects Analysis', url: 'https://radhome.gsfc.nasa.gov/', badge: 'NASA' }
        ]
      },
      {
        id: 'priority',
        title: 'LO6: Data Prioritization & RL Routing',
        color: '#d29922',
        icon: '&#10070;',
        summary: 'BPv7 priority classes (P0-P4), Q-learning, DQN, reward functions, multi-agent RL, federated learning',
        resources: [
          { type: 'Book', title: 'Sutton & Barto \u2014 "Reinforcement Learning: An Introduction" (FREE)', url: 'http://incompleteideas.net/book/the-book.html', badge: 'FREE BOOK' },
          { type: 'Course', title: 'David Silver (UCL) \u2014 RL Course (10 Lectures, Free)', url: 'https://www.davidsilver.uk/teaching/', badge: 'FREE COURSE' },
          { type: 'Course', title: 'UC Berkeley CS 285 \u2014 Deep RL (Free Lectures)', url: 'https://rail.eecs.berkeley.edu/deeprlcourse/', badge: 'FREE COURSE' },
          { type: 'Paper', title: 'Mnih et al. \u2014 "Human-Level Control Through Deep RL" (2015)', url: 'https://doi.org/10.1038/nature14236', badge: 'DQN' },
          { type: 'Tool', title: 'OpenAI Spinning Up \u2014 Educational RL Implementations', url: 'https://spinningup.openai.com/', badge: 'HANDS-ON' },
          { type: 'Video', title: 'ML with Phil \u2014 "Q-Learning Explained"', url: 'https://www.youtube.com/watch?v=qhRNvCVVJaA', badge: 'YOUTUBE' }
        ]
      }
    ],

    courses: [
      { title: 'Quantum Internet & Quantum Computers', provider: 'TU Delft (edX)', cert: true, url: 'https://www.edx.org/course/quantum-internet-and-quantum-computers-how-will-they-change-the-world' },
      { title: 'David Silver \u2014 Reinforcement Learning', provider: 'UCL', cert: false, url: 'https://www.davidsilver.uk/teaching/' },
      { title: 'CS 285 \u2014 Deep Reinforcement Learning', provider: 'UC Berkeley', cert: false, url: 'https://rail.eecs.berkeley.edu/deeprlcourse/' },
      { title: 'Spacecraft Dynamics & Control', provider: 'CU Boulder (Coursera)', cert: false, url: 'https://www.coursera.org/learn/spacecraft-dynamics-kinetics' },
      { title: 'Cisco Networking Essentials', provider: 'Cisco Networking Academy', cert: true, url: 'https://www.netacad.com/' },
      { title: 'IBM Quantum Learning', provider: 'IBM', cert: true, url: 'https://learning.quantum.ibm.com/' },
      { title: 'Scientific Computing with Python', provider: 'freeCodeCamp', cert: true, url: 'https://www.freecodecamp.org/' }
    ],

    tools: [
      { name: 'JPL Horizons', purpose: 'Precise ephemeris for any solar system body', url: 'https://ssd.jpl.nasa.gov/horizons/app.html' },
      { name: 'ION-DTN', purpose: 'Reference BPv7 implementation', url: 'https://sourceforge.net/projects/ion-dtn/' },
      { name: 'IBM Quantum', purpose: 'Free access to real quantum computers', url: 'https://quantum.ibm.com/' },
      { name: 'NASA GMAT', purpose: 'General Mission Analysis Tool', url: 'https://software.nasa.gov/software/GSFC-54099' },
      { name: 'Gymnasium', purpose: 'RL environments (successor to OpenAI Gym)', url: 'https://gymnasium.farama.org/' },
      { name: 'Qiskit', purpose: 'IBM quantum SDK with QKD tutorials', url: 'https://qiskit.org/' },
      { name: 'Astropy / Skyfield', purpose: 'Python astronomy & ephemeris libraries', url: 'https://www.astropy.org/' },
      { name: 'NASA Eyes', purpose: '3D solar system visualization', url: 'https://eyes.nasa.gov/' }
    ],

    keyReferences: [
      '[1] K. Fall, "A Delay-Tolerant Network Architecture for Challenged Internets," ACM SIGCOMM, 2003.',
      '[2] S. Burleigh et al., "Delay-Tolerant Networking: An Approach to Interplanetary Internet," IEEE Comm. Mag., 2003.',
      '[3] S. Burleigh, K. Fall, "Bundle Protocol Version 7," RFC 9171, Jan. 2022.',
      '[4] C.H. Bennett, G. Brassard, "Quantum Cryptography: Public Key Distribution and Coin Tossing," 1984.',
      '[5] A.K. Ekert, "Quantum Cryptography Based on Bell\'s Theorem," Phys. Rev. Lett., 1991.',
      '[6] S.-K. Liao et al., "Satellite-to-Ground QKD," Nature, 2017.',
      '[7] D.M. Boroson et al., "Overview and Results of LLCD," Proc. SPIE, 2014.',
      '[8] A. Biswas et al., "Deep Space Optical Communications (DSOC)," Proc. SPIE, 2018.',
      '[9] V. Mnih et al., "Human-Level Control Through Deep RL," Nature, 2015.',
      '[10] D.A. Vallado, Fundamentals of Astrodynamics and Applications, 4th ed., 2013.'
    ],

    init() {
      this.renderLOGrid();
      this.renderCourses();
      this.renderTools();
      this.renderRefs();
      this.renderDashboardStats();
    },

    renderLOGrid() {
      const container = $('study-lo-grid');
      if (!container) return;
      container.innerHTML = this.learningObjectives.map(lo => {
        const badgeColors = {
          'MUST READ': '#f85149', 'ESSENTIAL': '#f85149', 'FOUNDATIONAL': '#f85149', 'HIGH': '#ff6b35',
          'IMPORTANT': '#00d4ff', 'CCSDS': '#00d4ff', 'NIST': '#3fb950', 'ETSI': '#3fb950',
          'YOUTUBE': '#f85149', 'FREE COURSE': '#7c5cf7', 'FREE BOOK': '#7c5cf7', 'FREE AUDIT': '#7c5cf7',
          'OFFICIAL': '#00d4aa', 'DSN BIBLE': '#00d4aa', 'MUST USE': '#3fb950', 'INTERACTIVE': '#00d4ff',
          'SOFTWARE': '#d29922', 'HANDS-ON': '#d29922', 'TEXTBOOK': '#d29922', 'DQN': '#7c5cf7', 'NASA': '#00d4aa'
        };
        return '<div class="card"><div class="card-title" style="border-color:' + lo.color + '"><span class="ct-dot" style="background:' + lo.color + '"></span> ' + lo.title + '</div>' +
          '<p style="color:var(--text-secondary);font-size:0.85rem;margin-bottom:14px;line-height:1.5">' + lo.summary + '</p>' +
          '<div class="study-resource-list">' + lo.resources.map(r => {
            const bc = badgeColors[r.badge] || '#00d4ff';
            return '<a href="' + r.url + '" target="_blank" rel="noopener" class="study-resource-item">' +
              '<span class="study-resource-badge" style="background:' + bc + '22;color:' + bc + ';border-color:' + bc + '33">' + r.badge + '</span>' +
              '<span class="study-resource-type">' + r.type + '</span>' +
              '<span class="study-resource-title">' + r.title + '</span>' +
              '<span class="study-resource-arrow">&#8599;</span></a>';
          }).join('') + '</div></div>';
      }).join('');
    },

    renderCourses() {
      const el = $('study-courses-content');
      if (!el) return;
      el.innerHTML = '<div class="table-wrapper"><table class="pres-table"><thead><tr><th>Course</th><th>Provider</th><th>Free Certificate</th></tr></thead><tbody>' +
        this.courses.map(c => '<tr><td><a href="' + c.url + '" target="_blank" rel="noopener" style="color:var(--accent)">' + c.title + '</a></td><td>' + c.provider + '</td><td>' + (c.cert ? '<span class="badge success">Yes</span>' : '<span class="badge" style="background:rgba(138,146,170,0.15)">Free Audit</span>') + '</td></tr>').join('') +
        '</tbody></table></div>';
    },

    renderTools() {
      const el = $('study-tools-content');
      if (!el) return;
      el.innerHTML = '<div class="study-tools-grid">' +
        this.tools.map(t => '<a href="' + t.url + '" target="_blank" rel="noopener" class="study-tool-card"><div class="study-tool-name">' + t.name + '</div><div class="study-tool-purpose">' + t.purpose + '</div></a>').join('') +
        '</div>';
    },

    renderRefs() {
      const el = $('study-refs-content');
      if (!el) return;
      el.innerHTML = '<div class="study-refs-list">' + this.keyReferences.map(r => '<div class="study-ref-item">' + r + '</div>').join('') + '</div>' +
        '<div style="margin-top:16px;text-align:center"><a href="https://github.com/matx104/AETHERIX/blob/main/references/REFERENCES.md" target="_blank" class="btn btn-sm" style="border-color:var(--accent);color:var(--accent)">View all 64 references in REFERENCES.md &#8599;</a></div>';
    },

    renderDashboardStats() {
      const el = $('dashboard-study-stats');
      if (!el) return;
      const stats = [
        { value: '241', label: 'Network Nodes', color: 'var(--nebula)', sub: '5-tier topology' },
        { value: '149', label: 'Unit Tests', color: '#00d4aa', sub: '10 test modules' },
        { value: '64+', label: 'Academic References', color: 'var(--accent)', sub: 'IEEE format' },
        { value: '7', label: 'CCSDS/IETF Standards', color: 'var(--success)', sub: 'Blue Books & RFCs' },
        { value: '7+', label: 'Free Courses', color: 'var(--quantum)', sub: 'edX, Coursera, UCL' },
        { value: '6', label: 'Learning Objectives', color: 'var(--mars)', sub: 'Comprehensive coverage' }
      ];
      el.innerHTML = stats.map((s, i) =>
        '<div class="card stat-card animate-in stagger-' + (i + 1) + '" style="cursor:pointer" onclick="window.location.hash=\'#study\'">' +
        '<div class="card-value" style="color:' + s.color + '">' + s.value + '</div>' +
        '<div class="card-title">' + s.label + '</div>' +
        '<div style="font-size:0.7rem;color:var(--text-muted);margin-top:4px">' + s.sub + '</div></div>'
      ).join('');
    }
  };

  // --- PRESENTATION ---
  const presentation = {
    currentSlide: 0,
    timerSeconds: 0,
    timerInterval: null,
    timerVisible: true,
    notesVisible: false,
    shortcutsVisible: false,
    initialized: false,

    slides: [],

    init() {
      if (this.initialized) { this.render(); return; }
      this.slides = this.buildSlides();
      this.initialized = true;
      this.bindEvents();
      const hashSlide = window.location.hash.match(/presentation\/(\d+)/);
      this.currentSlide = hashSlide ? Math.min(parseInt(hashSlide[1]) - 1, this.slides.length - 1) : 0;
      this.render();
      this.startTimer();
    },

    mermaidDiagrams: {
      'system-architecture': 'graph TB\n'
        + '  subgraph SRC[Python Source]\n'
        + '    INFRA[Infrastructure - link_budget + rf_link_budget]\n'
        + '    ROUTE[Routing - rl_agent + bundle + ltp + tcpcl]\n'
        + '    SEC[Security - qkd + repeater_chain]\n'
        + '    ORBIT[Orbital - contact_windows + topology + doppler]\n'
        + '  end\n'
        + '  subgraph ENGINE[Simulation Engine]\n'
        + '    SIM[simulator]\n'
        + '    POLICY[policy_engine]\n'
        + '    TRAIN[training + multi_agent]\n'
        + '    FWD[forwarding_engine]\n'
        + '  end\n'
        + '  subgraph WEB[Web Showcase - 10 Demos]\n'
        + '    DASH[Mission Control]\n'
        + '    LB[Link Budget]\n'
        + '    RL[RL Routing]\n'
        + '    QKD[QKD Protocol]\n'
        + '    ORB[Orbital Mechanics]\n'
        + '    DTN[DTN Engine]\n'
        + '    MISS[Mars Mission]\n'
        + '  end\n'
        + '  INFRA --> SIM\n'
        + '  ROUTE --> SIM\n'
        + '  SEC --> SIM\n'
        + '  ORBIT --> SIM\n'
        + '  SIM --> POLICY\n'
        + '  SIM --> TRAIN\n'
        + '  SIM --> FWD\n'
        + '  POLICY --> DASH\n'
        + '  FWD --> DTN\n'
        + '  ROUTE --> RL\n'
        + '  SEC --> QKD\n'
        + '  ORBIT --> ORB\n'
        + '  INFRA --> LB\n'
        + '  SIM --> MISS',
      'network-topology': 'graph LR\n'
        + '  subgraph EARTH[EARTH]\n'
        + '    T1[T1 Earth Ground - 6 Nodes]\n'
        + '    T2[T2 Earth Orbital - 51 Nodes]\n'
        + '  end\n'
        + '  subgraph DEEP[DEEP SPACE]\n'
        + '    T3[T3 Transit - 4 Nodes]\n'
        + '  end\n'
        + '  subgraph MARS[MARS]\n'
        + '    T4[T4 Mars Orbital - 13 Nodes]\n'
        + '    T5[T5 Mars Surface - 167 Nodes]\n'
        + '  end\n'
        + '  T1 -->|100 Mbps| T2\n'
        + '  T2 -->|10 Gbps ISL| T3\n'
        + '  T3 -->|2 to 200 Mbps| T4\n'
        + '  T4 -->|2 Mbps UHF| T5\n'
        + '  T2 -.->|Redundant L5| T3\n'
        + '  T3 -.->|Direct optical| T4',
      'data-flow': 'graph TD\n'
        + '  subgraph APP[Application Layer]\n'
        + '    SRC[1 Source Node]\n'
        + '    BP[2 Bundle Protocol BPv7]\n'
        + '    RL[3 RL Routing]\n'
        + '    QE[4 QKD Encrypt]\n'
        + '  end\n'
        + '  subgraph CONV[Convergence Layer]\n'
        + '    LTP[5 LTP Segmentation]\n'
        + '    STORE[6 Store and Wait]\n'
        + '    FWD[7 Forward and Custody]\n'
        + '  end\n'
        + '  subgraph PHYS[Physical Layer]\n'
        + '    UHF[Mars UHF]\n'
        + '    ISL[Optical ISL]\n'
        + '    DEEP[Deep Space 1550nm]\n'
        + '    KAB[DSN Ka-band]\n'
        + '  end\n'
        + '  subgraph DELIV[Delivery]\n'
        + '    RASM[8 LTP Reassemble]\n'
        + '    DEC[9 QKD Decrypt]\n'
        + '    DEL[10 Delivered to JPL]\n'
        + '  end\n'
        + '  SRC --> BP --> RL --> QE\n'
        + '  QE --> LTP --> STORE --> FWD\n'
        + '  FWD --> UHF\n'
        + '  FWD --> ISL\n'
        + '  FWD --> DEEP\n'
        + '  FWD --> KAB\n'
        + '  UHF --> RASM\n'
        + '  ISL --> RASM\n'
        + '  DEEP --> RASM\n'
        + '  KAB --> RASM\n'
        + '  RASM --> DEC --> DEL'
    },

    buildSlides() {
      return [
        {
          title: 'Introduction',
          content: '<div class="pres-hero"><div style="display:flex;justify-content:center;margin-bottom:16px"><img src="img/logo.svg" alt="AETHERIX" style="width:100px;height:100px;filter:drop-shadow(0 0 20px rgba(0,212,255,0.3))"></div><div class="pres-hero-title" style="font-size:3.2rem;letter-spacing:8px">AETHERIX</div><div class="pres-hero-sub" style="max-width:820px">Autonomous Extraterrestrial High-throughput Enhancing Routing and Inter-planetary eXchange</div><div class="pres-divider"></div><div style="max-width:780px;margin:0 auto;text-align:left"><div style="background:rgba(var(--accent-rgb),0.06);border:1px solid rgba(var(--accent-rgb),0.2);border-radius:var(--radius-lg);padding:18px 22px;margin-bottom:20px"><div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--accent);margin-bottom:8px">EduQual Level 6 &mdash; Topic 59</div><div style="font-size:0.95rem;color:var(--text-primary);line-height:1.6">Building Interplanetary Communication Network with Delay-Tolerant Networking, Quantum Communication, and Space-Based Infrastructure for Mars Mission Support</div></div><div class="pres-grid-2" style="gap:12px"><div style="text-align:center;padding:14px;background:rgba(var(--quantum-rgb),0.06);border:1px solid rgba(var(--quantum-rgb),0.15);border-radius:var(--radius-md)"><div style="font-size:0.65rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Student</div><div style="font-size:0.9rem;color:var(--text-primary);font-weight:600">Muhammad Abdullah Tariq</div></div><div style="text-align:center;padding:14px;background:rgba(var(--quantum-rgb),0.06);border:1px solid rgba(var(--quantum-rgb),0.15);border-radius:var(--radius-md)"><div style="font-size:0.65rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Programme</div><div style="font-size:0.9rem;color:var(--text-primary);font-weight:600">Diploma in AI Operations</div></div></div><div style="display:flex;gap:10px;justify-content:center;margin-top:16px;flex-wrap:wrap"><a href="https://matx104.github.io/AETHERIX/" target="_blank" class="pres-link">Live Showcase</a><a href="https://github.com/matx104/AETHERIX" target="_blank" class="pres-link">Source Code</a><a href="https://www.linkedin.com/in/matx104" target="_blank" class="pres-link">LinkedIn</a><a href="https://matx104.com.pk" target="_blank" class="pres-link">Portfolio</a></div></div></div>',
          speakerNotes: 'State your name clearly. Read the topic number and title exactly as on the exam paper. Pause to let examiners see it. Point to the logo. This is your first impression. (30 seconds)'
        },
        {
          title: 'What is AETHERIX',
          content: '<h2><span class="pres-tag accent">Overview</span> What is AETHERIX &amp; Why Does It Matter?</h2><div class="pres-grid-2" style="margin-bottom:16px"><div class="pres-card"><div class="pres-card-title">What is AETHERIX?</div><ul class="pres-list"><li>A complete <strong style="color:#00d4ff">interplanetary networking platform</strong> for Earth-to-Mars communication</li><li>Uses <strong style="color:#7c5cf7">Delay-Tolerant Networking (DTN)</strong> &mdash; the postal service of space</li><li>Combines <strong style="color:#c84cff">quantum-secured links</strong>, <strong style="color:#ff6b35">AI-powered routing</strong>, and <strong style="color:#3fb950">hybrid optical/RF</strong> links</li><li>241-node, 5-tier network topology from Earth surface to Mars surface</li><li>Working proof-of-concept: 27 Python modules, 149 tests, 10 interactive browser demos</li></ul></div><div class="pres-card pres-card-danger"><div class="pres-card-title">The Problem We Are Solving</div><ul class="pres-list"><li><strong>TCP/IP breaks</strong> at interplanetary distances &mdash; 3 to 22 minute one-way delays</li><li>Current Mars communication: only <strong>0.5&ndash;6 Mbps</strong> with <strong>60&ndash;75% availability</strong></li><li><strong>Solar conjunction</strong> causes 2-week total communication blackout every 26 months</li><li>Static routing cannot adapt to dynamic space conditions</li><li>Classical encryption is vulnerable to future quantum computers</li></ul></div></div><div class="pres-callout pres-callout-accent">AETHERIX addresses every one of these challenges: DTN replaces TCP/IP, optical links deliver 10&ndash;100&times; more bandwidth, RL routing adapts in real-time, QKD provides quantum-proof security, and Lagrange relays maintain communication during conjunction.</div>',
          speakerNotes: 'This slide sets up the narrative arc. First explain what AETHERIX is in plain language - it\'s like the postal service for interplanetary space. Then pivot to the problem: TCP/IP was never designed for space. 22-minute delays break every assumption. Solar conjunction blackouts. Static routing. Vulnerable crypto. Each problem maps to one of our solutions. (1.5 minutes)'
        },
        {
          title: 'The Distance',
          content: '<h2><span class="pres-tag mars">The Problem</span> Why Space Breaks the Internet</h2><div class="pres-grid-2"><div class="pres-card pres-card-danger"><div class="pres-card-title">Earth &rarr; Mars</div><table class="pres-table"><tr><td><strong>Closest approach</strong></td><td>54.6 million km</td></tr><tr><td><strong>Farthest distance</strong></td><td>401 million km</td></tr><tr><td><strong>Distance range</strong></td><td>7&times; variation</td></tr><tr><td><strong>One-way light time</strong></td><td>3 &mdash; 22 minutes</td></tr><tr><td><strong>Solar conjunction</strong></td><td>2-week total blackout</td></tr></table></div><div class="pres-card pres-card-danger"><div class="pres-card-title">Why TCP/IP Fails</div><table class="pres-table"><tr><td><strong>TCP/IP expects</strong></td><td><strong>Space reality</strong></td></tr><tr><td>RTT &lt; 1 second</td><td>6 &mdash; 44 minute RTT</td></tr><tr><td>Always connected</td><td>Scheduled contacts only</td></tr><tr><td>End-to-end path</td><td>No persistent route</td></tr><tr><td>Reliable channel</td><td>High loss, radiation</td></tr></table></div></div><div class="pres-callout" style="margin-top:20px">&ldquo;Imagine waiting 44 minutes for a webpage to load. That\'s why we need a fundamentally different networking paradigm.&rdquo;</div>',
          speakerNotes: 'Start with the scale. 54.6M to 401M km. Light itself takes 3-22 minutes one way. TCP/IP was designed for sub-second round trips. In space, by the time a packet acknowledgment returns, the link may be gone. Solar conjunction causes 2-week blackout. This is why NASA calls it Delay-Tolerant Networking. (1.5 minutes)'
        },
        {
          title: 'The Answer',
          content: '<h2><span class="pres-tag accent">Solution</span> Delay-Tolerant Networking &mdash; The Postal Service of Space</h2><div class="pres-flow"><div class="pres-flow-step"><span class="pres-flow-step-icon">&#128230;</span><span class="pres-flow-step-text">Bundle</span></div><span class="pres-flow-arrow">&rarr;</span><div class="pres-flow-step"><span class="pres-flow-step-icon">&#128193;</span><span class="pres-flow-step-text">Store</span></div><span class="pres-flow-arrow">&rarr;</span><div class="pres-flow-step"><span class="pres-flow-step-icon">&#128257;</span><span class="pres-flow-step-text">Wait</span></div><span class="pres-flow-arrow">&rarr;</span><div class="pres-flow-step"><span class="pres-flow-step-icon">&#128640;</span><span class="pres-flow-step-text">Forward</span></div><span class="pres-flow-arrow">&rarr;</span><div class="pres-flow-step"><span class="pres-flow-step-icon">&#9989;</span><span class="pres-flow-step-text">Deliver</span></div></div><div class="pres-divider"></div><div class="pres-grid-3"><div class="pres-stat-card" style="border-color:rgba(0,212,255,0.2)"><div class="pres-stat-value" style="color:#00d4ff">BPv7</div><div class="pres-stat-unit">Bundle Protocol v7 (RFC 9171)</div></div><div class="pres-stat-card" style="border-color:rgba(124,92,247,0.2)"><div class="pres-stat-value" style="color:#7c5cf7">AI</div><div class="pres-stat-unit">Reinforcement Learning Routing</div></div><div class="pres-stat-card" style="border-color:rgba(200,76,255,0.2)"><div class="pres-stat-value" style="color:#c84cff">QKD</div><div class="pres-stat-unit">Quantum Key Distribution</div></div></div><div class="pres-callout pres-callout-accent" style="margin-top:20px">Like a postal service: you hand off your letter at each stop, and every post office takes responsibility for it &mdash; no end-to-end connection needed.</div>',
          speakerNotes: 'The key insight: instead of requiring an end-to-end connection like TCP, DTN works like the postal service. Each node takes custody of your data and forwards it when a link becomes available. Three pillars: BPv7 for the protocol, RL for intelligent routing, QKD for security. (1.5 minutes)'
        },
        {
          title: 'System Architecture',
          content: '<h2><span class="pres-tag accent">Architecture</span> System Component Overview</h2><div class="pres-grid-2" style="margin-bottom:16px"><div class="pres-card"><div class="pres-card-title">Five Core Modules</div><ul class="pres-list"><li><strong style="color:#00d4ff">Infrastructure</strong> &mdash; Optical + RF link budget calculators (FSPL, EIRP, margin). CCSDS 141.0-B-1.</li><li><strong style="color:#7c5cf7">Routing</strong> &mdash; Q-learning RL agent, BPv7 bundle protocol, LTP/TCPCL/UDP-CL. RFC 9171.</li><li><strong style="color:#c84cff">Security</strong> &mdash; BB84 &amp; E91 QKD, quantum repeater chains, CASCADE reconciliation. NIST FIPS 203/204.</li><li><strong style="color:#ff6b35">Orbital</strong> &mdash; Contact window prediction, 5-tier topology (241 nodes), Doppler compensation.</li><li><strong style="color:#3fb950">Simulation</strong> &mdash; Scenario engine, policy routing, RL training, multi-agent federated learning.</li></ul></div><div class="pres-card"><div class="pres-card-title">Module &rarr; Engine &rarr; Showcase</div><table class="pres-table"><tr><td><strong>Source</strong></td><td>27 Python modules across 5 packages</td></tr><tr><td><strong>Engine</strong></td><td>simulator + policy_engine + training + multi_agent + forwarding</td></tr><tr><td><strong>Showcase</strong></td><td>10 interactive browser demos (JS engine port)</td></tr><tr><td><strong>Tests</strong></td><td>149 unit tests across 10 test files</td></tr><tr><td><strong>Standards</strong></td><td>CCSDS 734.2/735.1/141.0/142.0 + RFC 9171/5326/7242</td></tr></table></div></div><div class="pres-mermaid-wrap" style="margin-bottom:16px"><div class="mermaid-diagram" data-diagram="system-architecture"></div></div>',
          speakerNotes: 'Show the architecture. Five core modules feed into the simulation engine, which feeds the web showcase. Standards compliance at the bottom. Point to each module as you explain. (1 minute)'
        },
        {
          title: 'BPv7 Deep Dive',
          content: '<h2><span class="pres-tag accent">Protocol</span> Bundle Protocol v7 &mdash; The Foundation</h2><div class="pres-card pres-card-glow" style="margin-bottom:20px"><div class="pres-card-title">Protocol Stack</div><div class="pres-stack"><div class="pres-stack-layer" style="background:rgba(0,212,255,0.08);border-color:rgba(0,212,255,0.2)">Application Layer &mdash; Science data, commands, telemetry</div><div class="pres-stack-layer" style="background:rgba(124,92,247,0.08);border-color:rgba(124,92,247,0.2)">Bundle Protocol v7 &mdash; Store-and-Forward &middot; Custody Transfer &middot; Priority P0-P4</div><div class="pres-stack-layer" style="background:rgba(255,107,53,0.08);border-color:rgba(255,107,53,0.2)">Convergence Layers &mdash; LTP (deep space) &middot; TCPCL (Earth) &middot; UDP-CL (optical ISL)</div><div class="pres-stack-layer" style="background:rgba(63,185,80,0.08);border-color:rgba(63,185,80,0.2)">Physical &mdash; Optical 1550nm / RF Ka/X/S-band</div></div></div><div class="pres-grid-2"><div class="pres-card"><div class="pres-card-title">How It Works</div><ol class="pres-list"><li>Source creates a <strong>bundle</strong> with destination, priority, lifetime</li><li>Bundle is forwarded to the next available hop</li><li>Each node <strong>stores</strong> the bundle during link outages</li><li><strong>Custody transfer</strong> shifts responsibility hop-by-hop</li><li>No end-to-end connection &mdash; ever</li></ol></div><div class="pres-card"><div class="pres-card-title">Standards Compliance</div><ul class="pres-list"><li><strong>CCSDS 734.2-B-1</strong> &mdash; DTN Architecture</li><li><strong>CCSDS 735.1-B-1</strong> &mdash; Bundle Protocol</li><li><strong>RFC 9171</strong> &mdash; BPv7 Specification</li><li><strong>RFC 5326</strong> &mdash; Licklider Transmission Protocol</li><li><strong>RFC 7242</strong> &mdash; TCP Convergence Layer</li></ul></div></div>',
          speakerNotes: 'BPv7 is the postal service protocol. Walk through the stack: Application at top, BPv7 as the store-and-forward layer, three convergence layers for different link types, physical at bottom. Custody transfer is the key innovation - each node takes legal responsibility. Priority P0 (emergency) to P4 (bulk). (2 minutes)'
        },
        {
          title: 'DTN Store-and-Forward',
          content: '<h2><span class="pres-tag accent">DTN</span> How Delay-Tolerant Networking Works</h2><div style="display:flex;justify-content:center;margin:8px 0"><svg viewBox="0 0 920 380" style="width:100%;max-width:920px" xmlns="http://www.w3.org/2000/svg"><defs><marker id="dtA" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6" fill="none" stroke="#00d4ff" stroke-width="1.2"/></marker><marker id="dtR" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6" fill="none" stroke="#f85149" stroke-width="1"/></marker></defs><text x="460" y="24" text-anchor="middle" fill="#8892a4" font-size="10" font-weight="600" letter-spacing="2">TCP/IP: END-TO-END CONNECTION (FAILS IN SPACE)</text><rect x="60" y="36" width="120" height="44" rx="6" fill="rgba(0,212,255,0.1)" stroke="#00d4ff" stroke-opacity="0.4"/><text x="120" y="63" text-anchor="middle" fill="#00d4ff" font-size="10" font-weight="600">Source</text><line x1="180" y1="58" x2="250" y2="58" stroke="#00d4ff" stroke-width="1.5" stroke-dasharray="4,3"/><text x="215" y="52" text-anchor="middle" fill="#5a6578" font-size="7">SYN</text><rect x="250" y="36" width="120" height="44" rx="6" fill="rgba(0,212,255,0.1)" stroke="#00d4ff" stroke-opacity="0.4"/><text x="310" y="63" text-anchor="middle" fill="#00d4ff" font-size="10" font-weight="600">Router</text><line x1="370" y1="58" x2="440" y2="58" stroke="#00d4ff" stroke-width="1.5" stroke-dasharray="4,3"/><text x="405" y="52" text-anchor="middle" fill="#5a6578" font-size="7">SYN</text><rect x="440" y="36" width="120" height="44" rx="6" fill="rgba(0,212,255,0.1)" stroke="#00d4ff" stroke-opacity="0.4"/><text x="500" y="63" text-anchor="middle" fill="#00d4ff" font-size="10" font-weight="600">Router</text><line x1="560" y1="58" x2="630" y2="58" stroke="#f85149" stroke-width="1.5" stroke-dasharray="4,3"/><text x="595" y="52" text-anchor="middle" fill="#f85149" font-size="7">TIMEOUT</text><rect x="630" y="36" width="120" height="44" rx="6" fill="rgba(248,81,73,0.1)" stroke="#f85149" stroke-opacity="0.4" stroke-dasharray="3,3"/><text x="690" y="63" text-anchor="middle" fill="#f85149" font-size="10" font-weight="600">Destination</text><text x="830" y="63" text-anchor="middle" fill="#f85149" font-size="20">&times;</text><text x="460" y="106" text-anchor="middle" fill="#8892a4" font-size="10" font-weight="600" letter-spacing="2">DTN: STORE-AND-FORWARD (WORKS IN SPACE)</text><rect x="20" y="118" width="160" height="100" rx="8" fill="rgba(63,185,80,0.08)" stroke="#3fb950" stroke-opacity="0.3"/><text x="100" y="142" text-anchor="middle" fill="#3fb950" font-size="10" font-weight="700">SOURCE</text><text x="100" y="160" text-anchor="middle" fill="#8892a4" font-size="8">Create Bundle</text><text x="100" y="175" text-anchor="middle" fill="#8892a4" font-size="8">Priority: P2</text><text x="100" y="190" text-anchor="middle" fill="#8892a4" font-size="8">Lifetime: 24h</text><text x="100" y="205" text-anchor="middle" fill="#5a6578" font-size="7.5">CUSTODY: Source</text><line x1="180" y1="168" x2="220" y2="168" stroke="#00d4ff" stroke-width="1.5" marker-end="url(#dtA)"/><text x="200" y="160" text-anchor="middle" fill="#5a6578" font-size="7">link up</text><rect x="220" y="118" width="160" height="100" rx="8" fill="rgba(0,212,255,0.08)" stroke="#00d4ff" stroke-opacity="0.3"/><text x="300" y="142" text-anchor="middle" fill="#00d4ff" font-size="10" font-weight="700">NODE A</text><text x="300" y="160" text-anchor="middle" fill="#8892a4" font-size="8">Forward bundle</text><text x="300" y="175" text-anchor="middle" fill="#3fb950" font-size="8">Custody accepted &#10003;</text><text x="300" y="205" text-anchor="middle" fill="#d29922" font-size="7.5">&#128193; STORE buffer: 2 bundles</text><line x1="380" y1="168" x2="420" y2="168" stroke="#d29922" stroke-width="1.5" stroke-dasharray="4,2"/><text x="400" y="160" text-anchor="middle" fill="#d29922" font-size="7">no link</text><rect x="420" y="118" width="160" height="100" rx="8" fill="rgba(210,153,34,0.08)" stroke="#d29922" stroke-opacity="0.3"/><text x="500" y="142" text-anchor="middle" fill="#d29922" font-size="10" font-weight="700">NODE B</text><text x="500" y="160" text-anchor="middle" fill="#8892a4" font-size="8">&#128193; Storing bundle</text><text x="500" y="175" text-anchor="middle" fill="#8892a4" font-size="8">Waiting for link...</text><text x="500" y="205" text-anchor="middle" fill="#d29922" font-size="7.5">&#128257; WAIT 14 min (link down)</text><line x1="580" y1="168" x2="620" y2="168" stroke="#00d4ff" stroke-width="1.5" marker-end="url(#dtA)"/><text x="600" y="160" text-anchor="middle" fill="#00d4ff" font-size="7">link up</text><rect x="620" y="118" width="160" height="100" rx="8" fill="rgba(0,212,255,0.08)" stroke="#00d4ff" stroke-opacity="0.3"/><text x="700" y="142" text-anchor="middle" fill="#00d4ff" font-size="10" font-weight="700">NODE C</text><text x="700" y="160" text-anchor="middle" fill="#8892a4" font-size="8">Forward bundle</text><text x="700" y="175" text-anchor="middle" fill="#3fb950" font-size="8">Custody accepted &#10003;</text><text x="700" y="205" text-anchor="middle" fill="#5a6578" font-size="7.5">CUSTODY: Node C</text><line x1="780" y1="168" x2="820" y2="168" stroke="#00d4ff" stroke-width="1.5" marker-end="url(#dtA)"/><text x="800" y="160" text-anchor="middle" fill="#00d4ff" font-size="7">link up</text><rect x="820" y="118" width="80" height="100" rx="8" fill="rgba(63,185,80,0.08)" stroke="#3fb950" stroke-opacity="0.3"/><text x="860" y="148" text-anchor="middle" fill="#3fb950" font-size="10" font-weight="700">DEST</text><text x="860" y="168" text-anchor="middle" fill="#3fb950" font-size="16">&#10003;</text><text x="860" y="190" text-anchor="middle" fill="#8892a4" font-size="8">Delivered</text><rect x="20" y="240" width="280" height="55" rx="6" fill="rgba(0,212,255,0.04)" stroke="#00d4ff" stroke-opacity="0.15"/><text x="160" y="260" text-anchor="middle" fill="#00d4ff" font-size="9" font-weight="600">Key Difference: Custody Transfer</text><text x="160" y="278" text-anchor="middle" fill="#8892a4" font-size="8">Each node takes legal responsibility for the bundle</text><rect x="320" y="240" width="280" height="55" rx="6" fill="rgba(63,185,80,0.04)" stroke="#3fb950" stroke-opacity="0.15"/><text x="460" y="260" text-anchor="middle" fill="#3fb950" font-size="9" font-weight="600">Data Never Lost</text><text x="460" y="278" text-anchor="middle" fill="#8892a4" font-size="8">Bundle stored until next hop confirms custody</text><rect x="620" y="240" width="280" height="55" rx="6" fill="rgba(124,92,247,0.04)" stroke="#7c5cf7" stroke-opacity="0.15"/><text x="760" y="260" text-anchor="middle" fill="#7c5cf7" font-size="9" font-weight="600">No End-to-End Needed</text><text x="760" y="278" text-anchor="middle" fill="#8892a4" font-size="8">Hop-by-hop reliability, works with 22-min delays</text><rect x="20" y="310" width="880" height="55" rx="6" fill="rgba(255,107,53,0.04)" stroke="#ff6b35" stroke-opacity="0.15"/><text x="460" y="332" text-anchor="middle" fill="#ff6b35" font-size="9" font-weight="600">Three Convergence Layers</text><text x="200" y="352" text-anchor="middle" fill="#8892a4" font-size="8.5">LTP (RFC 5326) &mdash; Deep space links, retransmission, sessions</text><text x="560" y="352" text-anchor="middle" fill="#8892a4" font-size="8.5">TCPCL (RFC 7242) &mdash; Earth segment, reliable TCP</text><text x="820" y="352" text-anchor="middle" fill="#8892a4" font-size="8.5">UDP-CL &mdash; Optical ISL, low latency</text></svg></div>',
          content: '<h2><span class="pres-tag accent">DTN</span> How Delay-Tolerant Networking Works</h2><div class="pres-grid-2" style="margin-bottom:16px"><div class="pres-card pres-card-danger"><div class="pres-card-title">TCP/IP in Space &mdash; Fails</div><ul class="pres-list"><li>Requires <strong>end-to-end ACK</strong> &mdash; impossible with 22-min delays</li><li>Connection breaks if <strong>any intermediate link</strong> drops</li><li>SYN handshake alone takes 44+ minutes RTT</li><li>No mechanism for <strong>scheduled contacts</strong></li></ul></div><div class="pres-card pres-card-accent"><div class="pres-card-title">DTN Store-and-Forward &mdash; Works</div><ul class="pres-list"><li><strong>Custody transfer</strong> &mdash; each node takes legal responsibility</li><li><strong>Store locally</strong> during link outages (hours to days)</li><li><strong>Forward when available</strong> &mdash; opportunistic scheduling</li><li><strong>Zero data loss</strong> &mdash; bundle survives any single link failure</li></ul></div></div><div class="pres-grid-3" style="margin-bottom:16px"><div class="pres-card" style="border-color:rgba(0,212,255,0.15)"><div class="pres-card-title">LTP (RFC 5326)</div><div style="font-size:0.82rem;color:var(--text-secondary)">Deep space links. Segmentation + retransmission. Handles 22-min round trips.</div></div><div class="pres-card" style="border-color:rgba(63,185,80,0.15)"><div class="pres-card-title">TCPCL (RFC 7242)</div><div style="font-size:0.82rem;color:var(--text-secondary)">Earth segment. Reliable TCP transport for ground station links.</div></div><div class="pres-card" style="border-color:rgba(255,107,53,0.15)"><div class="pres-card-title">UDP-CL</div><div style="font-size:0.82rem;color:var(--text-secondary)">Optical inter-satellite links. Low latency, high throughput.</div></div></div><details class="pres-diagram-detail"><summary class="pres-diagram-toggle">&#128206; View DTN vs TCP Diagram</summary><div style="display:flex;justify-content:center;margin:4px 0"><svg viewBox="0 0 900 200" style="width:100%;max-width:900px" xmlns="http://www.w3.org/2000/svg"><defs><marker id="dtA" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6" fill="none" stroke="#00d4ff" stroke-width="1.2"/></marker></defs><text x="450" y="18" text-anchor="middle" fill="#8892a4" font-size="10" font-weight="600" letter-spacing="2">TCP/IP FAILS: needs end-to-end ACK</text><rect x="60" y="26" width="110" height="32" rx="5" fill="rgba(0,212,255,0.1)" stroke="#00d4ff" stroke-opacity="0.4"/><text x="115" y="46" text-anchor="middle" fill="#00d4ff" font-size="10" font-weight="600">Source</text><line x1="170" y1="42" x2="230" y2="42" stroke="#00d4ff" stroke-width="1.5" stroke-dasharray="4,3"/><rect x="230" y="26" width="110" height="32" rx="5" fill="rgba(0,212,255,0.1)" stroke="#00d4ff" stroke-opacity="0.4"/><text x="285" y="46" text-anchor="middle" fill="#00d4ff" font-size="10" font-weight="600">Router</text><line x1="340" y1="42" x2="400" y2="42" stroke="#00d4ff" stroke-width="1.5" stroke-dasharray="4,3"/><rect x="400" y="26" width="110" height="32" rx="5" fill="rgba(0,212,255,0.1)" stroke="#00d4ff" stroke-opacity="0.4"/><text x="455" y="46" text-anchor="middle" fill="#00d4ff" font-size="10" font-weight="600">Router</text><line x1="510" y1="42" x2="570" y2="42" stroke="#f85149" stroke-width="1.5" stroke-dasharray="4,3"/><text x="540" y="36" text-anchor="middle" fill="#f85149" font-size="7">TIMEOUT</text><rect x="570" y="26" width="110" height="32" rx="5" fill="rgba(248,81,73,0.1)" stroke="#f85149" stroke-opacity="0.4" stroke-dasharray="3,3"/><text x="625" y="46" text-anchor="middle" fill="#f85149" font-size="10" font-weight="600">Dest</text><text x="760" y="46" text-anchor="middle" fill="#f85149" font-size="18">&times;</text><text x="450" y="84" text-anchor="middle" fill="#3fb950" font-size="10" font-weight="600" letter-spacing="2">DTN WORKS: store-and-forward with custody transfer</text><rect x="30" y="94" width="140" height="70" rx="6" fill="rgba(63,185,80,0.08)" stroke="#3fb950" stroke-opacity="0.3"/><text x="100" y="112" text-anchor="middle" fill="#3fb950" font-size="10" font-weight="700">SOURCE</text><text x="100" y="128" text-anchor="middle" fill="#8892a4" font-size="8">Create Bundle</text><text x="100" y="148" text-anchor="middle" fill="#5a6578" font-size="7.5">Custody: Source</text><line x1="170" y1="129" x2="210" y2="129" stroke="#00d4ff" stroke-width="1.5" marker-end="url(#dtA)"/><text x="190" y="122" text-anchor="middle" fill="#5a6578" font-size="7">link up</text><rect x="210" y="94" width="140" height="70" rx="6" fill="rgba(0,212,255,0.08)" stroke="#00d4ff" stroke-opacity="0.3"/><text x="280" y="112" text-anchor="middle" fill="#00d4ff" font-size="10" font-weight="700">NODE A</text><text x="280" y="128" text-anchor="middle" fill="#8892a4" font-size="8">Custody accepted</text><text x="280" y="148" text-anchor="middle" fill="#5a6578" font-size="7.5">Buffer: 2 bundles</text><line x1="350" y1="129" x2="390" y2="129" stroke="#d29922" stroke-width="1.5" stroke-dasharray="4,2"/><text x="370" y="122" text-anchor="middle" fill="#d29922" font-size="7">no link</text><rect x="390" y="94" width="140" height="70" rx="6" fill="rgba(210,153,34,0.08)" stroke="#d29922" stroke-opacity="0.3"/><text x="460" y="112" text-anchor="middle" fill="#d29922" font-size="10" font-weight="700">NODE B</text><text x="460" y="128" text-anchor="middle" fill="#8892a4" font-size="8">Storing bundle</text><text x="460" y="148" text-anchor="middle" fill="#d29922" font-size="7.5">WAIT 14 min</text><line x1="530" y1="129" x2="570" y2="129" stroke="#00d4ff" stroke-width="1.5" marker-end="url(#dtA)"/><text x="550" y="122" text-anchor="middle" fill="#00d4ff" font-size="7">link up</text><rect x="570" y="94" width="140" height="70" rx="6" fill="rgba(0,212,255,0.08)" stroke="#00d4ff" stroke-opacity="0.3"/><text x="640" y="112" text-anchor="middle" fill="#00d4ff" font-size="10" font-weight="700">NODE C</text><text x="640" y="128" text-anchor="middle" fill="#8892a4" font-size="8">Forward</text><text x="640" y="148" text-anchor="middle" fill="#5a6578" font-size="7.5">Custody: Node C</text><line x1="710" y1="129" x2="750" y2="129" stroke="#3fb950" stroke-width="1.5" marker-end="url(#dtA)"/><rect x="750" y="104" width="80" height="50" rx="6" fill="rgba(63,185,80,0.08)" stroke="#3fb950" stroke-opacity="0.3"/><text x="790" y="126" text-anchor="middle" fill="#3fb950" font-size="10" font-weight="700">DEST</text><text x="790" y="144" text-anchor="middle" fill="#3fb950" font-size="14">&#10003;</text></svg></div></details>',
        },
        {
          title: 'Network Topology',
          content: '<h2><span class="pres-tag accent">Architecture</span> Five-Tier Network &mdash; 241 Nodes Across Two Worlds</h2><div class="pres-tiers"><div class="pres-tier"><div class="pres-tier-badge" style="background:linear-gradient(135deg,#00d4ff,#0099cc)">T1</div><div class="pres-tier-content"><strong>Earth Ground (6)</strong> &mdash; DSN stations: Goldstone, Madrid, Canberra + Mission Ops Center, Network Ops, Science Ops</div></div><div class="pres-tier"><div class="pres-tier-badge" style="background:linear-gradient(135deg,#7c5cf7,#5a3fd4)">T2</div><div class="pres-tier-content"><strong>Earth Orbital (51)</strong> &mdash; 3 GEO relays + 48 LEO laser mesh constellation</div></div><div class="pres-tier"><div class="pres-tier-badge" style="background:linear-gradient(135deg,#ff6b35,#cc4a1a)">T3</div><div class="pres-tier-content"><strong>Deep Space Transit (4)</strong> &mdash; ES-L4 & ES-L5 Lagrange point relays + 2 transfer orbit satellites</div></div><div class="pres-tier"><div class="pres-tier-badge" style="background:linear-gradient(135deg,#f85149,#c9302c)">T4</div><div class="pres-tier-content"><strong>Mars Orbital (13)</strong> &mdash; 2 areostationary + 2 polar orbiters + 9 relay satellites</div></div><div class="pres-tier"><div class="pres-tier-badge" style="background:linear-gradient(135deg,#d29922,#b38318)">T5</div><div class="pres-tier-content"><strong>Mars Surface (167)</strong> &mdash; Habitats, rovers, drones, sensor networks</div></div></div><div class="pres-callout pres-callout-accent" style="margin-top:20px">Multiple redundant paths &middot; No single point of failure &middot; Lagrange relays provide coverage during solar conjunction</div>',
          speakerNotes: '241 nodes across 5 tiers. Walk through each tier. Earth Ground is the DSN - three stations around the globe for 24/7 coverage. Earth Orbital has LEO laser mesh for optical backhaul. Deep Space has Lagrange point relays - these are the critical innovation for conjunction coverage. Mars Orbital has areostationary relays at 17,032 km. Mars Surface is the most populated tier. (2 minutes)'
        },
        {
          title: '5-Tier Network Diagram',
          content: '<h2><span class="pres-tag accent">Network</span> 5-Tier Interplanetary Network &mdash; 241 Nodes</h2><div class="pres-grid-2" style="margin-bottom:16px"><div class="pres-card"><div class="pres-card-title">Tier Breakdown</div><table class="pres-table"><tr><td><strong style="color:#00d4ff">T1 Earth Ground</strong></td><td>6 nodes</td><td>DSN: Goldstone, Madrid, Canberra + MOC, NOC, SOC</td></tr><tr><td><strong style="color:#7c5cf7">T2 Earth Orbital</strong></td><td>51 nodes</td><td>3 GEO relays + 48 LEO laser mesh constellation</td></tr><tr><td><strong style="color:#ff6b35">T3 Deep Space</strong></td><td>4 nodes</td><td>ES-L4 &amp; ES-L5 Lagrange relays + 2 transfer orbit sats</td></tr><tr><td><strong style="color:#f85149">T4 Mars Orbital</strong></td><td>13 nodes</td><td>2 areostationary + 2 polar orbiters + 9 relay sats</td></tr><tr><td><strong style="color:#d29922">T5 Mars Surface</strong></td><td>167 nodes</td><td>Habitats, rovers, drones, sensor networks</td></tr></table></div><div class="pres-card"><div class="pres-card-title">Link Characteristics</div><table class="pres-table"><tr><td>Earth &harr; Deep Space</td><td>100 Mbps</td><td>1550nm optical</td></tr><tr><td>Deep Space &harr; Mars</td><td>2&ndash;200 Mbps</td><td>Distance dependent</td></tr><tr><td>Mars Orb &harr; Surface</td><td>2 Mbps</td><td>UHF/X-band</td></tr><tr><td>LEO ISL</td><td>10 Gbps</td><td>Optical inter-satellite</td></tr></table><div style="margin-top:12px;font-size:0.82rem;color:var(--text-secondary)"><strong style="color:var(--accent)">3 redundant paths</strong> &middot; No single point of failure &middot; Lagrange relays for conjunction coverage</div></div></div><div class="pres-mermaid-wrap" style="margin-bottom:16px"><div class="mermaid-diagram" data-diagram="network-topology"></div></div>',
        },
        {
          title: 'Optical Communications',
          content: '<h2><span class="pres-tag live">Live Demo</span> Optical Link Budget &mdash; 10-100&times; Faster</h2><div class="pres-grid-3" style="margin-bottom:20px"><div class="pres-stat-card" style="border-color:rgba(63,185,80,0.25)"><div class="pres-stat-value" style="color:#3fb950">100-200</div><div class="pres-stat-unit">Mbps at closest</div><div class="pres-stat-sub">54.6M km &middot; 3 min delay</div></div><div class="pres-stat-card" style="border-color:rgba(0,212,255,0.25)"><div class="pres-stat-value" style="color:#00d4ff">10-20</div><div class="pres-stat-unit">Mbps average</div><div class="pres-stat-sub">225M km &middot; 12.5 min delay</div></div><div class="pres-stat-card" style="border-color:rgba(248,81,73,0.25)"><div class="pres-stat-value" style="color:#f85149">2-5</div><div class="pres-stat-unit">Mbps at farthest</div><div class="pres-stat-sub">401M km &middot; 22 min delay</div></div></div><div class="pres-grid-2"><div class="pres-card"><div class="pres-card-title">Key Equations</div><div class="pres-code">FSPL = 20 &times; log<sub>10</sub>(4&pi;d/&lambda;)<br>Gain = 10 &times; log<sub>10</sub>(&eta; &times; (&pi;D/&lambda;)<sup>2</sup>)<br>P<sub>r</sub> = P<sub>t</sub> + G<sub>t</sub> + G<sub>r</sub> &minus; FSPL &minus; L<sub>atm</sub> &minus; L<sub>point</sub></div></div><div class="pres-card"><div class="pres-card-title">Configuration</div><table class="pres-table"><tr><td>Wavelength</td><td>1550 nm (telecom band)</td></tr><tr><td>Tx Power</td><td>5W (37 dBm)</td></tr><tr><td>Tx Aperture</td><td>22 cm</td></tr><tr><td>Rx Aperture</td><td>1.0 m</td></tr></table></div></div><div class="pres-comparison" style="margin-top:20px"><strong>vs Current RF (MRO):</strong> 0.5&ndash;6 Mbps &rarr; 2&ndash;200 Mbps &mdash; a 10-100&times; leap</div>',
          speakerNotes: 'RUN THE LIVE DEMO from the Link Budget page. Show the 3 distance scenarios. 1550nm was chosen for telecom heritage and eye safety. FSPL at average distance is -365 dB. The telescope apertures are realistic for spacecraft. RF backup for reliability. (2 minutes)'
        },
        {
          title: 'Earth-Mars Journey',
          content: '<h2><span class="pres-tag mars">Journey</span> The Path from Mars to Earth &mdash; 500 MB in 7 Hops</h2><div style="display:flex;justify-content:center;margin:4px 0"><svg viewBox="0 0 920 440" style="width:100%;max-width:920px" xmlns="http://www.w3.org/2000/svg"><defs><marker id="jmA" markerWidth="7" markerHeight="5" refX="7" refY="2.5" orient="auto"><path d="M0,0 L7,2.5 L0,5" fill="none" stroke="#ff6b35" stroke-width="1.2"/></marker><linearGradient id="jmG" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#d84315" stop-opacity="0.3"/><stop offset="50%" stop-color="#7c5cf7" stop-opacity="0.15"/><stop offset="100%" stop-color="#1e88e5" stop-opacity="0.3"/></linearGradient></defs><rect x="20" y="15" width="880" height="180" rx="10" fill="url(#jmG)" stroke="rgba(255,255,255,0.06)"/><circle cx="80" cy="80" r="45" fill="#d84315" fill-opacity="0.2" stroke="#ff6b35" stroke-width="1.5"/><text x="80" y="76" text-anchor="middle" fill="#ff6b35" font-size="11" font-weight="700">MARS</text><text x="80" y="92" text-anchor="middle" fill="#8892a4" font-size="7">Surface</text><circle cx="80" cy="100" r="8" fill="#ff7043" fill-opacity="0.6"/><circle cx="840" cy="80" r="55" fill="#1e88e5" fill-opacity="0.2" stroke="#00d4ff" stroke-width="1.5"/><text x="840" y="76" text-anchor="middle" fill="#00d4ff" font-size="11" font-weight="700">EARTH</text><text x="840" y="92" text-anchor="middle" fill="#8892a4" font-size="7">Ground</text><circle cx="840" cy="100" r="8" fill="#42a5f5" fill-opacity="0.6"/><line x1="125" y1="80" x2="795" y2="80" stroke="#5a6578" stroke-width="0.5" stroke-dasharray="4,4"/><text x="460" y="50" text-anchor="middle" fill="#5a6578" font-size="8" font-style="italic">~225 million km average distance &middot; 12.5 min one-way light time</text><rect x="150" y="70" width="72" height="40" rx="6" fill="rgba(255,112,67,0.15)" stroke="#ff7043" stroke-opacity="0.4"/><text x="186" y="86" text-anchor="middle" fill="#ff7043" font-size="7" font-weight="600">Areostat</text><text x="186" y="98" text-anchor="middle" fill="#5a6578" font-size="6">17,032 km</text><line x1="105" y1="80" x2="150" y2="80" stroke="#ff6b35" stroke-width="1.5" marker-end="url(#jmA)"/><text x="127" y="75" text-anchor="middle" fill="#5a6578" font-size="5.5">UHF</text><rect x="270" y="70" width="72" height="40" rx="6" fill="rgba(255,112,67,0.15)" stroke="#ff7043" stroke-opacity="0.4"/><text x="306" y="86" text-anchor="middle" fill="#ff7043" font-size="7" font-weight="600">Polar Orbiter</text><text x="306" y="98" text-anchor="middle" fill="#5a6578" font-size="6">Optical ISL</text><line x1="222" y1="80" x2="270" y2="80" stroke="#ff6b35" stroke-width="1.5" marker-end="url(#jmA)"/><text x="246" y="75" text-anchor="middle" fill="#5a6578" font-size="5.5">1550nm</text><rect x="400" y="60" width="100" height="50" rx="6" fill="rgba(124,92,247,0.15)" stroke="#7c5cf7" stroke-opacity="0.4"/><text x="450" y="78" text-anchor="middle" fill="#7c5cf7" font-size="7" font-weight="600">ES-L4 Relay</text><text x="450" y="92" text-anchor="middle" fill="#5a6578" font-size="6">Lagrange Point</text><text x="450" y="103" text-anchor="middle" fill="#5a6578" font-size="6">150M km from Earth</text><line x1="342" y1="80" x2="400" y2="80" stroke="#7c5cf7" stroke-width="1.5" marker-end="url(#jmA)"/><text x="371" y="75" text-anchor="middle" fill="#5a6578" font-size="5.5">Deep space optical</text><rect x="550" y="70" width="80" height="40" rx="6" fill="rgba(66,165,245,0.15)" stroke="#42a5f5" stroke-opacity="0.4"/><text x="590" y="86" text-anchor="middle" fill="#42a5f5" font-size="7" font-weight="600">LEO Mesh</text><text x="590" y="98" text-anchor="middle" fill="#5a6578" font-size="6">48 satellites</text><line x1="500" y1="80" x2="550" y2="80" stroke="#42a5f5" stroke-width="1.5" marker-end="url(#jmA)"/><text x="525" y="75" text-anchor="middle" fill="#5a6578" font-size="5.5">1550nm</text><rect x="680" y="70" width="80" height="40" rx="6" fill="rgba(0,212,255,0.15)" stroke="#00d4ff" stroke-opacity="0.4"/><text x="720" y="86" text-anchor="middle" fill="#00d4ff" font-size="7" font-weight="600">DSN</text><text x="720" y="98" text-anchor="middle" fill="#5a6578" font-size="6">Goldstone</text><line x1="630" y1="80" x2="680" y2="80" stroke="#00d4ff" stroke-width="1.5" marker-end="url(#jmA)"/><text x="655" y="75" text-anchor="middle" fill="#5a6578" font-size="5.5">Ka-band</text><line x1="760" y1="80" x2="795" y2="80" stroke="#00d4ff" stroke-width="1.5" marker-end="url(#jmA)"/><text x="20" y="210" text-anchor="middle" fill="#8892a4" font-size="10" font-weight="600" letter-spacing="1.5">HOP-BY-HOP DETAIL</text><rect x="20" y="225" width="125" height="90" rx="6" fill="rgba(255,112,67,0.08)" stroke="#ff7043" stroke-opacity="0.25"/><text x="82" y="244" text-anchor="middle" fill="#ff7043" font-size="8" font-weight="700">HOP 1</text><text x="82" y="258" text-anchor="middle" fill="#8892a4" font-size="7">Rover &rarr; UHF</text><text x="82" y="272" text-anchor="middle" fill="#5a6578" font-size="7">Band: UHF (400 MHz)</text><text x="82" y="286" text-anchor="middle" fill="#5a6578" font-size="7">Range: ~400 km</text><text x="82" y="300" text-anchor="middle" fill="#5a6578" font-size="7">Rate: 2 Mbps</text><line x1="145" y1="270" x2="160" y2="270" stroke="#5a6578" stroke-width="1" marker-end="url(#jmA)"/><rect x="160" y="225" width="125" height="90" rx="6" fill="rgba(255,112,67,0.08)" stroke="#ff7043" stroke-opacity="0.25"/><text x="222" y="244" text-anchor="middle" fill="#ff7043" font-size="8" font-weight="700">HOP 2</text><text x="222" y="258" text-anchor="middle" fill="#8892a4" font-size="7">UHF &rarr; Areostat</text><text x="222" y="272" text-anchor="middle" fill="#5a6578" font-size="7">Band: UHF uplink</text><text x="222" y="286" text-anchor="middle" fill="#5a6578" font-size="7">Altitude: 17,032 km</text><text x="222" y="300" text-anchor="middle" fill="#5a6578" font-size="7">Rate: 256 kbps</text><line x1="285" y1="270" x2="300" y2="270" stroke="#5a6578" stroke-width="1" marker-end="url(#jmA)"/><rect x="300" y="225" width="125" height="90" rx="6" fill="rgba(255,112,67,0.08)" stroke="#ff7043" stroke-opacity="0.25"/><text x="362" y="244" text-anchor="middle" fill="#ff7043" font-size="8" font-weight="700">HOP 3</text><text x="362" y="258" text-anchor="middle" fill="#8892a4" font-size="7">Areostat &rarr; Polar</text><text x="362" y="272" text-anchor="middle" fill="#5a6578" font-size="7">Band: Optical ISL</text><text x="362" y="286" text-anchor="middle" fill="#5a6578" font-size="7">Range: ~20,000 km</text><text x="362" y="300" text-anchor="middle" fill="#5a6578" font-size="7">Rate: 10 Gbps</text><line x1="425" y1="270" x2="440" y2="270" stroke="#5a6578" stroke-width="1" marker-end="url(#jmA)"/><rect x="440" y="225" width="125" height="90" rx="6" fill="rgba(124,92,247,0.08)" stroke="#7c5cf7" stroke-opacity="0.25"/><text x="502" y="244" text-anchor="middle" fill="#7c5cf7" font-size="8" font-weight="700">HOP 4-5</text><text x="502" y="258" text-anchor="middle" fill="#8892a4" font-size="7">Polar &rarr; Deep Space</text><text x="502" y="272" text-anchor="middle" fill="#5a6578" font-size="7">Band: 1550nm laser</text><text x="502" y="286" text-anchor="middle" fill="#5a6578" font-size="7">Range: ~225M km</text><text x="502" y="300" text-anchor="middle" fill="#5a6578" font-size="7">Rate: 10-20 Mbps</text><line x1="565" y1="270" x2="580" y2="270" stroke="#5a6578" stroke-width="1" marker-end="url(#jmA)"/><rect x="580" y="225" width="125" height="90" rx="6" fill="rgba(66,165,245,0.08)" stroke="#42a5f5" stroke-opacity="0.25"/><text x="642" y="244" text-anchor="middle" fill="#42a5f5" font-size="8" font-weight="700">HOP 6</text><text x="642" y="258" text-anchor="middle" fill="#8892a4" font-size="7">LEO mesh routing</text><text x="642" y="272" text-anchor="middle" fill="#5a6578" font-size="7">Optical inter-satellite</text><text x="642" y="286" text-anchor="middle" fill="#5a6578" font-size="7">48 LEO satellites</text><text x="642" y="300" text-anchor="middle" fill="#5a6578" font-size="7">Rate: 10 Gbps</text><line x1="705" y1="270" x2="720" y2="270" stroke="#5a6578" stroke-width="1" marker-end="url(#jmA)"/><rect x="720" y="225" width="125" height="90" rx="6" fill="rgba(63,185,80,0.08)" stroke="#3fb950" stroke-opacity="0.25"/><text x="782" y="244" text-anchor="middle" fill="#3fb950" font-size="8" font-weight="700">HOP 7</text><text x="782" y="258" text-anchor="middle" fill="#8892a4" font-size="7">DSN &rarr; JPL MOC</text><text x="782" y="272" text-anchor="middle" fill="#5a6578" font-size="7">Band: Ka-band</text><text x="782" y="286" text-anchor="middle" fill="#5a6578" font-size="7">Fiber backbone</text><text x="782" y="300" text-anchor="middle" fill="#3fb950" font-size="7" font-weight="600">DELIVERED &#10003;</text><rect x="20" y="330" width="280" height="50" rx="6" fill="rgba(0,212,255,0.04)" stroke="#00d4ff" stroke-opacity="0.15"/><text x="160" y="350" text-anchor="middle" fill="#00d4ff" font-size="9" font-weight="600">Total Transit: ~13 min</text><text x="160" y="368" text-anchor="middle" fill="#8892a4" font-size="8">vs 12.5 min light-time &mdash; near speed of light!</text><rect x="320" y="330" width="280" height="50" rx="6" fill="rgba(63,185,80,0.04)" stroke="#3fb950" stroke-opacity="0.15"/><text x="460" y="350" text-anchor="middle" fill="#3fb950" font-size="9" font-weight="600">DTN Overhead: &lt;5%</text><text x="460" y="368" text-anchor="middle" fill="#8892a4" font-size="8">Store-and-forward adds minimal latency</text><rect x="620" y="330" width="280" height="50" rx="6" fill="rgba(124,92,247,0.04)" stroke="#7c5cf7" stroke-opacity="0.15"/><text x="760" y="350" text-anchor="middle" fill="#7c5cf7" font-size="9" font-weight="600">QKD Secured</text><text x="760" y="368" text-anchor="middle" fill="#8892a4" font-size="8">End-to-end quantum encryption</text><rect x="20" y="395" width="880" height="35" rx="6" fill="rgba(248,81,73,0.04)" stroke="#f85149" stroke-opacity="0.15"/><text x="460" y="417" text-anchor="middle" fill="#f85149" font-size="9" font-weight="600">&#9889; If any link drops mid-transfer, the bundle is stored safely &mdash; zero data loss</text></svg></div>',
          content: '<h2><span class="pres-tag mars">Journey</span> The Path from Mars to Earth &mdash; 500 MB in 7 Hops</h2><div class="pres-grid-2" style="margin-bottom:16px"><div class="pres-card"><div class="pres-card-title">Hop-by-Hop Route</div><table class="pres-table"><tr><td><strong>Hop 1</strong></td><td>Rover &rarr; UHF uplink</td><td>400 MHz · 2 Mbps · ~400 km</td></tr><tr><td><strong>Hop 2</strong></td><td>UHF &rarr; Areostationary</td><td>UHF · 256 kbps · 17,032 km alt</td></tr><tr><td><strong>Hop 3</strong></td><td>Areostationary &rarr; Polar</td><td>Optical ISL · 10 Gbps</td></tr><tr><td><strong>Hop 4-5</strong></td><td>Polar &rarr; Lagrange relay &rarr; LEO</td><td>1550nm laser · 10-20 Mbps · 225M km</td></tr><tr><td><strong>Hop 6</strong></td><td>LEO mesh routing</td><td>Optical ISL · 10 Gbps · 48 sats</td></tr><tr><td><strong>Hop 7</strong></td><td>DSN &rarr; JPL MOC</td><td>Ka-band + fiber backbone</td></tr></table></div><div class="pres-card"><div class="pres-card-title">Key Metrics</div><div class="pres-grid-2" style="gap:10px"><div class="pres-stat-card" style="border-color:rgba(0,212,255,0.2);padding:14px 10px"><div class="pres-stat-value" style="color:#00d4ff;font-size:1.6rem">~13 min</div><div class="pres-stat-unit">Total transit</div></div><div class="pres-stat-card" style="border-color:rgba(63,185,80,0.2);padding:14px 10px"><div class="pres-stat-value" style="color:#3fb950;font-size:1.6rem">&lt;5%</div><div class="pres-stat-unit">DTN overhead</div></div><div class="pres-stat-card" style="border-color:rgba(124,92,247,0.2);padding:14px 10px"><div class="pres-stat-value" style="color:#7c5cf7;font-size:1.6rem">QKD</div><div class="pres-stat-unit">Encrypted</div></div><div class="pres-stat-card" style="border-color:rgba(255,107,53,0.2);padding:14px 10px"><div class="pres-stat-value" style="color:#ff6b35;font-size:1.6rem">7</div><div class="pres-stat-unit">Relay hops</div></div></div><div style="margin-top:10px;font-size:0.82rem;color:var(--text-secondary)">vs 12.5 min light-time &mdash; near speed of light delivery.</div></div></div><details class="pres-diagram-detail"><summary class="pres-diagram-toggle">&#128206; View Journey Diagram</summary><div style="display:flex;justify-content:center;margin:4px 0"><svg viewBox="0 0 900 140" style="width:100%;max-width:900px" xmlns="http://www.w3.org/2000/svg"><defs><marker id="jmA" markerWidth="7" markerHeight="5" refX="7" refY="2.5" orient="auto"><path d="M0,0 L7,2.5 L0,5" fill="none" stroke="#ff6b35" stroke-width="1.2"/></marker><linearGradient id="jmG" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#d84315" stop-opacity="0.2"/><stop offset="50%" stop-color="#7c5cf7" stop-opacity="0.1"/><stop offset="100%" stop-color="#1e88e5" stop-opacity="0.2"/></linearGradient></defs><rect x="10" y="10" width="880" height="100" rx="8" fill="url(#jmG)"/><circle cx="60" cy="60" r="30" fill="#d84315" fill-opacity="0.2" stroke="#ff6b35" stroke-width="1.5"/><text x="60" y="56" text-anchor="middle" fill="#ff6b35" font-size="9" font-weight="700">MARS</text><text x="60" y="70" text-anchor="middle" fill="#8892a4" font-size="7">Surface</text><rect x="130" y="45" width="60" height="30" rx="4" fill="rgba(255,112,67,0.15)" stroke="#ff7043" stroke-opacity="0.4"/><text x="160" y="64" text-anchor="middle" fill="#ff7043" font-size="7" font-weight="600">Areostat</text><line x1="90" y1="60" x2="130" y2="60" stroke="#ff6b35" stroke-width="1.5" marker-end="url(#jmA)"/><rect x="230" y="45" width="60" height="30" rx="4" fill="rgba(255,112,67,0.15)" stroke="#ff7043" stroke-opacity="0.4"/><text x="260" y="64" text-anchor="middle" fill="#ff7043" font-size="7" font-weight="600">Polar</text><line x1="190" y1="60" x2="230" y2="60" stroke="#ff6b35" stroke-width="1.5" marker-end="url(#jmA)"/><rect x="340" y="40" width="80" height="40" rx="4" fill="rgba(124,92,247,0.15)" stroke="#7c5cf7" stroke-opacity="0.4"/><text x="380" y="58" text-anchor="middle" fill="#7c5cf7" font-size="7" font-weight="600">ES-L4 Relay</text><text x="380" y="72" text-anchor="middle" fill="#5a6578" font-size="6">Lagrange Point</text><line x1="290" y1="60" x2="340" y2="60" stroke="#7c5cf7" stroke-width="1.5" marker-end="url(#jmA)"/><rect x="470" y="45" width="60" height="30" rx="4" fill="rgba(66,165,245,0.15)" stroke="#42a5f5" stroke-opacity="0.4"/><text x="500" y="64" text-anchor="middle" fill="#42a5f5" font-size="7" font-weight="600">LEO Mesh</text><line x1="420" y1="60" x2="470" y2="60" stroke="#42a5f5" stroke-width="1.5" marker-end="url(#jmA)"/><rect x="580" y="45" width="60" height="30" rx="4" fill="rgba(0,212,255,0.15)" stroke="#00d4ff" stroke-opacity="0.4"/><text x="610" y="64" text-anchor="middle" fill="#00d4ff" font-size="7" font-weight="600">DSN</text><line x1="530" y1="60" x2="580" y2="60" stroke="#00d4ff" stroke-width="1.5" marker-end="url(#jmA)"/><circle cx="690" cy="60" r="35" fill="#1e88e5" fill-opacity="0.2" stroke="#00d4ff" stroke-width="1.5"/><text x="690" y="56" text-anchor="middle" fill="#00d4ff" font-size="9" font-weight="700">EARTH</text><text x="690" y="70" text-anchor="middle" fill="#8892a4" font-size="7">Ground</text><line x1="640" y1="60" x2="655" y2="60" stroke="#3fb950" stroke-width="1.5" marker-end="url(#jmA)"/><text x="380" y="110" text-anchor="middle" fill="#5a6578" font-size="8">~225M km average · 12.5 min one-way · 7 relay hops · ~13 min total</text></svg></div></details>',
        },
        {
          title: 'RL Routing',
          content: '<h2><span class="pres-tag quantum">AI</span> Reinforcement Learning Routing &mdash; Brains of the Network</h2><div class="pres-grid-2" style="margin-bottom:20px"><div class="pres-card pres-card-danger"><div class="pres-card-title">Current: Contact Graph Routing</div><ul class="pres-list"><li>Requires pre-computed contact schedules</li><li>Cannot adapt to unexpected events</li><li>Manual schedule updates needed</li><li>Single-objective optimization only</li><li>Brittle under dynamic conditions</li></ul></div><div class="pres-card pres-card-accent"><div class="pres-card-title">Our Solution: RL Agent</div><div style="margin-bottom:8px"><strong>State:</strong> node, neighbors, link quality, buffer, priority, deadline</div><div style="margin-bottom:8px"><strong>Actions:</strong> Forward &middot; Store &middot; Drop &middot; Split</div><div class="pres-code" style="margin-top:10px">R = &alpha;(delivery) &minus; &beta;(delay) &minus; &gamma;(hops)<br>&nbsp;&nbsp;&minus; &delta;(drops) &minus; &epsilon;(energy)</div><table class="pres-table" style="margin-top:8px"><tr><td>&alpha;=1.0</td><td>&beta;=0.001</td><td>&gamma;=0.1</td><td>&delta;=10.0</td><td>&epsilon;=0.01</td></tr></table></div></div><div class="pres-grid-3"><div class="pres-stat-card" style="border-color:rgba(63,185,80,0.2)"><div class="pres-stat-value" style="color:#3fb950">+20-40%</div><div class="pres-stat-unit">Faster delivery</div></div><div class="pres-stat-card" style="border-color:rgba(0,212,255,0.2)"><div class="pres-stat-value" style="color:#00d4ff">3600&times;</div><div class="pres-stat-unit">Faster failure recovery</div></div><div class="pres-stat-card" style="border-color:rgba(124,92,247,0.2)"><div class="pres-stat-value" style="color:#7c5cf7">Federated</div><div class="pres-stat-unit">Multi-agent training</div></div></div>',
          speakerNotes: 'CGR is what NASA uses today. It\'s static - you have to pre-compute schedules. Our RL agent learns from experience. 8 state variables, 4 actions. The reward function balances delivery probability against delay, hops, drops, and energy. Multi-agent federated learning means agents at each node share knowledge. (2 minutes)'
        },
        {
          title: 'Quantum Security',
          content: '<h2><span class="pres-tag quantum">Security</span> Quantum Key Distribution &mdash; Unbreakable by Law of Physics</h2><div class="pres-grid-2" style="margin-bottom:20px"><div class="pres-card pres-card-quantum"><div class="pres-card-title">BB84 Protocol</div><ol class="pres-list"><li>Alice sends qubits in random bases (rectilinear/diagonal)</li><li>Bob measures in random bases</li><li>Public basis comparison &mdash; ~50% match</li><li>Estimate Quantum Bit Error Rate (QBER)</li><li><strong>QBER &lt; 11% &rarr; No eavesdropper &rarr; SECURE</strong></li><li>CASCADE reconciliation + Privacy amplification</li></ol></div><div class="pres-card"><div class="pres-card-title">Deployment Roadmap</div><table class="pres-table"><tr><td><strong>Phase 1</strong></td><td>Earth &harr; LEO</td><td>BB84</td><td>1-10 kbps</td></tr><tr><td><strong>Phase 2</strong></td><td>Earth &harr; GEO</td><td>BB84 + E91</td><td>100-1000 bps</td></tr><tr><td><strong>Phase 3</strong></td><td>Earth &harr; Mars</td><td>E91 + Repeaters</td><td>1-10 bps</td></tr></table><div style="margin-top:12px;font-size:0.8rem;color:var(--text-muted)"><strong>Quantum repeaters at L4/L5:</strong> Entanglement swapping + purification extends range across 225M km</div></div></div><div class="pres-grid-2"><div class="pres-callout pres-callout-quantum">Not computationally hard &mdash; information-theoretically secure. Even a quantum computer cannot break it.</div><div class="pres-card"><div class="pres-card-title">Post-Quantum Crypto (Complement)</div><div style="font-size:0.82rem;color:var(--text-secondary)"><strong>Kyber</strong> (ML-KEM) &mdash; Key encapsulation<br><strong>Dilithium</strong> (ML-DSA) &mdash; Digital signatures<br><span style="color:var(--text-muted)">Defense in depth: QKD + PQC together</span></div></div></div>',
          speakerNotes: 'BB84 is beautifully simple: send qubits, measure, compare bases, check QBER. If QBER is below 11%, no one listened in. CASCADE reconciliation and privacy amplification clean the key. E91 uses entanglement. Quantum repeaters at Lagrange points extend range. Post-quantum crypto as backup layer. (2 minutes)'
        },
        {
          title: 'Orbital Mechanics',
          content: '<h2><span class="pres-tag mars">Orbital</span> Contact Windows &amp; The Synodic Dance</h2><div class="pres-grid-2" style="margin-bottom:20px"><div class="pres-card"><div class="pres-card-title">Mars Orbital Parameters</div><table class="pres-table"><tr><td>Semi-major axis</td><td>1.524 AU (227.9M km)</td></tr><tr><td>Synodic period</td><td>779.94 days (~26 months)</td></tr><tr><td>Closest approach</td><td>54.6M km (3 min light time)</td></tr><tr><td>Farthest distance</td><td>401M km (22 min light time)</td></tr><tr><td>Areostationary orbit</td><td>17,032 km altitude</td></tr><tr><td>Max relative velocity</td><td>~24 km/s</td></tr></table></div><div class="pres-card"><div class="pres-card-title">Contact Quality Windows</div><table class="pres-table"><tr><td><strong style="color:#3fb950">Optimal (opposition)</strong></td><td>8-12 hrs/day</td><td>100-200 Mbps</td></tr><tr><td><strong style="color:#00d4ff">Good</strong></td><td>6-8 hrs/day</td><td>20-100 Mbps</td></tr><tr><td><strong style="color:#d29922">Fair (quadrature)</strong></td><td>2-4 hrs/day</td><td>5-20 Mbps</td></tr><tr><td><strong style="color:#f85149">Blackout (conjunction)</strong></td><td>0 hrs direct</td><td>Lagrange relay</td></tr></table></div></div><div class="pres-grid-2"><div class="pres-card"><div class="pres-card-title">Doppler Compensation</div><div style="font-size:0.85rem;color:var(--text-secondary)">Frequency shift at 1550nm: <strong>~15 GHz</strong><br>Real-time compensation required for optical links<br>Classical + relativistic corrections applied</div></div><div class="pres-card"><div class="pres-card-title">Conjunction Survival Strategy</div><ol class="pres-list"><li>T-14 days: Pre-position critical data uploads</li><li>T-7 days: Activate Lagrange relay chain</li><li>T-0 to T+14: Fully autonomous operations</li><li>T+14 days: Resume direct optical links</li></ol></div></div>',
          speakerNotes: 'Mars and Earth dance around the Sun with a 26-month synodic period. Everything changes - distance, delay, bandwidth. At opposition we get great bandwidth. At conjunction, the Sun blocks everything. Our Lagrange relays at ES-L4 and ES-L5 maintain 50-70% capacity during conjunction. Doppler shift of 15 GHz at optical wavelengths requires real-time compensation. (1.5 minutes)'
        },
        {
          title: 'End-to-End Mission',
          content: '<h2><span class="pres-tag live">Live Demo</span> Mars Surface &rarr; Earth &mdash; 500 MB in 7 Hops</h2><div class="pres-card pres-card-glow" style="margin-bottom:20px"><div class="pres-card-title">Scenario: Perseverance Rover &rarr; JPL Mission Operations Center</div><div class="pres-route-hops"><div class="pres-hop"><div class="pres-hop-num">1</div><div class="pres-hop-label">Rover<br><span>500 MB &middot; P2</span></div></div><div class="pres-hop-arrow">&rarr;</div><div class="pres-hop"><div class="pres-hop-num">2</div><div class="pres-hop-label">UHF<br><span>Uplink</span></div></div><div class="pres-hop-arrow">&rarr;</div><div class="pres-hop"><div class="pres-hop-num">3</div><div class="pres-hop-label">MRS-Alpha<br><span>Areostationary</span></div></div><div class="pres-hop-arrow">&rarr;</div><div class="pres-hop"><div class="pres-hop-num">4</div><div class="pres-hop-label">MRS-Polar<br><span>Optical ISL</span></div></div><div class="pres-hop-arrow">&rarr;</div><div class="pres-hop"><div class="pres-hop-num">5</div><div class="pres-hop-label">Deep Space<br><span>1550nm laser</span></div></div><div class="pres-hop-arrow">&rarr;</div><div class="pres-hop"><div class="pres-hop-num">6</div><div class="pres-hop-label">LEO Mesh<br><span>12.5 min</span></div></div><div class="pres-hop-arrow">&rarr;</div><div class="pres-hop"><div class="pres-hop-num">7</div><div class="pres-hop-label">DSN &rarr; MOC<br><span>Delivered &#10003;</span></div></div></div></div><div class="pres-grid-4"><div class="pres-stat-card" style="border-color:rgba(0,212,255,0.2)"><div class="pres-stat-value" style="color:#00d4ff">~13 min</div><div class="pres-stat-unit">Total transit</div></div><div class="pres-stat-card" style="border-color:rgba(63,185,80,0.2)"><div class="pres-stat-value" style="color:#3fb950">&lt;5%</div><div class="pres-stat-unit">DTN overhead</div></div><div class="pres-stat-card" style="border-color:rgba(255,107,53,0.2)"><div class="pres-stat-value" style="color:#ff6b35">7</div><div class="pres-stat-unit">Relay hops</div></div><div class="pres-stat-card" style="border-color:rgba(124,92,247,0.2)"><div class="pres-stat-value" style="color:#7c5cf7">QKD</div><div class="pres-stat-unit">Quantum secured</div></div></div><div class="pres-callout" style="margin-top:20px">If any link drops mid-transfer, the bundle is <strong>not</strong> lost &mdash; it\'s stored and forwarded when the link returns. That\'s the power of DTN.</div>',
          speakerNotes: 'Walk through the 7-hop journey. 500MB from Perseverance to JPL. Total transit ~13 min vs 12.5 min light-time - near speed of light! DTN overhead under 5%. Key point: if link drops at hop 5, the bundle stays stored at hop 4 and retries. No data loss. RUN LIVE DEMO if time permits. (2 minutes)'
        },
        {
          title: 'Data Flow Diagram',
          content: '<h2><span class="pres-tag quantum">Data Flow</span> End-to-End Bundle Journey Through the Stack</h2><div class="pres-grid-2" style="margin-bottom:16px"><div class="pres-card"><div class="pres-card-title">Application &rarr; Transport</div><ol class="pres-list"><li><strong style="color:#00d4ff">Source Node</strong> &mdash; Science data generated (500 MB camera image)</li><li><strong style="color:#7c5cf7">Bundle Protocol</strong> &mdash; BPv7 wraps data + metadata (priority P2, lifetime 24h)</li><li><strong style="color:#3fb950">RL Routing</strong> &mdash; Agent evaluates state, selects optimal next hop</li><li><strong style="color:#c84cff">QKD Encrypt</strong> &mdash; BB84 shared key applied (256-bit AES-256)</li></ol></div><div class="pres-card"><div class="pres-card-title">Convergence &rarr; Physical &rarr; Delivery</div><ol class="pres-list"><li><strong style="color:#ff6b35">LTP Segmentation</strong> &mdash; Bundle split into blocks, RS encoding, retransmission</li><li><strong style="color:#d29922">Store &amp; Wait</strong> &mdash; Buffer at relay until link becomes available</li><li><strong style="color:#00d4ff">Physical TX</strong> &mdash; UHF &rarr; Optical ISL &rarr; 1550nm deep space &rarr; Ka-band</li><li><strong style="color:#3fb950">LTP Reassemble</strong> &rarr; QKD Decrypt &rarr; Delivered to JPL MOC &#10003;</li></ol></div></div><div class="pres-callout" style="margin-bottom:16px">Each hop repeats: <strong style="color:#00d4ff">BPv7</strong> &rarr; <strong style="color:#7c5cf7">LTP</strong> &rarr; <strong style="color:#ff6b35">Physical</strong> &rarr; <strong style="color:#3fb950">Store/Forward</strong> &rarr; <strong style="color:#c84cff">Custody Transfer</strong></div><div class="pres-mermaid-wrap" style="margin-bottom:16px"><div class="mermaid-diagram" data-diagram="data-flow"></div></div>',
        },
        {
          title: 'Performance',
          content: '<h2><span class="pres-tag success">Results</span> AETHERIX vs Current Mars Communication</h2><div class="pres-table-wide"><table class="pres-table"><thead><tr><th>Metric</th><th>Current (MRO)</th><th>AETHERIX</th><th>Improvement</th></tr></thead><tbody><tr><td><strong>Downlink Rate</strong></td><td>0.5 &ndash; 6 Mbps</td><td>2 &ndash; 200 Mbps</td><td class="pres-highlight-good">10&ndash;100&times;</td></tr><tr><td><strong>Daily Data Volume</strong></td><td>5 &ndash; 10 GB</td><td>50 &ndash; 100 GB</td><td class="pres-highlight-good">10&ndash;20&times;</td></tr><tr><td><strong>Network Availability</strong></td><td>60 &ndash; 75%</td><td>&gt;95%</td><td class="pres-highlight-good">+20&ndash;35%</td></tr><tr><td><strong>Routing</strong></td><td>Static (CGR)</td><td>RL-adaptive, autonomous</td><td>Autonomous</td></tr><tr><td><strong>Security</strong></td><td>AES-256</td><td>QKD + Post-Quantum</td><td>Quantum-proof</td></tr><tr><td><strong>Scalability</strong></td><td>5 &ndash; 10 assets</td><td>241 nodes</td><td class="pres-highlight-good">24&ndash;48&times;</td></tr><tr><td><strong>Cost per MB</strong></td><td>$0.10</td><td>$0.01</td><td class="pres-highlight-good">10&times; cheaper</td></tr><tr><td><strong>Solar Conjunction</strong></td><td>Complete blackout</td><td>50&ndash;70% via Lagrange relays</td><td class="pres-highlight-good">+50&ndash;70%</td></tr></tbody></table></div><div class="pres-callout pres-callout-accent" style="margin-top:20px">10&ndash;100&times; faster &middot; &gt;95% availability &middot; Quantum-secure &middot; 1/10th cost per megabyte</div>',
          speakerNotes: 'Hit these numbers with confidence. 10-100x faster. >95% availability vs 60-75%. Quantum-secure. 241 nodes vs 5-10 assets. $0.01 vs $0.10 per MB. The conjunction improvement is thanks to Lagrange relays. All metrics are backed by our simulation engine. (1 minute)'
        },
        {
          title: 'Implementation',
          content: '<h2><span class="pres-tag accent">Implementation</span> What We Built &mdash; 10 Interactive Demos</h2><div class="pres-grid-4" style="margin-bottom:20px"><div class="pres-stat-card" style="border-color:rgba(63,185,80,0.2)"><div class="pres-stat-value" style="color:#3fb950">27</div><div class="pres-stat-unit">Python modules</div></div><div class="pres-stat-card" style="border-color:rgba(0,212,255,0.2)"><div class="pres-stat-value" style="color:#00d4ff">149</div><div class="pres-stat-unit">Unit tests</div></div><div class="pres-stat-card" style="border-color:rgba(124,92,247,0.2)"><div class="pres-stat-value" style="color:#7c5cf7">10</div><div class="pres-stat-unit">Live demos</div></div><div class="pres-stat-card" style="border-color:rgba(255,107,53,0.2)"><div class="pres-stat-value" style="color:#ff6b35">5</div><div class="pres-stat-unit">Routing policies</div></div></div><div class="pres-grid-2"><div class="pres-card"><div class="pres-card-title">Core Modules</div><ul class="pres-list"><li><strong>Link Budget</strong> &mdash; Optical + RF (Ka/X/S/UHF) calculators</li><li><strong>RL Agent</strong> &mdash; Q-learning with epsilon-greedy + federated learning</li><li><strong>QKD</strong> &mdash; BB84, E91, quantum repeaters, privacy amplification</li><li><strong>Bundle Protocol</strong> &mdash; BPv7 with custody transfer + LTP</li><li><strong>Topology</strong> &mdash; 241-node 5-tier network with BFS routing</li><li><strong>Simulation</strong> &mdash; Full scenario engine + policy evaluator</li></ul></div><div class="pres-card"><div class="pres-card-title">Standards Compliance</div><table class="pres-table"><tr><td><strong>CCSDS 734.2-B-1</strong></td><td>DTN Architecture</td></tr><tr><td><strong>CCSDS 735.1-B-1</strong></td><td>Bundle Protocol</td></tr><tr><td><strong>CCSDS 141.0-B-1</strong></td><td>Optical Communications</td></tr><tr><td><strong>CCSDS 142.0-B-2</strong></td><td>Space Link Identifiers</td></tr><tr><td><strong>RFC 9171</strong></td><td>Bundle Protocol v7</td></tr><tr><td><strong>NIST FIPS 203/204</strong></td><td>Post-Quantum Crypto</td></tr></table></div></div>',
          speakerNotes: 'This is real, working code. 27 Python modules, 149 tests, 10 interactive demos. All the physics is real - no mocked data. The showcase site has live calculators you can use right now. Standards compliance is complete - CCSDS, IETF, and NIST. (1.5 minutes)'
        },
        {
          title: 'Roadmap',
          content: '<h2><span class="pres-tag warning">Future</span> From Demo to Deployment</h2><div class="pres-timeline"><div class="pres-timeline-item"><div class="pres-timeline-dot" style="border-color:#3fb950;background:#3fb950"></div><div class="pres-timeline-title" style="color:#3fb950">Phase 1&ndash;4: Core Architecture <span class="pres-pill success">Complete</span></div><div class="pres-timeline-desc">Topology design &middot; RL routing agent &middot; QKD protocols &middot; Web showcase with 10 live demos &middot; 149 unit tests</div></div><div class="pres-timeline-item"><div class="pres-timeline-dot" style="border-color:#00d4ff"></div><div class="pres-timeline-title">Phase 5: Network Simulation</div><div class="pres-timeline-desc">ns-3 / OMNeT++ integration &middot; Realistic propagation models &middot; Performance benchmarking under simulated link conditions</div></div><div class="pres-timeline-item"><div class="pres-timeline-dot" style="border-color:#7c5cf7"></div><div class="pres-timeline-title">Phase 6: Production Upgrade</div><div class="pres-timeline-desc">Deep Q-Network (DQN) replacing Q-table &middot; ION-DTN integration for real Bundle Protocol &middot; JPL Horizons ephemeris data</div></div><div class="pres-timeline-item"><div class="pres-timeline-dot" style="border-color:#ff6b35"></div><div class="pres-timeline-title">Phase 7: Hardware Validation</div><div class="pres-timeline-desc">Hardware-in-the-loop testing &middot; SDR prototype &middot; Optical link ground demonstration &middot; Mission integration study</div></div></div>',
          speakerNotes: 'Phases 1-4 are done - this is what you see today. Phase 5: ns-3 simulation for realistic network modeling. Phase 6: Upgrade to DQN and integrate with NASA\'s ION-DTN implementation. Phase 7: Hardware prototypes with SDRs and optical links. The path from demo to deployed system. (1.5 minutes)'
        },
        {
          title: 'Conclusion',
          content: '<div class="pres-hero"><div class="pres-hero-title" style="font-size:2.8rem;letter-spacing:8px;margin-bottom:12px">Conclusion</div><div class="pres-hero-sub" style="max-width:820px">Why AETHERIX Was Needed &amp; What We Built</div><div class="pres-divider"></div><div style="max-width:800px;margin:0 auto;text-align:left"><div style="background:rgba(var(--danger-rgb),0.06);border:1px solid rgba(var(--danger-rgb),0.15);border-radius:var(--radius-lg);padding:16px 20px;margin-bottom:16px"><div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#f85149;margin-bottom:8px">The Problem We Solved</div><div style="font-size:0.85rem;color:var(--text-secondary);line-height:1.6">TCP/IP cannot work across interplanetary distances (3&ndash;22 min delays, 2-week blackouts, 7&times; distance variation). Current Mars communication delivers only 0.5&ndash;6 Mbps with 60&ndash;75% availability. We needed a fundamentally new networking paradigm for reliable interplanetary communication.</div></div><div style="background:rgba(var(--success-rgb),0.06);border:1px solid rgba(var(--success-rgb),0.15);border-radius:var(--radius-lg);padding:16px 20px;margin-bottom:16px"><div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#3fb950;margin-bottom:8px">What We Built</div><div style="font-size:0.85rem;color:var(--text-secondary);line-height:1.6">AETHERIX: a complete delay-tolerant networking platform with <strong style="color:var(--text-primary)">BPv7 store-and-forward</strong>, <strong style="color:var(--text-primary)">RL-based autonomous routing</strong>, <strong style="color:var(--text-primary)">quantum-secured links (QKD + PQC)</strong>, and <strong style="color:var(--text-primary)">hybrid optical/RF communications</strong> across a 241-node, 5-tier interplanetary network.</div></div><div class="pres-grid-4" style="margin-bottom:16px"><div class="pres-stat-card" style="border-color:rgba(63,185,80,0.2)"><div class="pres-stat-value" style="color:#3fb950">10&ndash;100&times;</div><div class="pres-stat-unit">Faster data</div></div><div class="pres-stat-card" style="border-color:rgba(0,212,255,0.2)"><div class="pres-stat-value" style="color:#00d4ff">&gt;95%</div><div class="pres-stat-unit">Availability</div></div><div class="pres-stat-card" style="border-color:rgba(124,92,247,0.2)"><div class="pres-stat-value" style="color:#7c5cf7">149</div><div class="pres-stat-unit">Unit tests</div></div><div class="pres-stat-card" style="border-color:rgba(255,107,53,0.2)"><div class="pres-stat-value" style="color:#ff6b35">241</div><div class="pres-stat-unit">Network nodes</div></div></div><div style="background:rgba(var(--accent-rgb),0.06);border:1px solid rgba(var(--accent-rgb),0.2);border-radius:var(--radius-lg);padding:14px 20px;margin-bottom:16px"><div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--accent);margin-bottom:6px">EduQual Level 6 &mdash; Topic 59</div><div style="font-size:0.85rem;color:var(--text-primary);line-height:1.5;font-weight:600">Building Interplanetary Communication Network with Delay-Tolerant Networking, Quantum Communication, and Space-Based Infrastructure for Mars Mission Support</div></div></div><div class="pres-hero-links" style="margin-top:12px"><a href="https://matx104.github.io/AETHERIX/" target="_blank" class="pres-link">Live Showcase</a><a href="https://github.com/matx104/AETHERIX" target="_blank" class="pres-link">GitHub Repository</a><a href="mailto:muhammad.atx@gmail.com" class="pres-link">Contact</a></div></div>',
          speakerNotes: 'Summarize the problem and solution clearly. Re-read the exam topic verbatim. Point to the numbers. Offer to show live demos or answer questions. Thank the examiners. (1 minute)'
        },
        {
          title: 'Thank You',
          content: '<div class="pres-conclusion"><div class="pres-hero-title" style="font-size:3.5rem;margin-bottom:12px">Thank You</div><div class="pres-divider"></div><h2 style="text-align:center;margin-bottom:28px;color:var(--text-secondary)">Questions?</h2><div class="pres-grid-4" style="margin-bottom:32px"><div class="pres-stat-card" style="border-color:rgba(63,185,80,0.2)"><div class="pres-stat-value" style="color:#3fb950">10-100&times;</div><div class="pres-stat-unit">Faster data rates</div></div><div class="pres-stat-card" style="border-color:rgba(0,212,255,0.2)"><div class="pres-stat-value" style="color:#00d4ff">&gt;95%</div><div class="pres-stat-unit">Availability</div></div><div class="pres-stat-card" style="border-color:rgba(124,92,247,0.2)"><div class="pres-stat-value" style="color:#7c5cf7">RL</div><div class="pres-stat-unit">AI Routing</div></div><div class="pres-stat-card" style="border-color:rgba(255,107,53,0.2)"><div class="pres-stat-value" style="color:#ff6b35">QKD</div><div class="pres-stat-unit">Quantum Secure</div></div></div><div class="pres-contact"><div><strong>Muhammad Abdullah Tariq</strong></div><div>EduQual Level 6 &middot; Topic 59</div><div style="margin-top:14px"><a href="mailto:muhammad.atx@gmail.com" class="pres-link">muhammad.atx@gmail.com</a></div><div style="margin-top:8px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap"><a href="https://matx104.github.io/AETHERIX/" target="_blank" class="pres-link">Live Showcase</a><a href="https://github.com/matx104/AETHERIX" target="_blank" class="pres-link">GitHub Repository</a><a href="https://www.linkedin.com/in/matx104" target="_blank" class="pres-link">LinkedIn</a><a href="https://matx104.com.pk" target="_blank" class="pres-link">Portfolio</a></div></div></div>',
          speakerNotes: 'Summarize the four key numbers: 10-100x faster, >95% availability, AI-powered routing, quantum-secure. Invite questions confidently. Make eye contact. Point to the live demo link. Thank the audience. Wait for first question. (30 seconds)'
        },
      ];
    },

    slideLinks: {
      'Introduction': [
        { type: 'ref', label: 'RFC 4838', url: 'https://www.rfc-editor.org/rfc/rfc4838' }
      ],
      'What is AETHERIX': [
        { type: 'learn', label: 'What is DTN', hash: 'what-is-dtn' },
        { type: 'learn', label: 'Why It Matters', hash: 'why-it-matters' }
      ],
      'The Distance': [
        { type: 'learn', label: 'Journey to Mars', hash: 'journey-to-mars' }
      ],
      'The Answer': [
        { type: 'learn', label: 'What is DTN', hash: 'what-is-dtn' },
        { type: 'learn', label: 'How It Works', hash: 'how-it-works' }
      ],
      'System Architecture': [
        { type: 'learn', label: 'How It Works', hash: 'how-it-works' },
        { type: 'ref', label: 'CCSDS 734.2-B-1', url: 'https://public.ccsds.org/Pubs/734x2b1.pdf' }
      ],
      'BPv7 Deep Dive': [
        { type: 'learn', label: 'DTN Protocols', hash: 'what-is-dtn' },
        { type: 'demo', label: 'Bundle Demo', hash: 'bundle' },
        { type: 'ref', label: 'RFC 9171', url: 'https://www.rfc-editor.org/rfc/rfc9171' }
      ],
      'DTN Store-and-Forward': [
        { type: 'learn', label: 'DTN Protocols', hash: 'what-is-dtn' },
        { type: 'demo', label: 'DTN Engine', hash: 'dtn-engine' },
        { type: 'ref', label: 'RFC 5326', url: 'https://www.rfc-editor.org/rfc/rfc5326' }
      ],
      'Network Topology': [
        { type: 'learn', label: 'The Network', hash: 'the-network' },
        { type: 'demo', label: 'Dashboard', hash: 'dashboard' }
      ],
      '5-Tier Network Diagram': [
        { type: 'learn', label: 'The Network', hash: 'the-network' },
        { type: 'ref', label: 'CCSDS 734.2-B-1', url: 'https://public.ccsds.org/Pubs/734x2b1.pdf' }
      ],
      'Optical Communications': [
        { type: 'learn', label: 'Optical Comms', hash: 'optical-comms' },
        { type: 'demo', label: 'Link Budget', hash: 'link-budget' },
        { type: 'demo', label: 'RF Budget', hash: 'rf-budget' },
        { type: 'ref', label: 'CCSDS 141.0-B-1', url: 'https://public.ccsds.org/Pubs/141x0b1.pdf' }
      ],
      'Earth-Mars Journey': [
        { type: 'learn', label: 'Journey to Mars', hash: 'journey-to-mars' },
        { type: 'demo', label: 'Mission', hash: 'mission' }
      ],
      'RL Routing': [
        { type: 'learn', label: 'RL Routing', hash: 'reinforcement-learning' },
        { type: 'demo', label: 'Routing Demo', hash: 'routing' },
        { type: 'ref', label: 'Sutton & Barto', url: 'http://incompleteideas.net/book/the-book.html' }
      ],
      'Quantum Security': [
        { type: 'learn', label: 'Space Security', hash: 'space-security' },
        { type: 'learn', label: 'QKD Science', hash: 'qkd-science' },
        { type: 'demo', label: 'QKD Demo', hash: 'qkd' },
        { type: 'ref', label: 'NIST FIPS 203', url: 'https://csrc.nist.gov/pubs/fips/203/final' }
      ],
      'Orbital Mechanics': [
        { type: 'learn', label: 'Journey to Mars', hash: 'journey-to-mars' },
        { type: 'demo', label: 'Orbital Demo', hash: 'orbital' }
      ],
      'End-to-End Mission': [
        { type: 'demo', label: 'Mission', hash: 'mission' },
        { type: 'demo', label: 'Simulation', hash: 'simulation' }
      ],
      'Data Flow Diagram': [
        { type: 'learn', label: 'DTN Protocols', hash: 'what-is-dtn' },
        { type: 'demo', label: 'DTN Engine', hash: 'dtn-engine' },
        { type: 'ref', label: 'RFC 7242', url: 'https://www.rfc-editor.org/rfc/rfc7242' }
      ],
      'Performance': [
        { type: 'demo', label: 'Dashboard', hash: 'dashboard' }
      ],
      'Implementation': [
        { type: 'learn', label: 'Standards', hash: 'deep-space-standards' },
        { type: 'demo', label: 'Dashboard', hash: 'dashboard' },
        { type: 'ref', label: 'CCSDS 735.1-B-1', url: 'https://public.ccsds.org/Pubs/735x1b1.pdf' }
      ],
      'Roadmap': [
        { type: 'learn', label: 'Standards', hash: 'deep-space-standards' },
        { type: 'ref', label: 'CCSDS 142.0-B-2', url: 'https://public.ccsds.org/Pubs/142x0b2.pdf' }
      ],
      'Thank You': [
        { type: 'demo', label: 'Dashboard', hash: 'dashboard' },
        { type: 'ref', label: 'LinkedIn', url: 'https://www.linkedin.com/in/matx104' },
        { type: 'ref', label: 'Portfolio', url: 'https://matx104.com.pk' }
      ],
      'Conclusion': [
        { type: 'demo', label: 'Dashboard', hash: 'dashboard' },
        { type: 'ref', label: 'GitHub', url: 'https://github.com/matx104/AETHERIX' }
      ]
    },

    linksHtml(links) {
      if (!links || !links.length) return '';
      return '<div class="pres-slide-links">' + links.map(l => {
        if (l.type === 'ref') {
          return '<a href="' + l.url + '" target="_blank" rel="noopener" class="pres-link-btn pres-link-ref" title="' + l.label + '">&#128196; ' + l.label + '</a>';
        } else if (l.type === 'demo') {
          return '<a href="#' + l.hash + '" class="pres-link-btn pres-link-demo" data-nav="' + l.hash + '" title="Demo: ' + l.label + '">&#9654; ' + l.label + '</a>';
        } else {
          return '<a href="#' + l.hash + '" class="pres-link-btn pres-link-learn" data-nav="' + l.hash + '" title="Learn: ' + l.label + '">&#128218; ' + l.label + '</a>';
        }
      }).join('') + '</div>';
    },

    render() {
      const slide = this.slides[this.currentSlide];
      const el = $('pres-slide-content');
      if (!el) return;
      const links = this.slideLinks[slide.title] || [];
      el.innerHTML = '<div class="pres-slide-title">' + slide.title + '</div>' + (slide.subtitle ? '<div class="pres-slide-subtitle">' + slide.subtitle + '</div>' : '') + '<div class="pres-slide-body">' + slide.content + '</div>' + this.linksHtml(links);
      renderMermaidInContainer(el);
      el.querySelectorAll('[data-nav]').forEach(a => {
        a.addEventListener('click', (e) => {
          e.preventDefault();
          this.exit();
          setTimeout(() => { window.location.hash = '#' + a.dataset.nav; }, 150);
        });
      });
      $('pres-counter').textContent = (this.currentSlide + 1) + ' / ' + this.slides.length;
      $('pres-progress').style.width = ((this.currentSlide + 1) / this.slides.length * 100) + '%';
      if (this.notesVisible) {
        $('pres-speaker-notes').innerHTML = '<div class="pres-notes-title">Speaker Notes \u2014 Slide ' + (this.currentSlide + 1) + '</div><div class="pres-notes-text">' + slide.speakerNotes + '</div>';
      }
      window.location.hash = '#presentation/' + (this.currentSlide + 1);
    },

    next() { if (this.currentSlide < this.slides.length - 1) { this.currentSlide++; this.render(); } },
    prev() { if (this.currentSlide > 0) { this.currentSlide--; this.render(); } },
    goTo(index) { this.currentSlide = Math.max(0, Math.min(index, this.slides.length - 1)); this.render(); },

    startTimer() {
      if (this.timerInterval) clearInterval(this.timerInterval);
      this.timerSeconds = 0;
      this.timerInterval = setInterval(() => {
        this.timerSeconds++;
        const m = Math.floor(this.timerSeconds / 60).toString().padStart(2, '0');
        const s = (this.timerSeconds % 60).toString().padStart(2, '0');
        $('pres-timer').textContent = m + ':' + s;
      }, 1000);
    },

    toggleFullscreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
      }
    },

    toggleNotes() {
      this.notesVisible = !this.notesVisible;
      $('pres-speaker-notes').style.display = this.notesVisible ? 'block' : 'none';
      if (this.notesVisible) this.render();
    },

    toggleShortcuts() {
      this.shortcutsVisible = !this.shortcutsVisible;
      $('pres-shortcuts').style.display = this.shortcutsVisible ? 'block' : 'none';
    },

    exit() {
      document.body.classList.remove('pres-active');
      if (this.timerInterval) clearInterval(this.timerInterval);
      window.location.hash = '#welcome';
    },

    bindEvents() {
      document.addEventListener('keydown', (e) => {
        if (!document.body.classList.contains('pres-active')) return;
        const target = e.target;
        if (target.tagName === 'INPUT' || target.tagName === 'SELECT' || target.tagName === 'TEXTAREA') return;
        switch (e.key) {
          case 'ArrowRight': case ' ': case 'Enter': e.preventDefault(); this.next(); break;
          case 'ArrowLeft': case 'Backspace': e.preventDefault(); this.prev(); break;
          case 'Home': e.preventDefault(); this.goTo(0); break;
          case 'End': e.preventDefault(); this.goTo(this.slides.length - 1); break;
          case 'f': case 'F': e.preventDefault(); this.toggleFullscreen(); break;
          case 'Escape': e.preventDefault(); this.exit(); break;
          case 't': case 'T': e.preventDefault(); this.timerVisible = !this.timerVisible; $('pres-timer').style.display = this.timerVisible ? 'inline' : 'none'; break;
          case 's': case 'S': e.preventDefault(); this.toggleNotes(); break;
          case '?': e.preventDefault(); this.toggleShortcuts(); break;
        }
      });
      const prev = $('pres-prev');
      const next = $('pres-next');
      const fs = $('pres-fullscreen');
      const exit = $('pres-exit');
      if (prev) prev.addEventListener('click', () => this.prev());
      if (next) next.addEventListener('click', () => this.next());
      if (fs) fs.addEventListener('click', () => this.toggleFullscreen());
      if (exit) exit.addEventListener('click', () => this.exit());
    }
  };

  function initSliders() {
    const bs = $('rt-buffer');
    if (bs) bs.addEventListener('input', e => { $('rt-buffer-val').textContent = e.target.value + '%'; });
    const es = $('qkd-error');
    if (es) es.addEventListener('input', e => { $('qkd-error-val').textContent = e.target.value + '%'; });
    const ltpLoss = $('ltp-loss');
    if (ltpLoss) ltpLoss.addEventListener('input', e => { $('ltp-loss-val').textContent = e.target.value + '%'; });
    const polBuffer = $('pol-buffer');
    if (polBuffer) polBuffer.addEventListener('input', e => { $('pol-buffer-val').textContent = e.target.value + '%'; });
    const polQuality = $('pol-quality');
    if (polQuality) polQuality.addEventListener('input', e => { $('pol-quality-val').textContent = e.target.value + '%'; });
  }

  let dashboardInitialized = false;
  function ensureDashboard() {
    if (dashboardInitialized) return;
    dashboardInitialized = true;
    initDashboard();
    setTimeout(() => initTopology(), 100);
  }

  function init() {
    initCosmos();
    study.init();
    qkd.init();
    bundle.renderList();
    dtnEngine.loadPolicies();
    initSliders();
    initTicker();
    window.addEventListener('resize', () => { resizeCosmos(); });
  }

  return { init, initCosmos, ensureDashboard, linkBudget, routing, qkd, orbital, bundle, mission, dtnEngine, rfBudget, simulation, study, presentation };
})();

document.addEventListener('DOMContentLoaded', () => {
  ThemeManager.init();
  DropdownManager.init();
  Router.init();
  App.init();
});
