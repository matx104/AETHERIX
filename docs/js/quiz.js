window.QuizEngine = (function () {
  const TOPIC_LABELS = {
    dtn_protocols: "DTN Protocols",
    quantum_comms: "Quantum Communications",
    space_infrastructure: "Space Infrastructure",
    orbital_mechanics: "Orbital Mechanics",
    radiation_hardening: "Radiation Hardening",
    data_prioritization: "Data Prioritization",
    standards: "Standards & RFCs",
    aetherix_specific: "AETHERIX Platform",
  };

  const DIFFICULTY_LABELS = {
    foundational: { label: "Foundational", color: "#3fb950" },
    intermediate: { label: "Intermediate", color: "#00d4ff" },
    advanced: { label: "Advanced", color: "#ff8c00" },
    expert: { label: "Expert", color: "#f85149" },
  };

  const STORAGE_KEY = "aetherix_wrong_answers";
  const STATS_KEY = "aetherix_quiz_stats";

  let bank = [];
  let mode = null;
  let currentIndex = 0;
  let questions = [];
  let answers = [];
  let wrongAnswers = [];
  let timer = null;
  let timeRemaining = 0;
  let sessionStartTime = 0;
  let questionStartTime = 0;
  let flashcardPool = [];

  function fisherYates(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function $(id) {
    return document.getElementById(id);
  }

  function show(el) {
    if (typeof el === "string") el = $(el);
    if (el) el.style.display = "";
  }

  function hide(el) {
    if (typeof el === "string") el = $(el);
    if (el) el.style.display = "none";
  }

  function hideAll() {
    hide("quiz-welcome");
    hide("quiz-filters");
    hide("quiz-area");
    hide("quiz-progress");
    hide("quiz-results");
    hide("quiz-review");
  }

  function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return m + ":" + (s < 10 ? "0" : "") + s;
  }

  function loadWrongAnswers() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      wrongAnswers = stored ? JSON.parse(stored) : [];
    } catch {
      wrongAnswers = [];
    }
  }

  function saveWrongAnswers() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(wrongAnswers));
    } catch {}
  }

  function loadStats() {
    try {
      const stored = localStorage.getItem(STATS_KEY);
      return stored ? JSON.parse(stored) : { sessions: 0, totalQuestions: 0, totalCorrect: 0, byTopic: {} };
    } catch {
      return { sessions: 0, totalQuestions: 0, totalCorrect: 0, byTopic: {} };
    }
  }

  function saveStats(stats) {
    try {
      localStorage.setItem(STATS_KEY, JSON.stringify(stats));
    } catch {}
  }

  function getTopics() {
    const topics = new Set();
    bank.forEach(function (q) {
      if (q.topic) topics.add(q.topic);
    });
    return Array.from(topics).sort();
  }

  function getDifficulties() {
    const diffs = new Set();
    bank.forEach(function (q) {
      if (q.difficulty) diffs.add(q.difficulty);
    });
    return Array.from(diffs);
  }

  function filterBank(topic, difficulty) {
    return bank.filter(function (q) {
      if (topic && q.topic !== topic) return false;
      if (difficulty && q.difficulty !== difficulty) return false;
      return true;
    });
  }

  function populateFilters() {
    var topicSelect = $("quiz-topic-filter");
    var diffSelect = $("quiz-difficulty-filter");
    if (!topicSelect || !diffSelect) return;

    topicSelect.innerHTML = '<option value="">All Topics</option>';
    getTopics().forEach(function (t) {
      var opt = document.createElement("option");
      opt.value = t;
      opt.textContent = TOPIC_LABELS[t] || t;
      topicSelect.appendChild(opt);
    });

    diffSelect.innerHTML = '<option value="">All Difficulties</option>';
    getDifficulties().forEach(function (d) {
      var opt = document.createElement("option");
      opt.value = d;
      opt.textContent = DIFFICULTY_LABELS[d] ? DIFFICULTY_LABELS[d].label : d;
      diffSelect.appendChild(opt);
    });
  }

  function renderWelcome() {
    hideAll();
    var stats = loadStats();
    loadWrongAnswers();

    var welcomeEl = $("quiz-welcome");
    if (!welcomeEl) return;

    var overallPct =
      stats.totalQuestions > 0
        ? Math.round((stats.totalCorrect / stats.totalQuestions) * 100)
        : 0;

    welcomeEl.innerHTML =
      '<h2 class="section-title">Knowledge Assessment</h2>' +
      '<div class="grid grid-3">' +
      '<div class="card" style="text-align:center">' +
      '<h3>Total Sessions</h3>' +
      '<p style="font-size:2rem;font-weight:700;color:var(--quantum)">' +
      stats.sessions +
      "</p></div>" +
      '<div class="card" style="text-align:center">' +
      "<h3>Questions Answered</h3>" +
      '<p style="font-size:2rem;font-weight:700;color:var(--quantum)">' +
      stats.totalQuestions +
      "</p></div>" +
      '<div class="card" style="text-align:center">' +
      "<h3>Overall Score</h3>" +
      '<p style="font-size:2rem;font-weight:700;color:' +
      (overallPct >= 70 ? "#3fb950" : overallPct >= 40 ? "#ff8c00" : "#f85149") +
      '">' +
      overallPct +
      "%</p></div>" +
      "</div>" +
      (wrongAnswers.length > 0
        ? '<div class="callout" style="margin:1.5rem 0"><strong>' +
          wrongAnswers.length +
          ' wrong answers saved for review.</strong> <button class="btn btn-danger" onclick="QuizEngine.reviewWrong()">Review Wrong Answers</button></div>'
        : "") +
      '<div class="grid grid-2" style="margin-top:1.5rem">' +
      '<div class="card">' +
      '<h3 style="color:var(--quantum)">Practice Mode</h3>' +
      "<p>Learn at your own pace with immediate feedback. Choose a topic and difficulty.</p>" +
      '<div class="form-group"><label>Topic</label><select id="quiz-topic-filter" class="form-control"></select></div>' +
      '<div class="form-group"><label>Difficulty</label><select id="quiz-difficulty-filter" class="form-control"></select></div>' +
      '<button class="btn btn-quantum" onclick="QuizEngine.startPractice()">' +
      "Start Practice</button></div>" +
      '<div class="card">' +
      '<h3 style="color:var(--quantum)">Timed Exam</h3>' +
      "<p>Simulate a timed assessment. 30 minutes, 50 questions.</p>" +
      '<div class="form-group"><label>Topic Filter</label><select id="exam-topic-filter" class="form-control"><option value="">All Topics</option></select></div>' +
      '<div class="form-group"><label>Time (minutes)</label><select id="exam-time" class="form-control"><option value="15">15 min</option><option value="30" selected>30 min</option><option value="45">45 min</option><option value="60">60 min</option></select></div>' +
      '<button class="btn btn-primary" onclick="QuizEngine.startTimedExam()">' +
      "Start Exam</button></div>" +
      '<div class="card">' +
      '<h3 style="color:var(--quantum)">Flashcards</h3>' +
      "<p>Review key concepts with flashcard-style questions.</p>" +
      '<div class="form-group"><label>Topic</label><select id="flashcard-topic-filter" class="form-control"><option value="">All Topics</option></select></div>' +
      '<button class="btn btn-quantum" onclick="QuizEngine.startFlashcards()">' +
      "Start Flashcards</button></div>" +
      "</div>";

    show("quiz-welcome");
    populateFilters();

    var examTopicEl = $("exam-topic-filter");
    if (examTopicEl) {
      examTopicEl.innerHTML = '<option value="">All Topics</option>';
      getTopics().forEach(function (t) {
        var opt = document.createElement("option");
        opt.value = t;
        opt.textContent = TOPIC_LABELS[t] || t;
        examTopicEl.appendChild(opt);
      });
    }

    var fcTopicEl = $("flashcard-topic-filter");
    if (fcTopicEl) {
      fcTopicEl.innerHTML = '<option value="">All Topics</option>';
      getTopics().forEach(function (t) {
        var opt = document.createElement("option");
        opt.value = t;
        opt.textContent = TOPIC_LABELS[t] || t;
        fcTopicEl.appendChild(opt);
      });
    }
  }

  function updateProgress() {
    var el = $("quiz-progress");
    if (!el) return;
    var pct = questions.length > 0 ? Math.round(((currentIndex + 1) / questions.length) * 100) : 0;

    var timerHtml = "";
    if (mode === "timed" && timer) {
      timerHtml =
        '<div style="position:absolute;top:0;right:0;padding:0.5rem 1rem;background:rgba(248,81,73,0.15);border-radius:4px;font-weight:700;font-size:1.1rem;color:#f85149">' +
        "⏱ " +
        formatTime(timeRemaining) +
        "</div>";
    }

    el.innerHTML =
      timerHtml +
      '<div style="margin-top:' +
      (timerHtml ? "2.5rem" : "0") +
      '">' +
      "<div><strong>Question " +
      (currentIndex + 1) +
      " of " +
      questions.length +
      "</strong></div>" +
      '<div style="background:var(--surface);border-radius:4px;height:8px;margin-top:0.5rem;overflow:hidden">' +
      '<div style="background:var(--quantum);height:100%;width:' +
      pct +
      '%;transition:width 0.3s;border-radius:4px"></div>' +
      "</div></div>";
    show("quiz-progress");
  }

  function renderQuestion() {
    if (currentIndex >= questions.length) {
      finishSession();
      return;
    }

    var q = questions[currentIndex];
    var area = $("quiz-area");
    if (!area) return;

    questionStartTime = Date.now();
    updateProgress();

    var diffInfo = DIFFICULTY_LABELS[q.difficulty] || { label: q.difficulty || "", color: "#888" };
    var topicLabel = TOPIC_LABELS[q.topic] || q.topic || "";

    var html =
      '<div class="card">' +
      '<div style="display:flex;gap:0.5rem;margin-bottom:1rem;flex-wrap:wrap">' +
      '<span class="badge" style="background:' +
      diffInfo.color +
      '22;color:' +
      diffInfo.color +
      '">' +
      diffInfo.label +
      "</span>" +
      '<span class="badge" style="background:var(--quantum);color:var(--bg)">' +
      topicLabel +
      "</span>" +
      "</div>" +
      "<h3>" +
      q.question +
      "</h3>";

    if (q.type === "true_false") {
      html += renderTrueFalse(q);
    } else if (q.type === "numeric") {
      html += renderNumeric(q);
    } else {
      html += renderMCQ(q);
    }

    html += '<div id="quiz-explanation" style="display:none;margin-top:1.5rem"></div>';
    html += '<div id="quiz-next-btn" style="display:none;margin-top:1rem"></div>';
    html += "</div>";

    area.innerHTML = html;
    show("quiz-area");
  }

  function renderMCQ(q) {
    var html = '<div class="grid grid-2">';
    q.options.forEach(function (opt, i) {
      html +=
        '<button class="btn quiz-option-btn" data-index="' +
        i +
        '" onclick="QuizEngine._handleAnswer(' +
        i +
        ')" style="text-align:left;padding:1rem;min-height:60px;display:flex;align-items:center;gap:0.75rem;border:1px solid var(--border);background:var(--surface)">' +
        '<span style="font-weight:700;color:var(--quantum);min-width:24px">' +
        (i + 1) +
        ".</span>" +
        "<span>" +
        opt +
        "</span>" +
        "</button>";
    });
    html += "</div>";
    return html;
  }

  function renderTrueFalse(q) {
    return (
      '<div class="grid grid-2">' +
      '<button class="btn quiz-option-btn" data-index="0" onclick="QuizEngine._handleAnswer(0)" style="padding:1.5rem;font-size:1.2rem;font-weight:700;background:var(--surface);border:1px solid var(--border)">True</button>' +
      '<button class="btn quiz-option-btn" data-index="1" onclick="QuizEngine._handleAnswer(1)" style="padding:1.5rem;font-size:1.2rem;font-weight:700;background:var(--surface);border:1px solid var(--border)">False</button>' +
      "</div>"
    );
  }

  function renderNumeric(q) {
    return (
      '<div class="form-group" style="max-width:300px;margin-top:1rem">' +
      '<input type="number" id="quiz-numeric-input" class="form-control" placeholder="Enter your answer" style="font-size:1.1rem;padding:0.75rem" onkeydown="if(event.key===\'Enter\')QuizEngine._handleNumericSubmit()">' +
      '<button class="btn btn-primary" style="margin-top:0.75rem" onclick="QuizEngine._handleNumericSubmit()">Submit Answer</button>' +
      "</div>"
    );
  }

  function handleAnswer(selectedIndex) {
    var q = questions[currentIndex];
    if (!q) return;

    var correct = false;
    var userAnswer = selectedIndex;

    if (q.type === "true_false") {
      correct =
        (selectedIndex === 0 && q.answer === true) ||
        (selectedIndex === 1 && q.answer === false);
      userAnswer = selectedIndex === 0;
    } else {
      correct = selectedIndex === q.correctIndex;
    }

    var timeMs = Date.now() - questionStartTime;
    answers.push({
      questionId: q.id || currentIndex,
      userAnswer: userAnswer,
      correct: correct,
      timeMs: timeMs,
    });

    if (!correct) {
      var exists = wrongAnswers.some(function (w) {
        return (w.questionId || w.id) === (q.id || currentIndex);
      });
      if (!exists) {
        wrongAnswers.push({
          questionId: q.id || currentIndex,
          question: q.question,
          topic: q.topic,
          difficulty: q.difficulty,
          type: q.type,
          options: q.options,
          correctIndex: q.correctIndex,
          answer: q.answer,
          explanation: q.explanation,
        });
        saveWrongAnswers();
      }
    } else {
      wrongAnswers = wrongAnswers.filter(function (w) {
        return (w.questionId || w.id) !== (q.id || currentIndex);
      });
      saveWrongAnswers();
    }

    if (mode === "practice") {
      showFeedback(q, correct, selectedIndex);
    } else if (mode === "timed") {
      advanceQuestion();
    } else if (mode === "review") {
      showFeedback(q, correct, selectedIndex);
    }
  }

  function handleNumericSubmit() {
    var input = $("quiz-numeric-input");
    if (!input) return;
    var val = parseFloat(input.value);
    if (isNaN(val)) return;

    var q = questions[currentIndex];
    var tolerance = q.tolerance || 0.01;
    var correctAnswer = q.answer;
    var correct = Math.abs(val - correctAnswer) <= tolerance;

    var timeMs = Date.now() - questionStartTime;
    answers.push({
      questionId: q.id || currentIndex,
      userAnswer: val,
      correct: correct,
      timeMs: timeMs,
    });

    if (!correct) {
      var exists = wrongAnswers.some(function (w) {
        return (w.questionId || w.id) === (q.id || currentIndex);
      });
      if (!exists) {
        wrongAnswers.push({
          questionId: q.id || currentIndex,
          question: q.question,
          topic: q.topic,
          difficulty: q.difficulty,
          type: q.type,
          answer: q.answer,
          tolerance: q.tolerance,
          explanation: q.explanation,
        });
        saveWrongAnswers();
      }
    } else {
      wrongAnswers = wrongAnswers.filter(function (w) {
        return (w.questionId || w.id) !== (q.id || currentIndex);
      });
      saveWrongAnswers();
    }

    if (mode === "practice" || mode === "review") {
      showNumericFeedback(q, correct, val);
    } else {
      advanceQuestion();
    }
  }

  function showFeedback(q, correct, selectedIndex) {
    var btns = document.querySelectorAll(".quiz-option-btn");
    btns.forEach(function (btn, i) {
      btn.disabled = true;
      btn.style.pointerEvents = "none";
      if (q.type === "true_false") {
        var isCorrectAnswer =
          (i === 0 && q.answer === true) || (i === 1 && q.answer === false);
        if (isCorrectAnswer) {
          btn.style.background = "#3fb95033";
          btn.style.borderColor = "#3fb950";
          btn.style.color = "#3fb950";
        }
        if (i === selectedIndex && !correct) {
          btn.style.background = "#f8514933";
          btn.style.borderColor = "#f85149";
          btn.style.color = "#f85149";
        }
      } else {
        if (i === q.correctIndex) {
          btn.style.background = "#3fb95033";
          btn.style.borderColor = "#3fb950";
          btn.style.color = "#3fb950";
        }
        if (i === selectedIndex && !correct) {
          btn.style.background = "#f8514933";
          btn.style.borderColor = "#f85149";
          btn.style.color = "#f85149";
        }
      }
    });

    var expEl = $("quiz-explanation");
    if (expEl) {
      expEl.style.display = "block";
      expEl.innerHTML =
        '<div class="callout" style="border-left:4px solid ' +
        (correct ? "#3fb950" : "#f85149") +
        '">' +
        "<strong>" +
        (correct ? "Correct!" : "Incorrect") +
        "</strong><br>" +
        (q.explanation || "") +
        "</div>";
    }

    showNextButton();
  }

  function showNumericFeedback(q, correct, userVal) {
    var input = $("quiz-numeric-input");
    if (input) {
      input.disabled = true;
      input.style.borderColor = correct ? "#3fb950" : "#f85149";
      input.style.color = correct ? "#3fb950" : "#f85149";
    }

    var expEl = $("quiz-explanation");
    if (expEl) {
      expEl.style.display = "block";
      expEl.innerHTML =
        '<div class="callout" style="border-left:4px solid ' +
        (correct ? "#3fb950" : "#f85149") +
        '">' +
        "<strong>" +
        (correct ? "Correct!" : "Incorrect") +
        "</strong>" +
        (!correct ? "<br>Correct answer: " + q.answer : "") +
        "<br>" +
        (q.explanation || "") +
        "</div>";
    }

    showNextButton();
  }

  function showNextButton() {
    var nextEl = $("quiz-next-btn");
    if (!nextEl) return;
    nextEl.style.display = "block";

    var isLast = currentIndex >= questions.length - 1;
    nextEl.innerHTML =
      '<button class="btn btn-quantum" onclick="QuizEngine._nextQuestion()">' +
      (isLast ? "See Results" : "Next Question →") +
      "</button>";
  }

  function nextQuestion() {
    currentIndex++;
    if (currentIndex >= questions.length) {
      finishSession();
    } else {
      renderQuestion();
    }
  }

  function advanceQuestion() {
    currentIndex++;
    if (currentIndex >= questions.length) {
      finishSession();
    } else {
      renderQuestion();
    }
  }

  function startPractice(topic, difficulty) {
    var topicVal = topic || ($("quiz-topic-filter") ? $("quiz-topic-filter").value : "");
    var diffVal = difficulty || ($("quiz-difficulty-filter") ? $("quiz-difficulty-filter").value : "");

    var filtered = filterBank(topicVal, diffVal);
    if (filtered.length === 0) {
      alert("No questions match the selected filters.");
      return;
    }

    mode = "practice";
    questions = fisherYates(filtered).slice(0, 20);
    currentIndex = 0;
    answers = [];
    sessionStartTime = Date.now();

    hideAll();
    renderQuestion();
  }

  function startTimedExam(minutes, topicFilter) {
    var mins = minutes || ($("exam-time") ? parseInt($("exam-time").value, 10) : 30);
    var topicVal = topicFilter || ($("exam-topic-filter") ? $("exam-topic-filter").value : "");

    var filtered = filterBank(topicVal, "");
    if (filtered.length === 0) {
      alert("No questions available for the selected topic.");
      return;
    }

    mode = "timed";
    questions = fisherYates(filtered).slice(0, 50);
    currentIndex = 0;
    answers = [];
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
      if (timeRemaining <= 0) {
        clearInterval(timer);
        timer = null;
        finishSession();
      }
    }, 1000);
  }

  function stopTimer() {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
  }

  function startFlashcards(topic) {
    var topicVal = topic || ($("flashcard-topic-filter") ? $("flashcard-topic-filter").value : "");

    var filtered = filterBank(topicVal, "");
    if (filtered.length === 0) {
      alert("No questions available for the selected topic.");
      return;
    }

    mode = "flashcard";
    flashcardPool = fisherYates(filtered);
    currentIndex = 0;
    answers = [];
    sessionStartTime = Date.now();

    hideAll();
    renderFlashcard();
  }

  function renderFlashcard() {
    if (flashcardPool.length === 0) {
      finishFlashcards();
      return;
    }

    var q = flashcardPool[0];
    var area = $("quiz-area");
    if (!area) return;

    var diffInfo = DIFFICULTY_LABELS[q.difficulty] || { label: q.difficulty || "", color: "#888" };
    var topicLabel = TOPIC_LABELS[q.topic] || q.topic || "";

    var html =
      '<div class="card" style="max-width:700px;margin:0 auto">' +
      '<div style="display:flex;gap:0.5rem;margin-bottom:1rem;flex-wrap:wrap">' +
      '<span class="badge" style="background:' +
      diffInfo.color +
      '22;color:' +
      diffInfo.color +
      '">' +
      diffInfo.label +
      "</span>" +
      '<span class="badge" style="background:var(--quantum);color:var(--bg)">' +
      topicLabel +
      "</span>" +
      "</div>" +
      "<h3>" +
      q.question +
      "</h3>" +
      '<div style="margin-top:1.5rem;text-align:center">' +
      '<button class="btn btn-quantum" onclick="QuizEngine._revealFlashcard()">Reveal Answer</button>' +
      "</div>" +
      '<div id="flashcard-answer" style="display:none;margin-top:1.5rem"></div>' +
      "</div>";

    area.innerHTML = html;

    var progressEl = $("quiz-progress");
    if (progressEl) {
      progressEl.innerHTML =
        "<div><strong>Flashcards remaining: " +
        flashcardPool.length +
        "</strong></div>";
      show("quiz-progress");
    }

    show("quiz-area");
  }

  function revealFlashcard() {
    var q = flashcardPool[0];
    var answerEl = $("flashcard-answer");
    if (!answerEl) return;

    var answerText = "";
    if (q.type === "true_false") {
      answerText = q.answer ? "True" : "False";
    } else if (q.type === "numeric") {
      answerText = String(q.answer);
    } else {
      answerText = q.options ? q.options[q.correctIndex] : "";
    }

    answerEl.style.display = "block";
    answerEl.innerHTML =
      '<div class="callout" style="border-left:4px solid var(--quantum)">' +
      "<strong>Answer:</strong> " +
      answerText +
      "<br>" +
      (q.explanation ? "<br>" + q.explanation : "") +
      "</div>" +
      '<div class="grid grid-2" style="margin-top:1rem">' +
      '<button class="btn btn-success" onclick="QuizEngine._flashcardGotIt()">Got It</button>' +
      '<button class="btn btn-danger" onclick="QuizEngine._flashcardStillLearning()">Still Learning</button>' +
      "</div>";
  }

  function flashcardGotIt() {
    answers.push({
      questionId: flashcardPool[0].id || 0,
      userAnswer: null,
      correct: true,
      timeMs: Date.now() - sessionStartTime,
    });
    flashcardPool.shift();
    currentIndex++;
    renderFlashcard();
  }

  function flashcardStillLearning() {
    answers.push({
      questionId: flashcardPool[0].id || 0,
      userAnswer: null,
      correct: false,
      timeMs: Date.now() - sessionStartTime,
    });
    var card = flashcardPool.shift();
    var insertAt = Math.min(Math.floor(Math.random() * flashcardPool.length) + 1, flashcardPool.length);
    flashcardPool.splice(insertAt, 0, card);
    renderFlashcard();
  }

  function finishFlashcards() {
    hideAll();
    var correct = answers.filter(function (a) {
      return a.correct;
    }).length;
    var total = answers.length;
    var elapsed = Date.now() - sessionStartTime;

    var resultsEl = $("quiz-results");
    if (!resultsEl) return;

    resultsEl.innerHTML =
      '<div class="card">' +
      '<h2 class="section-title">Flashcard Session Complete</h2>' +
      '<div class="grid grid-3" style="margin:1.5rem 0">' +
      '<div style="text-align:center"><strong>Completed</strong><br><span style="font-size:1.8rem;font-weight:700;color:var(--quantum)">' +
      total +
      "</span></div>" +
      '<div style="text-align:center"><strong>Got It</strong><br><span style="font-size:1.8rem;font-weight:700;color:#3fb950">' +
      correct +
      "</span></div>" +
      '<div style="text-align:center"><strong>Still Learning</strong><br><span style="font-size:1.8rem;font-weight:700;color:#f85149">' +
      (total - correct) +
      "</span></div>" +
      "</div>" +
      '<div style="text-align:center;margin-top:1rem">' +
      '<button class="btn btn-quantum" onclick="QuizEngine.init()" style="margin:0.25rem">Back to Quiz Home</button>' +
      "</div></div>";

    show("quiz-results");
  }

  function reviewWrong() {
    loadWrongAnswers();
    if (wrongAnswers.length === 0) {
      alert("No wrong answers saved. Great job!");
      return;
    }

    mode = "review";
    questions = fisherYates(wrongAnswers);
    currentIndex = 0;
    answers = [];
    sessionStartTime = Date.now();

    hideAll();
    renderQuestion();
  }

  function finishSession() {
    stopTimer();
    hideAll();

    var totalCorrect = answers.filter(function (a) {
      return a.correct;
    }).length;
    var totalQuestions = questions.length;
    var pct = totalQuestions > 0 ? Math.round((totalCorrect / totalQuestions) * 100) : 0;
    var elapsed = Date.now() - sessionStartTime;

    var stats = loadStats();
    stats.sessions++;
    stats.totalQuestions += totalQuestions;
    stats.totalCorrect += totalCorrect;

    var topicBreakdown = {};
    answers.forEach(function (a, i) {
      var q = questions[i];
      if (!q) return;
      var t = q.topic || "unknown";
      if (!topicBreakdown[t]) topicBreakdown[t] = { correct: 0, total: 0 };
      topicBreakdown[t].total++;
      if (a.correct) {
        topicBreakdown[t].correct++;
        if (!stats.byTopic[t]) stats.byTopic[t] = { total: 0, correct: 0 };
        stats.byTopic[t].total++;
        stats.byTopic[t].correct++;
      } else {
        if (!stats.byTopic[t]) stats.byTopic[t] = { total: 0, correct: 0 };
        stats.byTopic[t].total++;
      }
    });
    saveStats(stats);

    var wrongCount = totalQuestions - totalCorrect;

    var topicRows = "";
    Object.keys(topicBreakdown)
      .sort()
      .forEach(function (t) {
        var tb = topicBreakdown[t];
        var tPct = Math.round((tb.correct / tb.total) * 100);
        var tColor = tPct >= 70 ? "#3fb950" : tPct >= 40 ? "#ff8c00" : "#f85149";
        topicRows +=
          "<tr><td>" +
          (TOPIC_LABELS[t] || t) +
          "</td><td>" +
          tb.correct +
          " / " +
          tb.total +
          "</td><td style='color:" +
          tColor +
          ";font-weight:700'>" +
          tPct +
          "%</td></tr>";
      });

    var elapsedSec = Math.floor(elapsed / 1000);
    var elapsedMin = Math.floor(elapsedSec / 60);
    var elapsedRemSec = elapsedSec % 60;

    var resultsEl = $("quiz-results");
    if (!resultsEl) return;

    var gradeLabel = "";
    var gradeColor = "";
    if (pct >= 90) {
      gradeLabel = "Outstanding";
      gradeColor = "#3fb950";
    } else if (pct >= 80) {
      gradeLabel = "Excellent";
      gradeColor = "#3fb950";
    } else if (pct >= 70) {
      gradeLabel = "Good";
      gradeColor = "#00d4ff";
    } else if (pct >= 60) {
      gradeLabel = "Fair";
      gradeColor = "#ff8c00";
    } else {
      gradeLabel = "Needs Improvement";
      gradeColor = "#f85149";
    }

    var modeLabel = mode === "timed" ? "Timed Exam" : mode === "review" ? "Review Session" : "Practice";

    resultsEl.innerHTML =
      '<div class="card">' +
      '<h2 class="section-title">' +
      modeLabel +
      " Results</h2>" +
      '<div style="text-align:center;margin:1.5rem 0">' +
      '<div style="font-size:3rem;font-weight:700;color:' +
      gradeColor +
      '">' +
      pct +
      "%</div>" +
      '<div style="font-size:1.2rem;color:' +
      gradeColor +
      '">' +
      gradeLabel +
      "</div>" +
      "</div>" +
      '<div class="grid grid-3">' +
      '<div style="text-align:center"><strong>Score</strong><br><span style="font-size:1.5rem;font-weight:700">' +
      totalCorrect +
      " / " +
      totalQuestions +
      "</span></div>" +
      '<div style="text-align:center"><strong>Time</strong><br><span style="font-size:1.5rem;font-weight:700">' +
      elapsedMin +
      "m " +
      elapsedRemSec +
      "s</span></div>" +
      '<div style="text-align:center"><strong>Wrong</strong><br><span style="font-size:1.5rem;font-weight:700;color:#f85149">' +
      wrongCount +
      "</span></div>" +
      "</div>" +
      (topicRows
        ? '<h3 style="margin-top:1.5rem">Breakdown by Topic</h3>' +
          '<table class="pres-table"><thead><tr><th>Topic</th><th>Score</th><th>Percentage</th></tr></thead><tbody>' +
          topicRows +
          "</tbody></table>"
        : "") +
      '<div style="text-align:center;margin-top:1.5rem;display:flex;gap:0.5rem;justify-content:center;flex-wrap:wrap">' +
      (wrongCount > 0
        ? '<button class="btn btn-danger" onclick="QuizEngine.reviewWrong()">Review Wrong Answers</button>'
        : "") +
      '<button class="btn btn-quantum" onclick="QuizEngine.init()">Try Again</button>' +
      '<button class="btn btn-primary" onclick="QuizEngine.init()">Back to Quiz Home</button>' +
      "</div></div>";

    show("quiz-results");
  }

  function handleKeydown(e) {
    if (!mode || mode === "flashcard") return;
    if (mode === "timed" || mode === "practice" || mode === "review") {
      var q = questions[currentIndex];
      if (!q) return;

      if (e.key >= "1" && e.key <= "4") {
        var idx = parseInt(e.key, 10) - 1;
        if (q.type !== "numeric") {
          var maxIdx = q.type === "true_false" ? 1 : (q.options ? q.options.length : 0);
          if (idx < maxIdx) {
            handleAnswer(idx);
          }
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

  function init() {
    stopTimer();
    mode = null;
    currentIndex = 0;
    questions = [];
    answers = [];

    fetch("data/quiz_bank.json")
      .then(function (res) {
        if (!res.ok) throw new Error("Failed to load quiz bank: " + res.status);
        return res.json();
      })
      .then(function (data) {
        bank = Array.isArray(data) ? data : data.questions || [];
        renderWelcome();
      })
      .catch(function (err) {
        var welcomeEl = $("quiz-welcome");
        if (welcomeEl) {
          hideAll();
          welcomeEl.innerHTML =
            '<div class="callout" style="border-left:4px solid #f85149">' +
            "<strong>Error loading quiz data</strong><br>" +
            err.message +
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
    reviewWrong: reviewWrong,
    _handleAnswer: handleAnswer,
    _handleNumericSubmit: handleNumericSubmit,
    _nextQuestion: nextQuestion,
    _revealFlashcard: revealFlashcard,
    _flashcardGotIt: flashcardGotIt,
    _flashcardStillLearning: flashcardStillLearning,
  };
})();
