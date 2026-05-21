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
      if (slideNum >= 1 && slideNum <= 13) App.presentation.goTo(slideNum - 1);
    }
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
      this.currentSlide = hashSlide ? Math.min(parseInt(hashSlide[1]) - 1, 12) : 0;
      this.render();
      this.startTimer();
    },

    buildSlides() {
      return [
        {
          title: 'AETHERIX',
          subtitle: 'Autonomous Extraterrestrial High-throughput Enhancing Routing and Inter-planetary eXchange',
          content: '<div class="pres-hero"><div class="pres-hero-title">AETHERIX</div><div class="pres-hero-sub">Building an Interplanetary Communication Network for Mars Mission Support</div><div class="pres-hero-meta"><div class="pres-meta-item">Student: Muhammad Abdullah Tariq</div><div class="pres-meta-item">EduQual Level 6 \u2014 Topic 59</div><div class="pres-meta-item">January 2026</div></div><div class="pres-hero-links"><a href="https://matx104.github.io/AETHERIX/" target="_blank" class="pres-link">matx104.github.io/AETHERIX</a><a href="https://github.com/matx104/AETHERIX" target="_blank" class="pres-link">github.com/matx104/AETHERIX</a></div></div>',
          speakerNotes: 'Introduce yourself confidently. Spell out AETHERIX acronym once. State the core mission: building a communication network from Earth to Mars. (30 seconds)'
        },
        {
          title: 'The Challenge',
          content: '<h2>Why Space Communication is Hard</h2><div class="pres-grid-2"><div class="pres-card"><div class="pres-card-title">Extreme Challenges</div><table class="pres-table"><tr><td><strong>Distance</strong></td><td>54.6M \u2014 401M km (7\u00d7 range)</td></tr><tr><td><strong>One-way delay</strong></td><td>3 \u2014 22 minutes</td></tr><tr><td><strong>Bandwidth</strong></td><td>0.5 \u2014 6 Mbps (RF only)</td></tr><tr><td><strong>Blackouts</strong></td><td>2-week solar conjunction</td></tr><tr><td><strong>Environment</strong></td><td>Radiation, power limits</td></tr></table></div><div class="pres-card pres-card-danger"><div class="pres-card-title">Why TCP/IP Fails</div><table class="pres-table"><tr><td>Low latency (&lt;1s RTT)</td><td>6 \u2014 44 min RTT</td></tr><tr><td>Continuous connectivity</td><td>Scheduled contacts</td></tr><tr><td>End-to-end connection</td><td>No persistent path</td></tr><tr><td>Symmetric bandwidth</td><td>Highly asymmetric</td></tr></table><div class="pres-callout">&ldquo;We need a fundamentally different networking paradigm.&rdquo;</div></div></div>',
          speakerNotes: 'Distance varies 7\u00d7. Light-time delay makes TCP impossible. Current systems bandwidth-limited. Solar conjunction causes 2-week blackout. (1 minute)'
        },
        {
          title: 'Solution Overview',
          content: '<h2>DTN + AI Routing + Quantum Security</h2><div class="pres-grid-2"><div class="pres-card"><div class="pres-card-title">AETHERIX Product Suite</div><table class="pres-table"><tr><td><strong>Relay</strong></td><td>DTN + AI routing layer</td></tr><tr><td><strong>Quantum</strong></td><td>QKD security stack</td></tr><tr><td><strong>Ops</strong></td><td>Mission control dashboard</td></tr><tr><td><strong>Sim</strong></td><td>ns-3/OMNeT++ simulation</td></tr><tr><td><strong>Forge</strong></td><td>Policy & automation</td></tr></table></div><div class="pres-card pres-card-accent"><div class="pres-card-title">Four Key Innovations</div><ol class="pres-list"><li><strong>Bundle Protocol v7</strong> \u2014 Store-and-forward DTN</li><li><strong>RL Routing</strong> \u2014 Replaces static Contact Graph Routing</li><li><strong>QKD</strong> \u2014 Information-theoretically secure</li><li><strong>Hybrid Optical/RF</strong> \u2014 10-100\u00d7 faster with backup</li></ol></div></div><div class="pres-demo-badge">Live Demo: matx104.github.io/AETHERIX</div>',
          speakerNotes: 'Four integrated innovations: BPv7 for delay tolerance, RL for adaptive routing, QKD for security, hybrid optical/RF for performance. Mention live demo. (1.5 minutes)'
        },
        {
          title: 'DTN & Bundle Protocol',
          content: '<h2>The Foundation \u2014 RFC 9171</h2><div class="pres-card pres-card-accent"><div class="pres-card-title">Protocol Stack</div><div class="pres-stack"><div class="pres-stack-layer" style="background:rgba(0,212,255,0.15);border-color:#00d4ff">Application Layer</div><div class="pres-stack-layer" style="background:rgba(124,92,247,0.15);border-color:#7c5cf7">Bundle Protocol v7 \u2014 Store-and-Forward \u00b7 Custody Transfer \u00b7 Priority P0-P4</div><div class="pres-stack-layer" style="background:rgba(255,107,53,0.15);border-color:#ff6b35">Convergence Layers \u2014 LTP (deep space) \u00b7 TCPCL (Earth) \u00b7 UDP-CL (optical ISL)</div><div class="pres-stack-layer" style="background:rgba(63,185,80,0.15);border-color:#3fb950">Physical \u2014 Optical (1550nm) / RF (Ka/X-band)</div></div></div><div class="pres-grid-2" style="margin-top:16px"><div class="pres-card"><div class="pres-card-title">Store-and-Forward</div><ol class="pres-list"><li>Source creates bundle</li><li>Forward to next hop when link available</li><li>Store locally during outages</li><li>Custody transfer at each hop</li><li>No end-to-end connection needed</li></ol></div><div class="pres-card"><div class="pres-card-title">Standards</div><ul class="pres-list"><li><strong>CCSDS 734.2-B-1</strong> \u2014 DTN Architecture</li><li><strong>CCSDS 735.1-B-1</strong> \u2014 Bundle Protocol</li><li><strong>RFC 9171</strong> \u2014 BPv7 Specification</li><li><strong>RFC 5326</strong> \u2014 LTP</li></ul></div></div>',
          speakerNotes: 'BPv7 works like postal service, not phone call. Custody transfer shifts responsibility hop-by-hop. Three convergence layers for different link types. Priority P0-P4. (2 minutes)'
        },
        {
          title: 'Network Topology',
          content: '<h2>Five-Tier Architecture \u2014 232 Nodes</h2><div class="pres-tiers"><div class="pres-tier"><div class="pres-tier-badge" style="background:#00d4ff">T1</div><div class="pres-tier-content"><strong>Earth Ground (6)</strong> \u2014 DSN: Goldstone, Madrid, Canberra + MOC, NOC, SOC</div></div><div class="pres-tier"><div class="pres-tier-badge" style="background:#7c5cf7">T2</div><div class="pres-tier-content"><strong>Earth Orbital (51)</strong> \u2014 3 GEO relays + 48 LEO laser constellation</div></div><div class="pres-tier"><div class="pres-tier-badge" style="background:#ff6b35">T3</div><div class="pres-tier-content"><strong>Deep Space (4)</strong> \u2014 ES-L4, ES-L5 Lagrange relays + 2 transfer orbit sats</div></div><div class="pres-tier"><div class="pres-tier-badge" style="background:#f85149">T4</div><div class="pres-tier-content"><strong>Mars Orbital (4)</strong> \u2014 2 areostationary + 2 polar orbiters</div></div><div class="pres-tier"><div class="pres-tier-badge" style="background:#d29922">T5</div><div class="pres-tier-content"><strong>Mars Surface (167)</strong> \u2014 Bases, rovers, drones, sensors</div></div></div><div class="pres-callout pres-callout-accent" style="margin-top:16px">Multiple redundant paths \u2014 No single point of failure \u2014 Lagrange relays for conjunction coverage</div>',
          speakerNotes: '5 tiers, 232 nodes. Walk through each tier. Emphasize Lagrange relays for conjunction coverage. Areostationary at 17,032 km. Redundancy is key design principle. (2 minutes)'
        },
        {
          title: 'Optical Link Budget',
          content: '<h2>LIVE DEMO \u2014 Link Budget Calculator</h2><div class="pres-grid-3"><div class="pres-stat-card" style="border-color:#3fb950"><div class="pres-stat-value" style="color:#3fb950">100-200</div><div class="pres-stat-unit">Mbps at min dist</div><div class="pres-stat-sub">54.6M km \u00b7 3 min</div></div><div class="pres-stat-card" style="border-color:#00d4ff"><div class="pres-stat-value" style="color:#00d4ff">10-20</div><div class="pres-stat-unit">Mbps average</div><div class="pres-stat-sub">225M km \u00b7 12.5 min</div></div><div class="pres-stat-card" style="border-color:#f85149"><div class="pres-stat-value" style="color:#f85149">2-5</div><div class="pres-stat-unit">Mbps at max dist</div><div class="pres-stat-sub">401M km \u00b7 22 min</div></div></div><div class="pres-grid-2" style="margin-top:16px"><div class="pres-card"><div class="pres-card-title">Key Equations</div><div class="pres-code">FSPL = 20 \u00d7 log\u2081\u2080(4\u03c0d/\u03bb)<br>Gain = 10 \u00d7 log\u2081\u2080(\u03b7 \u00d7 (\u03c0D/\u03bb)\u00b2)<br>Pr = Pt + Gt + Gr \u2212 FSPL \u2212 Latm \u2212 Lpoint</div></div><div class="pres-card"><div class="pres-card-title">Configuration</div><table class="pres-table"><tr><td>Tx Power</td><td>5W (37 dBm)</td></tr><tr><td>Tx Aperture</td><td>22 cm</td></tr><tr><td>Rx Aperture</td><td>1.0 m</td></tr><tr><td>Wavelength</td><td>1550 nm</td></tr></table></div></div><div class="pres-comparison" style="margin-top:16px"><strong>vs Current RF:</strong> 10-100\u00d7 improvement (0.5-6 Mbps \u2192 2-200 Mbps)</div>',
          speakerNotes: 'RUN LIVE DEMO. Show 3 distance scenarios. Highlight 10-100\u00d7 improvement. FSPL at avg distance: -365 dB. Why 1550 nm: telecom heritage, eye-safe, atmospheric window. (2 minutes)'
        },
        {
          title: 'RL-Based Routing',
          content: '<h2>AI Innovation \u2014 Replacing Static CGR</h2><div class="pres-grid-2"><div class="pres-card pres-card-danger"><div class="pres-card-title">CGR Limitations</div><ul class="pres-list"><li>Requires pre-computed schedules</li><li>Cannot adapt to unexpected events</li><li>Manual updates needed</li><li>Single-objective only</li></ul></div><div class="pres-card pres-card-accent"><div class="pres-card-title">RL Agent Design</div><div style="margin-bottom:8px"><strong>State:</strong> node, neighbors, link quality, buffer, priority, deadline</div><div style="margin-bottom:8px"><strong>Actions:</strong> Forward \u00b7 Store \u00b7 Drop \u00b7 Split</div><div class="pres-code" style="margin-top:8px">R = \u03b1(delivery) \u2212 \u03b2(delay) \u2212 \u03b3(hops)<br>&nbsp;&nbsp;\u2212 \u03b4(drops) \u2212 \u03b5(energy)</div><table class="pres-table" style="margin-top:8px"><tr><td>\u03b1=1.0</td><td>\u03b2=0.001</td><td>\u03b3=0.1</td><td>\u03b4=10.0</td><td>\u03b5=0.01</td></tr></table></div></div><div class="pres-grid-3" style="margin-top:16px"><div class="pres-stat-card" style="border-color:#3fb950"><div class="pres-stat-value" style="color:#3fb950">+20-40%</div><div class="pres-stat-unit">Faster delivery</div></div><div class="pres-stat-card" style="border-color:#00d4ff"><div class="pres-stat-value" style="color:#00d4ff">3600\u00d7</div><div class="pres-stat-unit">Faster failure recovery</div></div><div class="pres-stat-card" style="border-color:#7c5cf7"><div class="pres-stat-value" style="color:#7c5cf7">MADQN</div><div class="pres-stat-unit">Multi-agent training</div></div></div>',
          speakerNotes: 'CGR is static, manual, single-objective. RL agent learns from experience. 8 state variables, 4 actions. Reward balances delivery vs delay vs energy. MADQN + federated learning. (2 minutes)'
        },
        {
          title: 'Quantum Security',
          content: '<h2>Future-Proof Protection \u2014 QKD</h2><div class="pres-grid-2"><div class="pres-card pres-card-quantum"><div class="pres-card-title">BB84 Protocol</div><ol class="pres-list"><li>Alice sends qubits in random bases</li><li>Bob measures in random bases</li><li>Public basis comparison (~50% match)</li><li>QBER estimation</li><li><strong>QBER &lt; 11% \u2192 SECURE</strong></li><li>Privacy amplification \u2192 final key</li></ol></div><div class="pres-card"><div class="pres-card-title">Deployment Roadmap</div><table class="pres-table"><tr><td>Phase 1</td><td>Earth \u2194 LEO</td><td>BB84</td><td>1-10 kbps</td></tr><tr><td>Phase 2</td><td>Earth \u2194 GEO</td><td>BB84/E91</td><td>100-1000 bps</td></tr><tr><td>Phase 3</td><td>Earth \u2194 Mars</td><td>E91+Repeaters</td><td>1-10 bps</td></tr></table><div style="margin-top:12px"><strong>Quantum Repeaters at L4/L5:</strong><br>Entanglement swapping extends range across 225M km</div></div></div><div class="pres-grid-2" style="margin-top:16px"><div class="pres-callout pres-callout-quantum">Information-theoretically secure \u2014 based on laws of physics, not computational difficulty</div><div class="pres-card"><div class="pres-card-title">Post-Quantum Crypto</div><div><strong>Kyber</strong> \u2014 Key encapsulation<br><strong>Dilithium</strong> \u2014 Digital signatures<br>Complementary to QKD (defense in depth)</div></div></div>',
          speakerNotes: 'BB84: send, measure, sift, verify. QBER < 11% is the magic number. E91 uses entanglement. Quantum repeaters at Lagrange points. Post-quantum crypto as complement. (2 minutes)'
        },
        {
          title: 'Orbital Mechanics',
          content: '<h2>Contact Windows & Propagation</h2><div class="pres-grid-2"><div class="pres-card"><div class="pres-card-title">Mars Orbital Parameters</div><table class="pres-table"><tr><td>Semi-major axis</td><td>1.524 AU (227.9M km)</td></tr><tr><td>Synodic period</td><td>779.94 days</td></tr><tr><td>Min distance</td><td>54.6M km (3 min)</td></tr><tr><td>Max distance</td><td>401M km (22 min)</td></tr><tr><td>Areostationary</td><td>17,032 km altitude</td></tr></table></div><div class="pres-card"><div class="pres-card-title">Contact Windows</div><table class="pres-table"><tr><td>Optimal (opposition)</td><td>8-12 hrs/day</td><td>100-200 Mbps</td></tr><tr><td>Good</td><td>6-8 hrs/day</td><td>20-100 Mbps</td></tr><tr><td>Fair (quadrature)</td><td>2-4 hrs/day</td><td>5-20 Mbps</td></tr><tr><td>Blackout (conjunction)</td><td>0 hrs (direct)</td><td>Lagrange relay</td></tr></table></div></div><div class="pres-grid-2" style="margin-top:16px"><div class="pres-card"><div class="pres-card-title">Doppler Shift</div><div>Max relative velocity: <strong>~24 km/s</strong><br>Frequency shift at 1550nm: <strong>~15 GHz</strong><br>Real-time compensation required</div></div><div class="pres-card"><div class="pres-card-title">Conjunction Strategy</div><ol class="pres-list"><li>T-14 days: Pre-position critical uploads</li><li>T-7 days: Activate Lagrange relays</li><li>T-0 to T+14: Autonomous operations</li><li>T+14: Resume direct links</li></ol></div></div>',
          speakerNotes: 'Synodic period 780 days. Contact windows vary dramatically. Solar conjunction: 2-week blackout, Lagrange relays provide 50-70%. Doppler shift ~15 GHz. (1.5 minutes)'
        },
        {
          title: 'Mars Mission Scenario',
          content: '<h2>LIVE DEMO \u2014 End-to-End Mission</h2><div class="pres-card pres-card-accent"><div class="pres-card-title">Scenario: Perseverance \u2192 JPL MOC (500 MB, P2 Priority)</div><div class="pres-route-hops"><div class="pres-hop"><div class="pres-hop-num">1</div><div class="pres-hop-label">Rover<br><span>500 MB</span></div></div><div class="pres-hop-arrow">\u2192</div><div class="pres-hop"><div class="pres-hop-num">2</div><div class="pres-hop-label">UHF<br><span>Uplink</span></div></div><div class="pres-hop-arrow">\u2192</div><div class="pres-hop"><div class="pres-hop-num">3</div><div class="pres-hop-label">MRS-Alpha<br><span>Areostat</span></div></div><div class="pres-hop-arrow">\u2192</div><div class="pres-hop"><div class="pres-hop-num">4</div><div class="pres-hop-label">MRS-Polar<br><span>Optical ISL</span></div></div><div class="pres-hop-arrow">\u2192</div><div class="pres-hop"><div class="pres-hop-num">5</div><div class="pres-hop-label">Deep Space<br><span>1550nm</span></div></div><div class="pres-hop-arrow">\u2192</div><div class="pres-hop"><div class="pres-hop-num">6</div><div class="pres-hop-label">LEO Mesh<br><span>12.5 min</span></div></div><div class="pres-hop-arrow">\u2192</div><div class="pres-hop"><div class="pres-hop-num">7</div><div class="pres-hop-label">DSN \u2192 MOC<br><span>Delivered \u2713</span></div></div></div></div><div class="pres-grid-4" style="margin-top:16px"><div class="pres-stat-card" style="border-color:#00d4ff"><div class="pres-stat-value" style="color:#00d4ff">~13 min</div><div class="pres-stat-unit">Total time</div></div><div class="pres-stat-card" style="border-color:#3fb950"><div class="pres-stat-value" style="color:#3fb950">&lt;5%</div><div class="pres-stat-unit">DTN overhead</div></div><div class="pres-stat-card" style="border-color:#ff6b35"><div class="pres-stat-value" style="color:#ff6b35">7</div><div class="pres-stat-unit">Hops</div></div><div class="pres-stat-card" style="border-color:#7c5cf7"><div class="pres-stat-value" style="color:#7c5cf7">98.7%</div><div class="pres-stat-unit">Reliability</div></div></div>',
          speakerNotes: '500 MB from Perseverance to JPL. 7 hops in ~13 min (vs 12.5 min light-time). DTN overhead <5%. Key point: if link drops, bundle is NOT lost. (2 minutes)'
        },
        {
          title: 'Performance Comparison',
          content: '<h2>AETHERIX vs Current Mars Communication</h2><div class="pres-table-wide"><table class="pres-table"><thead><tr><th>Metric</th><th>Current (MRO)</th><th>AETHERIX</th><th>Improvement</th></tr></thead><tbody><tr><td><strong>Downlink</strong></td><td>0.5-6 Mbps</td><td>2-200 Mbps</td><td class="pres-highlight-good">10-100\u00d7</td></tr><tr><td><strong>Daily Data</strong></td><td>5-10 GB</td><td>50-100 GB</td><td class="pres-highlight-good">10-20\u00d7</td></tr><tr><td><strong>Availability</strong></td><td>60-75%</td><td>&gt;95%</td><td class="pres-highlight-good">+20-35%</td></tr><tr><td><strong>Routing</strong></td><td>Static (CGR)</td><td>RL-adaptive</td><td>Autonomous</td></tr><tr><td><strong>Security</strong></td><td>AES-256</td><td>QKD + PQC</td><td>Future-proof</td></tr><tr><td><strong>Scalability</strong></td><td>5-10 assets</td><td>232 nodes</td><td class="pres-highlight-good">10-100\u00d7</td></tr><tr><td><strong>Cost/MB</strong></td><td>$0.10</td><td>$0.01</td><td class="pres-highlight-good">10\u00d7</td></tr><tr><td><strong>Conjunction</strong></td><td>Complete blackout</td><td>50-70% via relays</td><td class="pres-highlight-good">+50-70%</td></tr></tbody></table></div><div class="pres-callout pres-callout-accent" style="margin-top:20px">10-100\u00d7 improvement in data throughput \u00b7 &gt;95% availability \u00b7 1/10th cost per megabyte</div>',
          speakerNotes: 'Hit numbers confidently. 10-100\u00d7 faster. >95% availability. $0.01 vs $0.10 per MB. Quantum-secure. 232 nodes vs 5-10 assets. (1 minute)'
        },
        {
          title: 'Standards & Roadmap',
          content: '<h2>Full Standards Compliance</h2><div class="pres-grid-2"><div class="pres-card"><div class="pres-card-title">CCSDS Standards</div><table class="pres-table"><tr><td><strong>734.2-B-1</strong></td><td>DTN Architecture</td></tr><tr><td><strong>735.1-B-1</strong></td><td>Bundle Protocol</td></tr><tr><td><strong>735.2-B-1</strong></td><td>Bundle Security</td></tr><tr><td><strong>141.0-B-1</strong></td><td>Optical Comms</td></tr><tr><td><strong>142.0-B-2</strong></td><td>Space Link IDs</td></tr><tr><td><strong>131.0-B-4</strong></td><td>Channel Coding</td></tr></table></div><div class="pres-card"><div class="pres-card-title">Development Roadmap</div><table class="pres-table"><tr><td>Phase 1-4</td><td>Topology \u00b7 Routing \u00b7 QKD \u00b7 Web</td><td style="color:#3fb950">\u2713 Complete</td></tr><tr><td>Phase 5</td><td>Simulation (ns-3/OMNeT++)</td><td>Planned</td></tr><tr><td>Phase 6</td><td>DQN \u00b7 ION-DTN \u00b7 Real ephemeris</td><td>Future</td></tr><tr><td>Phase 7</td><td>Hardware-in-loop \u00b7 Mission</td><td>Future</td></tr></table></div></div><div class="pres-card" style="margin-top:16px"><div class="pres-card-title">IETF Standards</div><div><strong>RFC 9171</strong> \u2014 Bundle Protocol v7 &nbsp;&nbsp; <strong>RFC 5326</strong> \u2014 LTP &nbsp;&nbsp; <strong>RFC 4838</strong> \u2014 DTN Architecture &nbsp;&nbsp; <strong>NIST FIPS 203/204</strong> \u2014 Post-Quantum</div></div>',
          speakerNotes: 'Full CCSDS + IETF compliance. Phases 1-4 complete. Next: ns-3 simulation, ION-DTN, DQN upgrade. Interoperability with DSN, LunaNet. (1 minute)'
        },
        {
          title: 'Conclusion',
          content: '<div class="pres-conclusion"><div class="pres-hero-title" style="font-size:3rem;margin-bottom:32px">Thank You</div><h2 style="text-align:center;margin-bottom:32px">Questions?</h2><div class="pres-grid-4" style="margin-bottom:32px"><div class="pres-stat-card" style="border-color:#3fb950"><div class="pres-stat-value" style="color:#3fb950">10-100\u00d7</div><div class="pres-stat-unit">Faster data rates</div></div><div class="pres-stat-card" style="border-color:#00d4ff"><div class="pres-stat-value" style="color:#00d4ff">&gt;95%</div><div class="pres-stat-unit">Availability</div></div><div class="pres-stat-card" style="border-color:#7c5cf7"><div class="pres-stat-value" style="color:#7c5cf7">RL</div><div class="pres-stat-unit">AI Routing</div></div><div class="pres-stat-card" style="border-color:#ff6b35"><div class="pres-stat-value" style="color:#ff6b35">QKD</div><div class="pres-stat-unit">Quantum Secure</div></div></div><div class="pres-contact"><div><strong>Muhammad Abdullah Tariq</strong></div><div>EduQual Level 6 \u00b7 Topic 59</div><div style="margin-top:12px"><a href="mailto:muhammad.atx@gmail.com" class="pres-link">muhammad.atx@gmail.com</a></div><div><a href="https://matx104.github.io/AETHERIX/" target="_blank" class="pres-link">matx104.github.io/AETHERIX</a></div><div><a href="https://github.com/matx104/AETHERIX" target="_blank" class="pres-link">github.com/matx104/AETHERIX</a></div></div></div>',
          speakerNotes: 'Summarize: 10-100\u00d7 faster, >95% availability, AI routing, quantum security. Invite questions confidently. Make eye contact. Wait for first question. (30 seconds)'
        }
      ];
    },

    render() {
      const slide = this.slides[this.currentSlide];
      const el = $('pres-slide-content');
      if (!el) return;
      el.innerHTML = '<div class="pres-slide-title">' + slide.title + '</div>' + (slide.subtitle ? '<div class="pres-slide-subtitle">' + slide.subtitle + '</div>' : '') + '<div class="pres-slide-body">' + slide.content + '</div>';
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
