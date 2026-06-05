window.QuizEngine = (function () {
  var TOPIC_LABELS = {
    dtn_protocols: "DTN Protocols",
    quantum_comms: "Quantum Communications",
    space_infrastructure: "Space Infrastructure",
    orbital_mechanics: "Orbital Mechanics",
    radiation_hardening: "Radiation Hardening",
    data_prioritization: "Data Prioritization",
    standards: "Standards & RFCs",
    aetherix_specific: "AETHERIX Platform",
  };

  var TOPIC_ICONS = {
    dtn_protocols: "\u{1F310}",
    quantum_comms: "\u{269B}",
    space_infrastructure: "\u{1F680}",
    orbital_mechanics: "\u{1FA90}",
    radiation_hardening: "\u{2622}",
    data_prioritization: "\u{1F4CA}",
    standards: "\u{1F4D1}",
    aetherix_specific: "\u{1F48E}",
  };

  var DIFFICULTY_LABELS = {
    foundational: { label: "Foundational", color: "#3fb950", xp: 10 },
    intermediate: { label: "Intermediate", color: "#00d4ff", xp: 20 },
    advanced: { label: "Advanced", color: "#ff8c00", xp: 35 },
    expert: { label: "Expert", color: "#f85149", xp: 50 },
  };

  var DIFFICULTY_ORDER = ["foundational", "intermediate", "advanced", "expert"];

  var STORAGE_WRONG = "aetherix_wrong_answers";
  var STORAGE_STATS = "aetherix_quiz_stats";
  var STORAGE_SM2 = "aetherix_sm2_data";
  var STORAGE_HISTORY = "aetherix_session_history";
  var STORAGE_STREAK = "aetherix_streak_data";

  var XP_PER_LEVEL = 500;
  var LEVEL_NAMES = [
    "Cadet", "Ensign", "Lieutenant", "Commander", "Captain",
    "Admiral", "Commodore", "Rear Admiral", "Vice Admiral", "Fleet Admiral",
  ];

  var bank = [];
  var mode = null;
  var subMode = null;
  var currentIndex = 0;
  var questions = [];
  var answers = [];
  var wrongAnswers = [];
  var timer = null;
  var timeRemaining = 0;
  var sessionStartTime = 0;
  var questionStartTime = 0;
  var flashcardPool = [];
  var quizCharts = {};
  var confettiPieces = [];
  var confettiAnimating = false;
  var streakCorrect = 0;
  var maxStreak = 0;
  var adaptiveDifficulty = null;
  var questionResults = [];

  function $(id) { return document.getElementById(id); }

  function show(el) { if (typeof el === "string") el = $(el); if (el) el.style.display = ""; }
  function hide(el) { if (typeof el === "string") el = $(el); if (el) el.style.display = "none"; }

  function hideAll() {
    ["quiz-welcome", "quiz-area", "quiz-progress", "quiz-results", "quiz-heatmap", "quiz-stats-detail", "quiz-confetti-canvas"].forEach(function (id) { hide(id); });
  }

  function formatTime(seconds) {
    var m = Math.floor(seconds / 60);
    var s = seconds % 60;
    return m + ":" + (s < 10 ? "0" : "") + s;
  }

  function formatTimeLong(ms) {
    var sec = Math.floor(ms / 1000);
    var m = Math.floor(sec / 60);
    var s = sec % 60;
    return m + "m " + s + "s";
  }

  function fisherYates(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = a[i]; a[i] = a[j]; a[j] = tmp;
    }
    return a;
  }

  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

  function todayKey() {
    var d = new Date();
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }

  function destroyQuizChart(id) {
    if (quizCharts[id]) { quizCharts[id].destroy(); delete quizCharts[id]; }
  }

  function destroyAllCharts() {
    Object.keys(quizCharts).forEach(destroyQuizChart);
  }

  var chartTheme = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: "#8892aa", font: { size: 11, family: "'Inter', sans-serif" }, padding: 14, usePointStyle: true, pointStyleWidth: 8 } },
      tooltip: { backgroundColor: "rgba(8,16,40,0.92)", borderColor: "rgba(60,100,180,0.2)", borderWidth: 1, titleColor: "#e4eaf5", bodyColor: "#8892aa", titleFont: { weight: "600" }, padding: 10, cornerRadius: 8 }
    },
    scales: {
      x: { grid: { color: "rgba(60,100,180,0.08)" }, ticks: { color: "#4a5270", font: { size: 10 } } },
      y: { grid: { color: "rgba(60,100,180,0.08)" }, ticks: { color: "#4a5270", font: { size: 10 } } }
    }
  };

  // --- STORAGE ---
  function loadWrongAnswers() {
    try { wrongAnswers = JSON.parse(localStorage.getItem(STORAGE_WRONG)) || []; }
    catch (e) { wrongAnswers = []; }
  }
  function saveWrongAnswers() {
    try { localStorage.setItem(STORAGE_WRONG, JSON.stringify(wrongAnswers)); } catch (e) {}
  }

  function loadStats() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_STATS)) || {
        sessions: 0, totalQuestions: 0, totalCorrect: 0, totalXp: 0, byTopic: {},
        bestStreak: 0, totalTimeMs: 0, sessionsByDay: {}
      };
    } catch (e) {
      return { sessions: 0, totalQuestions: 0, totalCorrect: 0, totalXp: 0, byTopic: {}, bestStreak: 0, totalTimeMs: 0, sessionsByDay: {} };
    }
  }
  function saveStats(s) { try { localStorage.setItem(STORAGE_STATS, JSON.stringify(s)); } catch (e) {} }

  function loadSM2() {
    try { return JSON.parse(localStorage.getItem(STORAGE_SM2)) || {}; }
    catch (e) { return {}; }
  }
  function saveSM2(data) { try { localStorage.setItem(STORAGE_SM2, JSON.stringify(data)); } catch (e) {} }

  function loadHistory() {
    try { return JSON.parse(localStorage.getItem(STORAGE_HISTORY)) || []; }
    catch (e) { return []; }
  }
  function saveHistory(h) { try { localStorage.setItem(STORAGE_HISTORY, JSON.stringify(h)); } catch (e) {} }

  function loadStreak() {
    try { return JSON.parse(localStorage.getItem(STORAGE_STREAK)) || { current: 0, best: 0, lastDate: null }; }
    catch (e) { return { current: 0, best: 0, lastDate: null }; }
  }
  function saveStreak(s) { try { localStorage.setItem(STORAGE_STREAK, JSON.stringify(s)); } catch (e) {} }

  // --- XP / LEVEL ---
  function getLevel(xp) { return Math.floor(xp / XP_PER_LEVEL) + 1; }
  function getLevelName(xp) {
    var lvl = getLevel(xp) - 1;
    return LEVEL_NAMES[Math.min(lvl, LEVEL_NAMES.length - 1)];
  }
  function getXpProgress(xp) { return (xp % XP_PER_LEVEL) / XP_PER_LEVEL * 100; }
  function getXpInLevel(xp) { return xp % XP_PER_LEVEL; }

  // --- SM-2 SPACED REPETITION ---
  function sm2Init() { return { interval: 1, repetition: 0, efactor: 2.5, nextReview: 0 }; }

  function sm2Update(data, quality) {
    var d = data || sm2Init();
    var q = clamp(quality, 0, 5);
    d.repetition += 1;
    if (q < 3) {
      d.repetition = 0;
      d.interval = 1;
    } else {
      if (d.repetition === 1) d.interval = 1;
      else if (d.repetition === 2) d.interval = 6;
      else d.interval = Math.round(d.interval * d.efactor);
    }
    d.efactor = clamp(d.efactor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)), 1.3, 2.5);
    d.nextReview = Date.now() + d.interval * 24 * 60 * 60 * 1000;
    return d;
  }

  function getDueCards(sm2Data, topic) {
    var now = Date.now();
    var due = [];
    bank.forEach(function (q) {
      if (topic && q.topic !== topic) return;
      var sd = sm2Data[q.id];
      if (!sd || sd.nextReview <= now) {
        due.push({ question: q, sm2: sd || sm2Init(), quality: sd ? 3 : 0 });
      }
    });
    return due;
  }

  // --- STREAK ---
  function updateStreak() {
    var streak = loadStreak();
    var today = todayKey();
    if (streak.lastDate === today) return streak;
    var yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    var yKey = yesterday.getFullYear() + "-" + String(yesterday.getMonth() + 1).padStart(2, "0") + "-" + String(yesterday.getDate()).padStart(2, "0");
    if (streak.lastDate === yKey) {
      streak.current += 1;
    } else if (streak.lastDate !== today) {
      streak.current = 1;
    }
    streak.lastDate = today;
    if (streak.current > streak.best) streak.best = streak.current;
    saveStreak(streak);
    return streak;
  }

  // --- ADAPTIVE DIFFICULTY ---
  function pickAdaptiveDifficulty(sessionAnswers) {
    if (sessionAnswers.length < 3) return null;
    var recent = sessionAnswers.slice(-5);
    var correct = recent.filter(function (a) { return a.correct; }).length;
    var ratio = correct / recent.length;
    if (ratio >= 0.8 && adaptiveDifficulty !== null) {
      var idx = DIFFICULTY_ORDER.indexOf(adaptiveDifficulty);
      if (idx < DIFFICULTY_ORDER.length - 1) adaptiveDifficulty = DIFFICULTY_ORDER[idx + 1];
    } else if (ratio <= 0.3 && adaptiveDifficulty !== null) {
      var idx2 = DIFFICULTY_ORDER.indexOf(adaptiveDifficulty);
      if (idx2 > 0) adaptiveDifficulty = DIFFICULTY_ORDER[idx2 - 1];
    } else if (adaptiveDifficulty === null) {
      adaptiveDifficulty = ratio >= 0.6 ? "intermediate" : "foundational";
    }
    return adaptiveDifficulty;
  }

  // --- FILTERING ---
  function getTopics() {
    var topics = {};
    bank.forEach(function (q) { if (q.topic) topics[q.topic] = (topics[q.topic] || 0) + 1; });
    return Object.keys(topics).sort();
  }

  function filterBank(topic, difficulty) {
    return bank.filter(function (q) {
      if (topic && q.topic !== topic) return false;
      if (difficulty && q.difficulty !== difficulty) return false;
      return true;
    });
  }

  // --- CONFETTI ---
  function launchConfetti() {
    var canvas = $("quiz-confetti-canvas");
    if (!canvas) return;
    canvas.style.display = "block";
    canvas.style.pointerEvents = "none";
    var ctx = canvas.getContext("2d");
    canvas.width = canvas.parentElement.offsetWidth || 800;
    canvas.height = canvas.parentElement.offsetHeight || 600;
    confettiPieces = [];
    var colors = ["#00d4ff", "#7c5cf7", "#3fb950", "#ff8c00", "#f85149", "#c84cff", "#2dd4bf", "#ff6b35"];
    for (var i = 0; i < 150; i++) {
      confettiPieces.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height - canvas.height,
        w: Math.random() * 8 + 4,
        h: Math.random() * 6 + 3,
        color: colors[Math.floor(Math.random() * colors.length)],
        vx: (Math.random() - 0.5) * 4,
        vy: Math.random() * 3 + 2,
        rotation: Math.random() * 360,
        rotationSpeed: (Math.random() - 0.5) * 10,
        opacity: 1,
      });
    }
    confettiAnimating = true;
    animateConfetti(ctx, canvas);
  }

  function animateConfetti(ctx, canvas) {
    if (!confettiAnimating) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    var alive = false;
    confettiPieces.forEach(function (p) {
      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.05;
      p.rotation += p.rotationSpeed;
      if (p.y > canvas.height + 20) p.opacity -= 0.02;
      if (p.opacity <= 0) return;
      alive = true;
      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate(p.rotation * Math.PI / 180);
      ctx.globalAlpha = clamp(p.opacity, 0, 1);
      ctx.fillStyle = p.color;
      ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
      ctx.restore();
    });
    if (alive) requestAnimationFrame(function () { animateConfetti(ctx, canvas); });
    else { confettiAnimating = false; canvas.style.display = "none"; }
  }

  // --- PROGRESS RING ---
  function renderProgressRing(pct, size, stroke, color, label) {
    var s = size || 80;
    var sw = stroke || 6;
    var r = (s - sw) / 2;
    var circ = 2 * Math.PI * r;
    var offset = circ - (pct / 100) * circ;
    return '<svg width="' + s + '" height="' + s + '" viewBox="0 0 ' + s + " " + s + '" style="transform:rotate(-90deg)">' +
      '<circle cx="' + s / 2 + '" cy="' + s / 2 + '" r="' + r + '" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="' + sw + '"/>' +
      '<circle cx="' + s / 2 + '" cy="' + s / 2 + '" r="' + r + '" fill="none" stroke="' + (color || "#00d4ff") + '" stroke-width="' + sw + '" stroke-dasharray="' + circ + '" stroke-dashoffset="' + offset + '" stroke-linecap="round" class="quiz-progress-ring"/>' +
      "</svg>" +
      '<div class="quiz-ring-label" style="margin-top:-' + (s / 2 + 10) + "px;text-align:center;position:relative\">" +
      '<div style="font-size:' + (s > 60 ? "1.4" : "1") + 'rem;font-weight:700;color:' + (color || "#00d4ff") + '">' + Math.round(pct) + "%</div>" +
      (label ? '<div style="font-size:0.7rem;color:var(--text-muted)">' + label + "</div>" : "") +
      "</div>";
  }

  // --- XP BAR ---
  function renderXpBar(xp) {
    var level = getLevel(xp);
    var name = getLevelName(xp);
    var progress = getXpProgress(xp);
    var inLevel = getXpInLevel(xp);
    return '<div class="quiz-xp-bar-container">' +
      '<div class="quiz-xp-level-badge">Lvl ' + level + " &mdash; " + name + "</div>" +
      '<div class="quiz-xp-bar-track">' +
      '<div class="quiz-xp-bar-fill" style="width:' + progress + '%"></div>' +
      "</div>" +
      '<div class="quiz-xp-text">' + inLevel + " / " + XP_PER_LEVEL + " XP</div>" +
      "</div>";
  }

  // --- STREAK BADGE ---
  function renderStreakBadge(streak) {
    if (!streak || streak.current < 1) return "";
    return '<div class="quiz-streak-badge">' +
      '<span class="quiz-streak-fire">\uD83D\uDD25</span>' +
      '<span class="quiz-streak-count">' + streak.current + '</span>' +
      '<span class="quiz-streak-label">' + (streak.current === 1 ? "day streak" : "day streak") + "</span>" +
      "</div>";
  }

  // --- POPULATE FILTERS ---
  function populateFilters() {
    var topicSelect = $("quiz-topic-filter");
    var diffSelect = $("quiz-difficulty-filter");
    if (topicSelect) {
      topicSelect.innerHTML = '<option value="">All Topics</option>';
      getTopics().forEach(function (t) {
        var opt = document.createElement("option");
        opt.value = t;
        opt.textContent = TOPIC_LABELS[t] || t;
        topicSelect.appendChild(opt);
      });
    }
    if (diffSelect) {
      diffSelect.innerHTML = '<option value="">All Difficulties</option>';
      DIFFICULTY_ORDER.forEach(function (d) {
        var opt = document.createElement("option");
        opt.value = d;
        opt.textContent = DIFFICULTY_LABELS[d].label;
        diffSelect.appendChild(opt);
      });
    }
  }

  function populateTopicSelect(id) {
    var el = $(id);
    if (!el) return;
    el.innerHTML = '<option value="">All Topics</option>';
    getTopics().forEach(function (t) {
      var opt = document.createElement("option");
      opt.value = t;
      opt.textContent = TOPIC_LABELS[t] || t;
      el.appendChild(opt);
    });
  }

  // --- MASTERY CALCULATION ---
  function getMasteryData() {
    var stats = loadStats();
    var sm2 = loadSM2();
    var mastery = {};
    getTopics().forEach(function (topic) {
      mastery[topic] = {};
      DIFFICULTY_ORDER.forEach(function (diff) {
        var key = topic + ":" + diff;
        var topicStats = stats.byTopic[topic];
        var total = topicStats ? topicStats[diff + "_total"] || 0 : 0;
        var correct = topicStats ? topicStats[diff + "_correct"] || 0 : 0;
        var sm2Count = 0;
        var sm2Mature = 0;
        bank.forEach(function (q) {
          if (q.topic !== topic || q.difficulty !== diff) return;
          sm2Count++;
          var sd = sm2[q.id];
          if (sd && sd.efactor >= 2.0 && sd.repetition >= 2) sm2Mature++;
        });
        var ratio = total > 0 ? correct / total : 0;
        var sm2Ratio = sm2Count > 0 ? sm2Mature / sm2Count : 0;
        mastery[topic][diff] = {
          total: total, correct: correct, ratio: ratio,
          sm2Count: sm2Count, sm2Mature: sm2Mature, sm2Ratio: sm2Ratio,
          score: Math.round((ratio * 0.6 + sm2Ratio * 0.4) * 100),
        };
      });
    });
    return mastery;
  }

  function masteryColor(score) {
    if (score >= 80) return "#3fb950";
    if (score >= 60) return "#2dd4bf";
    if (score >= 40) return "#ff8c00";
    if (score >= 20) return "#d29922";
    return "#f85149";
  }

  function masteryLabel(score) {
    if (score >= 80) return "Mastered";
    if (score >= 60) return "Proficient";
    if (score >= 40) return "Developing";
    if (score >= 20) return "Beginner";
    return "New";
  }

  // ========== RENDER WELCOME ==========
  function renderWelcome() {
    destroyAllCharts();
    hideAll();
    var stats = loadStats();
    loadWrongAnswers();
    var streak = updateStreak();
    var overallPct = stats.totalQuestions > 0 ? Math.round((stats.totalCorrect / stats.totalQuestions) * 100) : 0;
    var xp = stats.totalXp || 0;

    var el = $("quiz-welcome");
    if (!el) return;

    el.innerHTML =
      '<div class="quiz-welcome-hero">' +
        '<div class="quiz-welcome-top">' +
          '<div class="quiz-hero-left">' +
            '<h2 class="section-title" style="margin-bottom:0.25rem">Knowledge Assessment</h2>' +
            '<p style="color:var(--text-secondary);margin:0">Master DTN, quantum comms, orbital mechanics & more</p>' +
          "</div>" +
          '<div class="quiz-hero-right">' +
            renderStreakBadge(streak) +
            renderXpBar(xp) +
          "</div>" +
        "</div>" +
        '<div class="grid grid-4 quiz-stat-strip">' +
          '<div class="stat-card accent">' +
            '<div class="card-title"><span class="ct-dot"></span>Total Sessions</div>' +
            '<div class="card-value">' + stats.sessions + "</div>" +
          "</div>" +
          '<div class="stat-card quantum">' +
            '<div class="card-title"><span class="ct-dot"></span>Questions</div>' +
            '<div class="card-value">' + stats.totalQuestions + "</div>" +
          "</div>" +
          '<div class="stat-card success">' +
            '<div class="card-title"><span class="ct-dot"></span>Accuracy</div>' +
            '<div class="card-value" style="color:' + (overallPct >= 70 ? "#3fb950" : overallPct >= 40 ? "#ff8c00" : "#f85149") + '">' + overallPct + "%</div>" +
          "</div>" +
          '<div class="stat-card mars">' +
            '<div class="card-title"><span class="ct-dot"></span>Best Streak</div>' +
            '<div class="card-value">' + (stats.bestStreak || 0) + "</div>" +
          "</div>" +
        "</div>" +
      "</div>" +

      (wrongAnswers.length > 0
        ? '<div class="callout callout-warning" style="margin:1rem 0;display:flex;align-items:center;justify-content:space-between">' +
          '<div><strong>' + wrongAnswers.length + ' wrong answers saved</strong> &mdash; review them to improve your mastery</div>' +
          '<button class="btn btn-sm btn-mars" onclick="QuizEngine.reviewWrong()">Review Mistakes</button>' +
          "</div>"
        : "") +

      '<div class="quiz-mode-grid">' +
        renderModeCard("Practice", "\u{1F393}", "Learn at your own pace with instant feedback and explanations", "var(--accent)",
          '<div class="form-group"><label>Topic</label><select id="quiz-topic-filter" class="form-control"></select></div>' +
          '<div class="form-group"><label>Difficulty</label><select id="quiz-difficulty-filter" class="form-control"></select></div>' +
          '<div class="form-group"><label>Questions</label><select id="quiz-count" class="form-control"><option value="10">10</option><option value="20" selected>20</option><option value="30">30</option><option value="50">50</option></select></div>' +
          '<button class="btn btn-primary" onclick="QuizEngine.startPractice()" style="width:100%">Start Practice</button>'
        ) +
        renderModeCard("Timed Exam", "\u23F0", "Simulate a real assessment under time pressure", "var(--mars)",
          '<div class="form-group"><label>Topic</label><select id="exam-topic-filter" class="form-control"></select></div>' +
          '<div class="form-group"><label>Time</label><select id="exam-time" class="form-control"><option value="15">15 min</option><option value="30" selected>30 min</option><option value="45">45 min</option><option value="60">60 min</option></select></div>' +
          '<div class="form-group"><label>Questions</label><select id="exam-count" class="form-control"><option value="25">25</option><option value="50" selected>50</option><option value="75">75</option></select></div>' +
          '<button class="btn btn-mars" onclick="QuizEngine.startTimedExam()" style="width:100%">Start Exam</button>'
        ) +
        renderModeCard("Flashcards", "\u{1F4DA}", "Spaced repetition flashcards with SM-2 scheduling", "var(--quantum)",
          '<div class="form-group"><label>Topic</label><select id="flashcard-topic-filter" class="form-control"></select></div>' +
          '<div class="form-group" style="display:flex;align-items:center;gap:0.5rem"><input type="checkbox" id="flashcard-due-only" checked><label for="flashcard-due-only" style="margin:0">Due cards only</label></div>' +
          '<button class="btn btn-quantum" onclick="QuizEngine.startFlashcards()" style="width:100%">Start Flashcards</button>'
        ) +
        renderModeCard("Adaptive", "\u{1F9E0}", "Questions adjust to your skill level in real-time", "var(--nebula)",
          '<div class="form-group"><label>Topic</label><select id="adaptive-topic-filter" class="form-control"></select></div>' +
          '<div class="form-group"><label>Questions</label><select id="adaptive-count" class="form-control"><option value="20" selected>20</option><option value="30">30</option><option value="50">50</option></select></div>' +
          '<button class="btn btn-primary" onclick="QuizEngine.startAdaptive()" style="width:100%;background:linear-gradient(135deg,#c84cff,#7c5cf7)">Start Adaptive</button>'
        ) +
      "</div>" +

      '<div style="display:flex;gap:0.5rem;margin-top:1.5rem;flex-wrap:wrap">' +
        '<button class="btn btn-quantum" onclick="QuizEngine.showHeatmap()">Mastery Heatmap</button>' +
        '<button class="btn btn-primary" onclick="QuizEngine.showStatsDetail()">Performance Stats</button>' +
        '<button class="btn" onclick="QuizEngine.showQuickStart()">Quick Start (Mixed 20)</button>' +
      "</div>";

    show("quiz-welcome");
    populateFilters();
    populateTopicSelect("exam-topic-filter");
    populateTopicSelect("flashcard-topic-filter");
    populateTopicSelect("adaptive-topic-filter");
  }

  function renderModeCard(title, icon, desc, color, body) {
    return '<div class="card quiz-mode-card">' +
      '<div class="quiz-mode-header" style="color:' + color + '">' +
        '<span style="font-size:1.5rem">' + icon + "</span>" +
        "<h3>" + title + "</h3>" +
      "</div>" +
      '<p style="color:var(--text-secondary);font-size:0.9rem">' + desc + "</p>" +
      '<div class="quiz-mode-body">' + body + "</div>" +
    "</div>";
  }

  // ========== MASTERY HEATMAP ==========
  function renderHeatmap() {
    destroyAllCharts();
    hideAll();
    var mastery = getMasteryData();
    var el = $("quiz-heatmap");
    if (!el) return;

    var topicRows = "";
    getTopics().forEach(function (topic) {
      var cells = "";
      DIFFICULTY_ORDER.forEach(function (diff) {
        var m = mastery[topic][diff];
        var c = masteryColor(m.score);
        var lbl = masteryLabel(m.score);
        cells += '<div class="quiz-heatmap-cell" style="background:' + c + "22;border:1px solid " + c + "44;color:" + c + '" ' +
          'title="' + (TOPIC_LABELS[topic] || topic) + " / " + DIFFICULTY_LABELS[diff].label + ": " + m.score + '%">' +
          '<div class="quiz-heatmap-score">' + m.score + "%</div>" +
          '<div class="quiz-heatmap-label">' + lbl + "</div>" +
          "</div>";
      });

      var overallTopicScore = 0;
      var count = 0;
      DIFFICULTY_ORDER.forEach(function (diff) { overallTopicScore += mastery[topic][diff].score; count++; });
      var avgScore = Math.round(overallTopicScore / count);
      var avgColor = masteryColor(avgScore);

      topicRows +=
        '<div class="quiz-heatmap-row">' +
          '<div class="quiz-heatmap-topic">' +
            '<span class="quiz-heatmap-icon">' + (TOPIC_ICONS[topic] || "") + "</span>" +
            '<span class="quiz-heatmap-name">' + (TOPIC_LABELS[topic] || topic) + "</span>" +
            '<span class="badge" style="background:' + avgColor + "22;color:" + avgColor + '">' + avgScore + "%</span>" +
          "</div>" +
          '<div class="quiz-heatmap-cells">' + cells + "</div>" +
        "</div>";
    });

    var overallMastery = 0;
    var totalCells = 0;
    getTopics().forEach(function (topic) {
      DIFFICULTY_ORDER.forEach(function (diff) { overallMastery += mastery[topic][diff].score; totalCells++; });
    });
    var overallAvg = totalCells > 0 ? Math.round(overallMastery / totalCells) : 0;

    el.innerHTML =
      '<div class="card">' +
        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem">' +
          '<h2 class="section-title" style="margin:0">Mastery Heatmap</h2>' +
          '<button class="btn btn-sm" onclick="QuizEngine.init()">Back</button>' +
        "</div>" +
        '<div style="text-align:center;margin-bottom:1.5rem">' +
          renderProgressRing(overallAvg, 100, 8, masteryColor(overallAvg), "Overall Mastery") +
        "</div>" +
        '<div class="quiz-heatmap-legend">' +
          '<span style="color:#f85149">New</span>' +
          '<div class="quiz-heatmap-legend-bar">' +
            '<div style="background:linear-gradient(to right,#f85149,#d29922,#ff8c00,#2dd4bf,#3fb950);width:100%;height:6px;border-radius:3px"></div>' +
          "</div>" +
          '<span style="color:#3fb950">Mastered</span>' +
        "</div>" +
        '<div class="quiz-heatmap-diff-labels">' +
          '<div class="quiz-heatmap-topic"></div>' +
          '<div class="quiz-heatmap-cells" style="color:var(--text-muted);font-size:0.75rem;font-weight:600">' +
          DIFFICULTY_ORDER.map(function (d) { return '<div style="text-align:center">' + DIFFICULTY_LABELS[d].label + "</div>"; }).join("") +
          "</div>" +
        "</div>" +
        topicRows +
      "</div>";

    show("quiz-heatmap");
  }

  // ========== STATS DETAIL ==========
  function renderStatsDetail() {
    destroyAllCharts();
    hideAll();
    var stats = loadStats();
    var history = loadHistory();
    var el = $("quiz-stats-detail");
    if (!el) return;

    el.innerHTML =
      '<div class="card">' +
        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem">' +
          '<h2 class="section-title" style="margin:0">Performance Stats</h2>' +
          '<button class="btn btn-sm" onclick="QuizEngine.init()">Back</button>' +
        "</div>" +
        '<div class="grid grid-2" style="margin-bottom:1.5rem">' +
          '<div class="card" style="background:var(--bg-glass)">' +
            '<h3 style="color:var(--quantum)">Score Trend</h3>' +
            '<canvas id="quiz-trend-chart" height="200"></canvas>' +
          "</div>" +
          '<div class="card" style="background:var(--bg-glass)">' +
            '<h3 style="color:var(--quantum)">Topic Radar</h3>' +
            '<canvas id="quiz-radar-chart" height="200"></canvas>' +
          "</div>" +
        "</div>" +
        '<div class="card" style="background:var(--bg-glass);margin-bottom:1rem">' +
          '<h3 style="color:var(--quantum)">Activity</h3>' +
          '<canvas id="quiz-activity-chart" height="120"></canvas>' +
        "</div>" +
        '<div class="card" style="background:var(--bg-glass)">' +
          '<h3 style="color:var(--quantum)">Topic Breakdown</h3>' +
          '<canvas id="quiz-topic-bar-chart" height="160"></canvas>' +
        "</div>" +
      "</div>";

    show("quiz-stats-detail");

    setTimeout(function () { buildStatsCharts(stats, history); }, 50);
  }

  function buildStatsCharts(stats, history) {
    var chartBase = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: "#8892aa", font: { size: 11, family: "'Inter', sans-serif" }, padding: 12, usePointStyle: true } },
        tooltip: { backgroundColor: "rgba(8,16,40,0.92)", borderColor: "rgba(60,100,180,0.2)", borderWidth: 1, titleColor: "#e4eaf5", bodyColor: "#8892aa", padding: 10, cornerRadius: 8 }
      }
    };

    // Score trend
    destroyQuizChart("trend");
    var trendEl = $("quiz-trend-chart");
    if (trendEl && history.length > 0) {
      var last20 = history.slice(-20);
      quizCharts.trend = new Chart(trendEl.getContext("2d"), {
        type: "line",
        data: {
          labels: last20.map(function (h, i) { return "#" + (history.length - 20 + i + 1); }),
          datasets: [{
            label: "Score %",
            data: last20.map(function (h) { return h.pct; }),
            borderColor: "#00d4ff",
            backgroundColor: "rgba(0,212,255,0.08)",
            fill: true,
            tension: 0.4,
            pointRadius: 3,
            pointBackgroundColor: "#00d4ff",
            borderWidth: 2,
          }]
        },
        options: Object.assign({}, chartBase, { scales: { x: { grid: { color: "rgba(60,100,180,0.08)" }, ticks: { color: "#4a5270" } }, y: { min: 0, max: 100, grid: { color: "rgba(60,100,180,0.08)" }, ticks: { color: "#4a5270" } } } })
      });
    }

    // Topic radar
    destroyQuizChart("radar");
    var radarEl = $("quiz-radar-chart");
    if (radarEl) {
      var topics = getTopics();
      var topicPcts = topics.map(function (t) {
        var ts = stats.byTopic[t];
        if (!ts || !ts.total) return 0;
        return Math.round((ts.correct / ts.total) * 100);
      });
      quizCharts.radar = new Chart(radarEl.getContext("2d"), {
        type: "radar",
        data: {
          labels: topics.map(function (t) { return TOPIC_LABELS[t] || t; }),
          datasets: [{
            label: "Accuracy %",
            data: topicPcts,
            borderColor: "#7c5cf7",
            backgroundColor: "rgba(124,92,247,0.15)",
            pointBackgroundColor: "#7c5cf7",
            pointBorderColor: "#7c5cf7",
            borderWidth: 2,
          }]
        },
        options: Object.assign({}, chartBase, {
          scales: {
            r: {
              min: 0, max: 100,
              grid: { color: "rgba(60,100,180,0.12)" },
              angleLines: { color: "rgba(60,100,180,0.12)" },
              pointLabels: { color: "#8892aa", font: { size: 10 } },
              ticks: { color: "#4a5270", backdropColor: "transparent" }
            }
          }
        })
      });
    }

    // Activity chart (sessions per day, last 14 days)
    destroyQuizChart("activity");
    var actEl = $("quiz-activity-chart");
    if (actEl && history.length > 0) {
      var days = {};
      var now = new Date();
      for (var i = 13; i >= 0; i--) {
        var d = new Date(now);
        d.setDate(d.getDate() - i);
        var key = d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
        days[key] = 0;
      }
      history.forEach(function (h) { if (days[h.date] !== undefined) days[h.date]++; });
      var dayLabels = Object.keys(days).map(function (k) { return k.slice(5); });
      var dayData = Object.values(days);

      quizCharts.activity = new Chart(actEl.getContext("2d"), {
        type: "bar",
        data: {
          labels: dayLabels,
          datasets: [{
            label: "Sessions",
            data: dayData,
            backgroundColor: "rgba(0,212,255,0.3)",
            borderColor: "#00d4ff",
            borderWidth: 1,
            borderRadius: 4,
          }]
        },
        options: Object.assign({}, chartBase, {
          scales: {
            x: { grid: { color: "rgba(60,100,180,0.08)" }, ticks: { color: "#4a5270" } },
            y: { beginAtZero: true, grid: { color: "rgba(60,100,180,0.08)" }, ticks: { color: "#4a5270", stepSize: 1 } }
          }
        })
      });
    }

    // Topic breakdown bar
    destroyQuizChart("topicBar");
    var tbEl = $("quiz-topic-bar-chart");
    if (tbEl) {
      var topics2 = getTopics();
      quizCharts.topicBar = new Chart(tbEl.getContext("2d"), {
        type: "bar",
        data: {
          labels: topics2.map(function (t) { return TOPIC_LABELS[t] || t; }),
          datasets: [
            { label: "Correct", data: topics2.map(function (t) { return (stats.byTopic[t] || {}).correct || 0; }), backgroundColor: "rgba(63,185,80,0.5)", borderColor: "#3fb950", borderWidth: 1, borderRadius: 4 },
            { label: "Incorrect", data: topics2.map(function (t) { var s = stats.byTopic[t] || {}; return (s.total || 0) - (s.correct || 0); }), backgroundColor: "rgba(248,81,73,0.3)", borderColor: "#f85149", borderWidth: 1, borderRadius: 4 },
          ]
        },
        options: Object.assign({}, chartBase, {
          indexAxis: "y",
          scales: {
            x: { stacked: true, grid: { color: "rgba(60,100,180,0.08)" }, ticks: { color: "#4a5270" } },
            y: { stacked: true, grid: { color: "rgba(60,100,180,0.08)" }, ticks: { color: "#8892aa", font: { size: 10 } } }
          }
        })
      });
    }
  }

  // ========== QUIZ AREA RENDERING ==========
  function updateProgress() {
    var el = $("quiz-progress");
    if (!el) return;
    var pct = questions.length > 0 ? Math.round(((currentIndex + 1) / questions.length) * 100) : 0;

    var timerHtml = "";
    if (mode === "timed" && timer) {
      var timerColor = timeRemaining <= 60 ? "#f85149" : timeRemaining <= 300 ? "#ff8c00" : "#00d4ff";
      timerHtml = '<div class="quiz-timer-badge" style="background:' + timerColor + "18;border-color:" + timerColor + ';color:' + timerColor + '">' +
        "\u23F1 " + formatTime(timeRemaining) + "</div>";
    }

    var streakHtml = streakCorrect >= 3 ? '<div class="quiz-live-streak">\uD83D\uDD25 " + streakCorrect + " in a row</div>' : "";

    el.innerHTML =
      timerHtml + streakHtml +
      '<div class="quiz-progress-bar-container">' +
        '<div class="quiz-progress-text">Question ' + (currentIndex + 1) + " of " + questions.length + "</div>" +
        '<div class="quiz-progress-bar-track">' +
          '<div class="quiz-progress-bar-fill" style="width:' + pct + '%"></div>' +
        "</div>" +
      "</div>";
    show("quiz-progress");
  }

  function renderQuestion() {
    if (currentIndex >= questions.length) { finishSession(); return; }

    var q = questions[currentIndex];
    var area = $("quiz-area");
    if (!area) return;

    questionStartTime = Date.now();
    updateProgress();

    var diffInfo = DIFFICULTY_LABELS[q.difficulty] || { label: q.difficulty || "", color: "#888" };
    var topicLabel = TOPIC_LABELS[q.topic] || q.topic || "";

    var html = '<div class="card quiz-question-card animate-in">' +
      '<div class="quiz-question-meta">' +
        '<span class="badge" style="background:' + diffInfo.color + "22;color:" + diffInfo.color + '">' + diffInfo.label + "</span>" +
        '<span class="badge quantum">' + topicLabel + "</span>" +
        (mode === "adaptive" && adaptiveDifficulty ? '<span class="badge" style="background:var(--nebula);color:white">Adaptive</span>' : "") +
        '<span class="quiz-question-number">#' + (currentIndex + 1) + "</span>" +
      "</div>" +
      '<h3 class="quiz-question-text">' + q.question + "</h3>";

    if (q.type === "true_false") html += renderTrueFalse(q);
    else if (q.type === "numeric") html += renderNumeric(q);
    else html += renderMCQ(q);

    html += '<div id="quiz-explanation" style="display:none;margin-top:1.5rem"></div>';
    html += '<div id="quiz-next-btn" style="display:none;margin-top:1rem"></div>';
    html += "</div>";

    area.innerHTML = html;
    show("quiz-area");

    var input = $("quiz-numeric-input");
    if (input) input.focus();
  }

  function renderMCQ(q) {
    var html = '<div class="quiz-options-grid">';
    q.options.forEach(function (opt, i) {
      html += '<button class="btn quiz-option-btn" data-index="' + i + '" onclick="QuizEngine._handleAnswer(' + i + ')">' +
        '<span class="quiz-option-key">' + (i + 1) + "</span>" +
        "<span>" + opt + "</span>" +
        "</button>";
    });
    html += "</div>";
    return html;
  }

  function renderTrueFalse(q) {
    return '<div class="quiz-tf-grid">' +
      '<button class="btn quiz-option-btn quiz-tf-btn" data-index="0" onclick="QuizEngine._handleAnswer(0)">' +
        '<span style="font-size:1.3rem">\u2714</span> True' +
      "</button>" +
      '<button class="btn quiz-option-btn quiz-tf-btn" data-index="1" onclick="QuizEngine._handleAnswer(1)">' +
        '<span style="font-size:1.3rem">\u2718</span> False' +
      "</button>" +
      "</div>";
  }

  function renderNumeric(q) {
    return '<div class="quiz-numeric-input-group">' +
      '<input type="number" id="quiz-numeric-input" class="form-control quiz-numeric-field" placeholder="Enter your answer" step="any" onkeydown="if(event.key===\'Enter\')QuizEngine._handleNumericSubmit()">' +
      '<button class="btn btn-primary" onclick="QuizEngine._handleNumericSubmit()">Submit</button>' +
      "</div>";
  }

  // ========== FEEDBACK ==========
  function showFeedback(q, correct, selectedIndex) {
    var btns = document.querySelectorAll(".quiz-option-btn");
    btns.forEach(function (btn, i) {
      btn.disabled = true;
      btn.classList.add("quiz-option-disabled");
      var isCorrectAnswer;
      if (q.type === "true_false") {
        isCorrectAnswer = (i === 0 && q.answer === true) || (i === 1 && q.answer === false);
      } else {
        isCorrectAnswer = i === q.correctIndex;
      }
      if (isCorrectAnswer) btn.classList.add("quiz-option-correct");
      if (i === selectedIndex && !correct) btn.classList.add("quiz-option-wrong");
    });

    var xpGain = correct ? (DIFFICULTY_LABELS[q.difficulty] || { xp: 10 }).xp : 0;

    var expEl = $("quiz-explanation");
    if (expEl) {
      expEl.style.display = "block";
      expEl.innerHTML =
        '<div class="quiz-feedback ' + (correct ? "quiz-feedback-correct" : "quiz-feedback-wrong") + '">' +
          '<div class="quiz-feedback-header">' +
            '<span class="quiz-feedback-icon">' + (correct ? "\u2714" : "\u2718") + "</span>" +
            "<strong>" + (correct ? "Correct!" : "Incorrect") + "</strong>" +
            (correct ? '<span class="quiz-xp-gain">+' + xpGain + " XP</span>" : "") +
          "</div>" +
          '<div class="quiz-feedback-body">' + (q.explanation || "") + "</div>" +
          (!correct && q.type !== "true_false" && q.options ? '<div class="quiz-correct-answer">Correct answer: ' + q.options[q.correctIndex] + "</div>" : "") +
          (!correct && q.type === "true_false" ? '<div class="quiz-correct-answer">Correct answer: ' + (q.answer ? "True" : "False") + "</div>" : "") +
        "</div>";
    }

    showNextButton();
  }

  function showNumericFeedback(q, correct, userVal) {
    var input = $("quiz-numeric-input");
    if (input) {
      input.disabled = true;
      input.classList.add(correct ? "quiz-input-correct" : "quiz-input-wrong");
    }

    var xpGain = correct ? (DIFFICULTY_LABELS[q.difficulty] || { xp: 10 }).xp : 0;

    var expEl = $("quiz-explanation");
    if (expEl) {
      expEl.style.display = "block";
      expEl.innerHTML =
        '<div class="quiz-feedback ' + (correct ? "quiz-feedback-correct" : "quiz-feedback-wrong") + '">' +
          '<div class="quiz-feedback-header">' +
            '<span class="quiz-feedback-icon">' + (correct ? "\u2714" : "\u2718") + "</span>" +
            "<strong>" + (correct ? "Correct!" : "Incorrect") + "</strong>" +
            (correct ? '<span class="quiz-xp-gain">+' + xpGain + " XP</span>" : "") +
          "</div>" +
          (!correct ? '<div class="quiz-correct-answer">Correct answer: ' + q.answer + "</div>" : "") +
          '<div class="quiz-feedback-body">' + (q.explanation || "") + "</div>" +
        "</div>";
    }

    showNextButton();
  }

  function showNextButton() {
    var nextEl = $("quiz-next-btn");
    if (!nextEl) return;
    nextEl.style.display = "block";
    var isLast = currentIndex >= questions.length - 1;
    nextEl.innerHTML = '<button class="btn btn-quantum" onclick="QuizEngine._nextQuestion()">' +
      (isLast ? "See Results" : "Next Question \u2192") + "</button>" +
      '<div class="quiz-keyboard-hint">Press Enter to continue</div>';
  }

  // ========== ANSWER HANDLING ==========
  function handleAnswer(selectedIndex) {
    var q = questions[currentIndex];
    if (!q) return;

    var correct = false;
    if (q.type === "true_false") {
      correct = (selectedIndex === 0 && q.answer === true) || (selectedIndex === 1 && q.answer === false);
    } else {
      correct = selectedIndex === q.correctIndex;
    }

    var timeMs = Date.now() - questionStartTime;
    if (correct) { streakCorrect++; maxStreak = Math.max(maxStreak, streakCorrect); }
    else streakCorrect = 0;

    answers.push({ questionId: q.id || currentIndex, userAnswer: selectedIndex, correct: correct, timeMs: timeMs, difficulty: q.difficulty, topic: q.topic });
    questionResults.push({ id: q.id, correct: correct, difficulty: q.difficulty });

    updateWrongAnswers(q, correct);

    if (mode === "practice" || mode === "review" || mode === "adaptive") {
      showFeedback(q, correct, selectedIndex);
    } else if (mode === "timed") {
      advanceQuestion();
    }
  }

  function handleNumericSubmit() {
    var input = $("quiz-numeric-input");
    if (!input) return;
    var val = parseFloat(input.value);
    if (isNaN(val)) return;

    var q = questions[currentIndex];
    var tolerance = q.tolerance || 0.01;
    var correct = Math.abs(val - q.answer) <= tolerance;

    var timeMs = Date.now() - questionStartTime;
    if (correct) { streakCorrect++; maxStreak = Math.max(maxStreak, streakCorrect); }
    else streakCorrect = 0;

    answers.push({ questionId: q.id || currentIndex, userAnswer: val, correct: correct, timeMs: timeMs, difficulty: q.difficulty, topic: q.topic });
    questionResults.push({ id: q.id, correct: correct, difficulty: q.difficulty });

    updateWrongAnswers(q, correct);

    if (mode === "practice" || mode === "review" || mode === "adaptive") {
      showNumericFeedback(q, correct, val);
    } else {
      advanceQuestion();
    }
  }

  function updateWrongAnswers(q, correct) {
    if (!correct) {
      var exists = wrongAnswers.some(function (w) { return (w.questionId || w.id) === (q.id || currentIndex); });
      if (!exists) {
        wrongAnswers.push({
          questionId: q.id || currentIndex, question: q.question, topic: q.topic,
          difficulty: q.difficulty, type: q.type, options: q.options,
          correctIndex: q.correctIndex, answer: q.answer, explanation: q.explanation,
        });
        saveWrongAnswers();
      }
    } else {
      wrongAnswers = wrongAnswers.filter(function (w) { return (w.questionId || w.id) !== (q.id || currentIndex); });
      saveWrongAnswers();
    }
  }

  function nextQuestion() {
    currentIndex++;
    if (currentIndex >= questions.length) finishSession();
    else {
      if (mode === "adaptive") pickNextAdaptive();
      renderQuestion();
    }
  }

  function advanceQuestion() {
    currentIndex++;
    if (currentIndex >= questions.length) finishSession();
    else {
      if (mode === "adaptive") pickNextAdaptive();
      renderQuestion();
    }
  }

  function pickNextAdaptive() {
    var diff = pickAdaptiveDifficulty(answers);
    if (diff) {
      var pool = filterBank(null, diff);
      if (pool.length > 0) {
        var seen = questions.slice(0, currentIndex + 1).map(function (q) { return q.id; });
        var unseen = pool.filter(function (q) { return seen.indexOf(q.id) === -1; });
        if (unseen.length > 0) {
          questions[currentIndex + 1] = unseen[Math.floor(Math.random() * unseen.length)];
        }
      }
    }
  }

  // ========== START MODES ==========
  function startPractice(topic, difficulty) {
    var topicVal = topic || ($("quiz-topic-filter") ? $("quiz-topic-filter").value : "");
    var diffVal = difficulty || ($("quiz-difficulty-filter") ? $("quiz-difficulty-filter").value : "");
    var count = $("quiz-count") ? parseInt($("quiz-count").value, 10) : 20;

    var filtered = filterBank(topicVal, diffVal);
    if (filtered.length === 0) { alert("No questions match the selected filters."); return; }

    mode = "practice";
    questions = fisherYates(filtered).slice(0, Math.min(count, filtered.length));
    currentIndex = 0;
    answers = [];
    questionResults = [];
    streakCorrect = 0;
    maxStreak = 0;
    sessionStartTime = Date.now();

    hideAll();
    renderQuestion();
  }

  function startTimedExam(minutes, topicFilter) {
    var mins = minutes || ($("exam-time") ? parseInt($("exam-time").value, 10) : 30);
    var topicVal = topicFilter || ($("exam-topic-filter") ? $("exam-topic-filter").value : "");
    var count = $("exam-count") ? parseInt($("exam-count").value, 10) : 50;

    var filtered = filterBank(topicVal, "");
    if (filtered.length === 0) { alert("No questions available for the selected topic."); return; }

    mode = "timed";
    questions = fisherYates(filtered).slice(0, Math.min(count, filtered.length));
    currentIndex = 0;
    answers = [];
    questionResults = [];
    streakCorrect = 0;
    maxStreak = 0;
    sessionStartTime = Date.now();
    timeRemaining = mins * 60;

    hideAll();
    renderQuestion();
    startTimer();
  }

  function startTimer() {
    if (timer) clearInterval(timer);
    timer = setInterval(function () {
      timeRemaining--;
      updateProgress();
      if (timeRemaining <= 0) { clearInterval(timer); timer = null; finishSession(); }
    }, 1000);
  }

  function stopTimer() { if (timer) { clearInterval(timer); timer = null; } }

  function startFlashcards(topic) {
    var topicVal = topic || ($("flashcard-topic-filter") ? $("flashcard-topic-filter").value : "");
    var dueOnly = $("flashcard-due-only") ? $("flashcard-due-only").checked : true;
    var sm2Data = loadSM2();

    var filtered = filterBank(topicVal, "");
    if (filtered.length === 0) { alert("No questions available for the selected topic."); return; }

    mode = "flashcard";
    if (dueOnly) {
      var due = getDueCards(sm2Data, topicVal);
      if (due.length === 0) {
        if (confirm("No cards are due for review! Study all cards instead?")) {
          flashcardPool = fisherYates(filtered);
        } else return;
      } else {
        flashcardPool = fisherYates(due.map(function (d) { return d.question; }));
      }
    } else {
      flashcardPool = fisherYates(filtered);
    }

    currentIndex = 0;
    answers = [];
    questionResults = [];
    streakCorrect = 0;
    maxStreak = 0;
    sessionStartTime = Date.now();

    hideAll();
    renderFlashcard();
  }

  function startAdaptive() {
    var topicVal = $("adaptive-topic-filter") ? $("adaptive-topic-filter").value : "";
    var count = $("adaptive-count") ? parseInt($("adaptive-count").value, 10) : 20;

    var filtered = filterBank(topicVal, "");
    if (filtered.length === 0) { alert("No questions available."); return; }

    mode = "adaptive";
    adaptiveDifficulty = "foundational";
    questions = [];
    var shuffled = fisherYates(filtered);
    for (var i = 0; i < Math.min(count, shuffled.length); i++) {
      var diff = i < 5 ? "foundational" : adaptiveDifficulty;
      var pool = filterBank(topicVal, diff);
      if (pool.length === 0) pool = shuffled;
      var seen = questions.map(function (q) { return q.id; });
      var unseen = pool.filter(function (q) { return seen.indexOf(q.id) === -1; });
      if (unseen.length === 0) unseen = pool;
      questions.push(unseen[Math.floor(Math.random() * unseen.length)]);
    }

    currentIndex = 0;
    answers = [];
    questionResults = [];
    streakCorrect = 0;
    maxStreak = 0;
    sessionStartTime = Date.now();

    hideAll();
    renderQuestion();
  }

  // ========== FLASHCARDS ==========
  function renderFlashcard() {
    if (flashcardPool.length === 0) { finishFlashcards(); return; }

    var q = flashcardPool[0];
    var area = $("quiz-area");
    if (!area) return;

    var diffInfo = DIFFICULTY_LABELS[q.difficulty] || { label: q.difficulty || "", color: "#888" };
    var topicLabel = TOPIC_LABELS[q.topic] || q.topic || "";

    area.innerHTML =
      '<div class="quiz-flashcard-container">' +
        '<div class="quiz-flashcard-progress">Cards remaining: <strong>' + flashcardPool.length + "</strong></div>" +
        '<div class="quiz-flashcard" id="quiz-flashcard-inner">' +
          '<div class="quiz-flashcard-front">' +
            '<div class="quiz-question-meta">' +
              '<span class="badge" style="background:' + diffInfo.color + "22;color:" + diffInfo.color + '">' + diffInfo.label + "</span>" +
              '<span class="badge quantum">' + topicLabel + "</span>" +
            "</div>" +
            '<h3 class="quiz-question-text">' + q.question + "</h3>" +
            '<button class="btn btn-quantum quiz-flashcard-reveal-btn" onclick="QuizEngine._revealFlashcard()">' +
              "\u{1F441} Reveal Answer" +
            "</button>" +
          "</div>" +
          '<div class="quiz-flashcard-back" id="flashcard-answer" style="display:none">' +
            '<div class="quiz-feedback quiz-feedback-correct">' +
              '<div class="quiz-feedback-header"><strong>Answer</strong></div>' +
              '<div class="quiz-feedback-body">' + getAnswerText(q) + "</div>" +
              (q.explanation ? '<div style="margin-top:0.75rem;color:var(--text-secondary)">' + q.explanation + "</div>" : "") +
            "</div>" +
            '<div class="quiz-flashcard-actions">' +
              '<button class="btn btn-sm" style="background:#3fb95033;color:#3fb950;border-color:#3fb95055" onclick="QuizEngine._flashcardRate(4)">' +
                '<span style="font-size:1.1rem">\uD83D\uDE0A</span> Easy' +
              "</button>" +
              '<button class="btn btn-sm" style="background:#00d4ff33;color:#00d4ff;border-color:#00d4ff55" onclick="QuizEngine._flashcardRate(3)">' +
                '<span style="font-size:1.1rem">\uD83D\uDE10</span> Good' +
              "</button>" +
              '<button class="btn btn-sm" style="background:#ff8c0033;color:#ff8c00;border-color:#ff8c0055" onclick="QuizEngine._flashcardRate(2)">' +
                '<span style="font-size:1.1rem">\uD83D\uDE15</span> Hard' +
              "</button>" +
              '<button class="btn btn-sm" style="background:#f8514933;color:#f85149;border-color:#f8514955" onclick="QuizEngine._flashcardRate(1)">' +
                '<span style="font-size:1.1rem">\uD83D\uDE35</span> Again' +
              "</button>" +
            "</div>" +
          "</div>" +
        "</div>" +
      "</div>";

    show("quiz-area");
  }

  function getAnswerText(q) {
    if (q.type === "true_false") return q.answer ? "True" : "False";
    if (q.type === "numeric") return String(q.answer);
    return q.options ? q.options[q.correctIndex] : "";
  }

  function revealFlashcard() {
    var back = $("flashcard-answer");
    if (back) back.style.display = "block";
  }

  function flashcardRate(quality) {
    var q = flashcardPool[0];
    var sm2Data = loadSM2();
    sm2Data[q.id] = sm2Update(sm2Data[q.id], quality);
    saveSM2(sm2Data);

    answers.push({ questionId: q.id, userAnswer: null, correct: quality >= 3, timeMs: Date.now() - sessionStartTime });
    flashcardPool.shift();
    currentIndex++;
    renderFlashcard();
  }

  function finishFlashcards() {
    hideAll();
    var correct = answers.filter(function (a) { return a.correct; }).length;
    var total = answers.length;
    var elapsed = Date.now() - sessionStartTime;

    updateStreak();
    var xpGain = correct * 15;
    var stats = loadStats();
    stats.sessions++;
    stats.totalQuestions += total;
    stats.totalCorrect += correct;
    stats.totalXp = (stats.totalXp || 0) + xpGain;
    if (maxStreak > (stats.bestStreak || 0)) stats.bestStreak = maxStreak;
    stats.totalTimeMs = (stats.totalTimeMs || 0) + elapsed;
    saveStats(stats);
    saveHistoryEntry(stats, total, correct, elapsed, "flashcard");

    var el = $("quiz-results");
    if (!el) return;
    el.innerHTML =
      '<div class="card quiz-results-card">' +
        '<h2 class="section-title">Flashcard Session Complete</h2>' +
        '<div class="quiz-results-score-grid">' +
          '<div class="quiz-results-ring">' + renderProgressRing(total > 0 ? (correct / total) * 100 : 0, 100, 8, "#7c5cf7") + "</div>" +
          '<div class="quiz-results-stats">' +
            '<div class="grid grid-3">' +
              '<div class="quiz-result-stat"><span class="quiz-result-value">' + total + '</span><span class="quiz-result-label">Completed</span></div>' +
              '<div class="quiz-result-stat"><span class="quiz-result-value" style="color:#3fb950">' + correct + '</span><span class="quiz-result-label">Got It</span></div>' +
              '<div class="quiz-result-stat"><span class="quiz-result-value" style="color:#f85149">' + (total - correct) + '</span><span class="quiz-result-label">Still Learning</span></div>' +
            "</div>" +
            '<div class="quiz-xp-earned">+' + xpGain + " XP earned</div>" +
          "</div>" +
        "</div>" +
        '<div style="text-align:center;margin-top:1.5rem;display:flex;gap:0.5rem;justify-content:center;flex-wrap:wrap">' +
          '<button class="btn btn-quantum" onclick="QuizEngine.init()">Quiz Home</button>' +
          '<button class="btn btn-mars" onclick="QuizEngine.startFlashcards()">More Flashcards</button>' +
        "</div>" +
      "</div>";

    show("quiz-results");
  }

  // ========== REVIEW WRONG ==========
  function reviewWrong() {
    loadWrongAnswers();
    if (wrongAnswers.length === 0) { alert("No wrong answers saved. Great job!"); return; }

    mode = "review";
    questions = fisherYates(wrongAnswers);
    currentIndex = 0;
    answers = [];
    questionResults = [];
    streakCorrect = 0;
    maxStreak = 0;
    sessionStartTime = Date.now();

    hideAll();
    renderQuestion();
  }

  // ========== FINISH SESSION ==========
  function finishSession() {
    stopTimer();
    hideAll();
    destroyAllCharts();

    var totalCorrect = answers.filter(function (a) { return a.correct; }).length;
    var totalQuestions = questions.length || answers.length;
    var pct = totalQuestions > 0 ? Math.round((totalCorrect / totalQuestions) * 100) : 0;
    var elapsed = Date.now() - sessionStartTime;

    var stats = loadStats();
    stats.sessions++;
    stats.totalQuestions += totalQuestions;
    stats.totalCorrect += totalCorrect;
    if (maxStreak > (stats.bestStreak || 0)) stats.bestStreak = maxStreak;
    stats.totalTimeMs = (stats.totalTimeMs || 0) + elapsed;

    var topicBreakdown = {};
    answers.forEach(function (a, i) {
      var q = questions[i];
      if (!q) return;
      var t = q.topic || "unknown";
      if (!topicBreakdown[t]) topicBreakdown[t] = { correct: 0, total: 0 };
      topicBreakdown[t].total++;
      if (a.correct) topicBreakdown[t].correct++;
      if (!stats.byTopic[t]) stats.byTopic[t] = { total: 0, correct: 0 };
      stats.byTopic[t].total++;
      if (a.correct) stats.byTopic[t].correct++;
    });

    var xpGain = 0;
    answers.forEach(function (a) {
      if (a.correct) {
        var diff = a.difficulty || "foundational";
        xpGain += (DIFFICULTY_LABELS[diff] || { xp: 10 }).xp;
      }
    });
    if (maxStreak >= 5) xpGain = Math.round(xpGain * 1.1);
    if (pct === 100) xpGain = Math.round(xpGain * 1.25);

    stats.totalXp = (stats.totalXp || 0) + xpGain;
    saveStats(stats);

    var sm2Data = loadSM2();
    questionResults.forEach(function (r) {
      sm2Data[r.id] = sm2Update(sm2Data[r.id], r.correct ? 4 : 1);
    });
    saveSM2(sm2Data);

    updateStreak();
    saveHistoryEntry(stats, totalQuestions, totalCorrect, elapsed, mode);

    var wrongCount = totalQuestions - totalCorrect;

    var gradeLabel, gradeColor;
    if (pct >= 90) { gradeLabel = "Outstanding"; gradeColor = "#3fb950"; }
    else if (pct >= 80) { gradeLabel = "Excellent"; gradeColor = "#3fb950"; }
    else if (pct >= 70) { gradeLabel = "Good"; gradeColor = "#00d4ff"; }
    else if (pct >= 60) { gradeLabel = "Fair"; gradeColor = "#ff8c00"; }
    else { gradeLabel = "Needs Improvement"; gradeColor = "#f85149"; }

    var modeLabel = mode === "timed" ? "Timed Exam" : mode === "review" ? "Review Session" : mode === "adaptive" ? "Adaptive Challenge" : "Practice";

    var topicRows = "";
    Object.keys(topicBreakdown).sort().forEach(function (t) {
      var tb = topicBreakdown[t];
      var tPct = Math.round((tb.correct / tb.total) * 100);
      var tColor = masteryColor(tPct);
      topicRows +=
        '<tr><td>' + (TOPIC_LABELS[t] || t) + "</td>" +
        "<td>" + tb.correct + " / " + tb.total + "</td>" +
        '<td style="color:' + tColor + ';font-weight:700">' + tPct + "%</td>" +
        '<td><div class="quiz-mini-bar"><div class="quiz-mini-bar-fill" style="width:' + tPct + "%;background:" + tColor + '"></div></div></td></tr>';
    });

    var el = $("quiz-results");
    if (!el) return;

    el.innerHTML =
      '<div class="card quiz-results-card">' +
        '<div class="quiz-results-header">' +
          '<h2 class="section-title">' + modeLabel + " Results</h2>" +
          '<div class="quiz-results-grade" style="color:' + gradeColor + '">' +
            '<div class="quiz-results-pct">' + pct + "%</div>" +
            '<div class="quiz-results-grade-label">' + gradeLabel + "</div>" +
          "</div>" +
        "</div>" +

        '<div class="quiz-results-score-grid">' +
          '<div class="quiz-results-ring">' + renderProgressRing(pct, 120, 10, gradeColor) + "</div>" +
          '<div class="quiz-results-stats">' +
            '<div class="grid grid-3">' +
              '<div class="quiz-result-stat"><span class="quiz-result-value">' + totalCorrect + " / " + totalQuestions + '</span><span class="quiz-result-label">Score</span></div>' +
              '<div class="quiz-result-stat"><span class="quiz-result-value">' + formatTimeLong(elapsed) + '</span><span class="quiz-result-label">Time</span></div>' +
              '<div class="quiz-result-stat"><span class="quiz-result-value" style="color:#ff8c00">' + maxStreak + '</span><span class="quiz-result-label">Best Streak</span></div>' +
            "</div>" +
            '<div class="quiz-xp-earned">+' + xpGain + " XP earned" +
              (maxStreak >= 5 ? ' <span class="badge success">Streak Bonus +10%</span>' : "") +
              (pct === 100 ? ' <span class="badge accent">Perfect Bonus +25%</span>' : "") +
            "</div>" +
          "</div>" +
        "</div>" +

        (topicRows
          ? '<div class="quiz-results-breakdown">' +
            '<h3>Breakdown by Topic</h3>' +
            '<table class="pres-table"><thead><tr><th>Topic</th><th>Score</th><th>%</th><th>Mastery</th></tr></thead><tbody>' +
            topicRows + "</tbody></table></div>"
          : "") +

        '<div class="quiz-results-actions">' +
          (wrongCount > 0 ? '<button class="btn btn-mars" onclick="QuizEngine.reviewWrong()">Review Mistakes (' + wrongCount + ")</button>" : "") +
          '<button class="btn btn-quantum" onclick="QuizEngine.init()">Quiz Home</button>' +
          '<button class="btn btn-primary" onclick="QuizEngine.showQuickStart()">Quick Retry</button>' +
        "</div>" +
      "</div>" +

      '<div class="card" style="margin-top:1rem">' +
        '<h3 style="color:var(--quantum)">Session Performance</h3>' +
        '<canvas id="quiz-session-chart" height="160"></canvas>' +
      "</div>";

    show("quiz-results");

    if (pct >= 90) launchConfetti();

    setTimeout(function () {
      destroyQuizChart("session");
      var sessionEl = $("quiz-session-chart");
      if (sessionEl) {
        var labels = answers.map(function (a, i) { return "Q" + (i + 1); });
        var colors = answers.map(function (a) { return a.correct ? "#3fb950" : "#f85149"; });
        var times = answers.map(function (a) { return Math.round(a.timeMs / 1000); });

        quizCharts.session = new Chart(sessionEl.getContext("2d"), {
          type: "bar",
          data: {
            labels: labels,
            datasets: [
              { label: "Time (s)", data: times, backgroundColor: colors.map(function (c) { return c + "55"; }), borderColor: colors, borderWidth: 1, borderRadius: 3, yAxisID: "y" },
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
              x: { grid: { color: "rgba(60,100,180,0.08)" }, ticks: { color: "#4a5270" } },
              y: { beginAtZero: true, grid: { color: "rgba(60,100,180,0.08)" }, ticks: { color: "#4a5270" }, title: { display: true, text: "Seconds", color: "#4a5270" } }
            }
          }
        });
      }
    }, 100);
  }

  function saveHistoryEntry(stats, totalQuestions, totalCorrect, elapsed, mode) {
    var history = loadHistory();
    history.push({
      date: todayKey(),
      mode: mode,
      totalQuestions: totalQuestions,
      correct: totalCorrect,
      pct: totalQuestions > 0 ? Math.round((totalCorrect / totalQuestions) * 100) : 0,
      timeMs: elapsed,
      timestamp: Date.now(),
    });
    if (history.length > 100) history = history.slice(-100);
    saveHistory(history);
  }

  // ========== QUICK START ==========
  function showQuickStart() {
    mode = "practice";
    questions = fisherYates(bank).slice(0, 20);
    currentIndex = 0;
    answers = [];
    questionResults = [];
    streakCorrect = 0;
    maxStreak = 0;
    sessionStartTime = Date.now();

    hideAll();
    renderQuestion();
  }

  // ========== KEYBOARD ==========
  function handleKeydown(e) {
    if (!mode || mode === "flashcard") return;
    if (mode === "timed" || mode === "practice" || mode === "review" || mode === "adaptive") {
      var q = questions[currentIndex];
      if (!q) return;

      if (e.key >= "1" && e.key <= "4") {
        var idx = parseInt(e.key, 10) - 1;
        if (q.type !== "numeric") {
          var maxIdx = q.type === "true_false" ? 1 : (q.options ? q.options.length : 0);
          if (idx < maxIdx) handleAnswer(idx);
        }
      }

      if (e.key === "Enter") {
        var nextBtnEl = $("quiz-next-btn");
        if (nextBtnEl && nextBtnEl.style.display !== "none" && nextBtnEl.querySelector("button")) {
          nextQuestion();
        }
      }
    }
  }

  document.addEventListener("keydown", handleKeydown);

  // ========== INIT ==========
  function init() {
    stopTimer();
    destroyAllCharts();
    mode = null;
    currentIndex = 0;
    questions = [];
    answers = [];
    questionResults = [];
    streakCorrect = 0;
    maxStreak = 0;
    adaptiveDifficulty = null;

    fetch("data/quiz_bank.json")
      .then(function (res) {
        if (!res.ok) throw new Error("Failed to load quiz bank: " + res.status);
        return res.json();
      })
      .then(function (data) {
        bank = Array.isArray(data) ? data : data.questions || [];
        bank.forEach(function (q) {
          if (q.type === "mcq" && q.choices && !q.options) {
            q.options = q.choices;
          }
          if (q.type === "mcq" && q.answer && q.options && q.correctIndex === undefined) {
            q.correctIndex = q.options.indexOf(q.answer);
            if (q.correctIndex === -1) q.correctIndex = 0;
          }
          if (q.type === "true_false" || q.type === "tf") {
            q.type = "true_false";
          }
        });
        renderWelcome();
      })
      .catch(function (err) {
        var welcomeEl = $("quiz-welcome");
        if (welcomeEl) {
          hideAll();
          welcomeEl.innerHTML =
            '<div class="callout callout-danger">' +
            "<strong>Error loading quiz data</strong><br>" + err.message +
            "<br><br>Make sure <code>docs/data/quiz_bank.json</code> exists." +
            "</div>";
          show("quiz-welcome");
        }
      });
  }

  return {
    init: init,
    startPractice: startPractice,
    startTimedExam: startTimedExam,
    startFlashcards: startFlashcards,
    startAdaptive: startAdaptive,
    reviewWrong: reviewWrong,
    showHeatmap: renderHeatmap,
    showStatsDetail: renderStatsDetail,
    showQuickStart: showQuickStart,
    _handleAnswer: handleAnswer,
    _handleNumericSubmit: handleNumericSubmit,
    _nextQuestion: nextQuestion,
    _revealFlashcard: revealFlashcard,
    _flashcardRate: flashcardRate,
  };
})();
