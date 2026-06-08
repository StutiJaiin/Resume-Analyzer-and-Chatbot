/* ═══════════════════════════════════════════════════════════════════
   ResumeIQ — UI Rendering
   File: js/ui.js

   All DOM manipulation functions.
   Keeps rendering logic separate from NLP (nlp.js) and app logic (app.js).
═══════════════════════════════════════════════════════════════════ */

/* ───────────────────────────────────────────
   showPhase(n)
   Shows phase n (1–4), hides all others.
   Updates step bar state.
─────────────────────────────────────────── */
function showPhase(n) {
  document.querySelectorAll('.phase').forEach((p, i) => {
    p.classList.toggle('active', i === n - 1);
  });
  updateStepBar(n);
}

/* ───────────────────────────────────────────
   updateStepBar(currentStep)
   Marks steps < current as 'done',
   current step as 'active', future as neutral.
─────────────────────────────────────────── */
function updateStepBar(current) {
  for (let i = 1; i <= 4; i++) {
    const el = document.getElementById('step' + i);
    el.classList.remove('active', 'done');
    if (i < current)      el.classList.add('done');
    else if (i === current) el.classList.add('active');
  }
}

function setStepDone(n) {
  document.getElementById('step' + n).classList.add('done');
}

/* ───────────────────────────────────────────
   showLoading() / hideLoading()
   Animates the loading steps sequentially
─────────────────────────────────────────── */
function showLoading() {
  document.getElementById('loading').classList.add('show');
}

function hideLoading() {
  document.getElementById('loading').classList.remove('show');
}

async function animateLoadingSteps() {
  const steps  = ['ls1','ls2','ls3','ls4','ls5'];
  const labels = [
    '✅ Text extracted and tokenized',
    '✅ Job description profiles loaded',
    '✅ TF-IDF vectors computed',
    '✅ Cosine similarity calculated',
    '✅ Suggestions generated'
  ];

  for (let i = 0; i < steps.length; i++) {
    await sleep(500 + Math.random() * 400);
    document.getElementById(steps[i]).textContent = labels[i];
    document.getElementById(steps[i]).classList.add('done');
  }
  await sleep(300);
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

/* ───────────────────────────────────────────
   renderAnalysis(result)
   Renders the full Phase 3 analysis view.

   result = {
     overall, kwPct, cosPct, skPct, expPct,
     kwResult, profile, jobRole, fname
   }
─────────────────────────────────────────── */
function renderAnalysis(result) {
  // Header
  document.getElementById('job-tag-name').textContent     = result.jobRole;
  document.getElementById('filename-display').textContent = '📄 ' + result.fname;

  // ── Score ring animation ──
  setTimeout(() => {
    const pct     = result.overall;
    const circumf = 2 * Math.PI * 50;            // r=50 → C = 2πr ≈ 314.16
    const offset  = circumf * (1 - pct / 100);   // stroke-dashoffset

    const circle  = document.getElementById('score-circle');
    circle.style.strokeDashoffset = offset;
    circle.style.stroke =
      pct >= 75 ? '#059669' : pct >= 50 ? '#d97706' : '#dc2626';

    // Animate counter
    let i = 0;
    const tick = setInterval(() => {
      document.getElementById('score-display').textContent = i + '%';
      if (i >= pct) clearInterval(tick); else i++;
    }, 16);

    // Verdict text
    const verdictEl = document.getElementById('score-verdict');
    verdictEl.textContent =
      pct >= 75 ? '🟢 Strong Match'   :
      pct >= 50 ? '🟡 Moderate Match' : '🔴 Needs Work';
    verdictEl.style.color =
      pct >= 75 ? 'var(--success)' :
      pct >= 50 ? 'var(--warn)'    : 'var(--danger)';
  }, 150);

  // ── Breakdown bars (animate after slight delay) ──
  const bars = [
    ['kw',  result.kwPct,  '#4f46e5'],
    ['cos', result.cosPct, '#7c3aed'],
    ['sk',  result.skPct,  '#059669'],
    ['exp', result.expPct, '#d97706']
  ];
  bars.forEach(([id, val, color]) => {
    setTimeout(() => {
      document.getElementById(id + '-score').textContent = val + '%';
      const bar = document.getElementById(id + '-bar');
      bar.style.width      = val + '%';
      bar.style.background = color;
    }, 400);
  });

  // ── Keyword chips ──
  renderKeywords(result);

  // ── Source cards ──
  renderSources(result.profile.sources);

  // ── Improvement suggestions ──
  renderSuggestions(result);
}

/* ───────────────────────────────────────────
   renderKeywords(result)
   Shows matched (green) and missing (red) keywords
─────────────────────────────────────────── */
function renderKeywords(result) {
  const grid = document.getElementById('kw-grid');
  grid.innerHTML = '';

  const matchedSet = new Set(result.kwResult.matched);

  // Combine matched JD keywords + canonical skills
  const allKw = [
    ...result.kwResult.matched.slice(0, 12),
    ...result.profile.skills
  ];
  const seen = new Set();

  allKw.forEach(kw => {
    const key = kw.toLowerCase();
    if (seen.has(key)) return;
    seen.add(key);

    const isMatch = matchedSet.has(stem(key.replace(/[^a-z0-9]/g, '')));
    const chip    = document.createElement('div');
    chip.className = 'kw-chip ' + (isMatch ? 'kw-match' : 'kw-miss');
    chip.textContent = (isMatch ? '✓ ' : '✗ ') + kw;
    grid.appendChild(chip);
  });
}

/* ───────────────────────────────────────────
   renderSources(sources)
   Renders web source cards
─────────────────────────────────────────── */
function renderSources(sources) {
  const list = document.getElementById('sources-list');
  list.innerHTML = sources.map(s => `
    <div class="source-item">
      <div class="source-icon">${s.icon}</div>
      <div>
        <div class="source-title">${s.title}</div>
        <div class="source-url">${s.url}</div>
        <div class="source-insight">${s.insight}</div>
      </div>
    </div>
  `).join('');
}

/* ───────────────────────────────────────────
   renderSuggestions(result)
   Generates and renders improvement tips
─────────────────────────────────────────── */
function renderSuggestions(result) {
  const job      = result.jobRole;
  const missing  = result.profile.skills.filter(
    s => !result.kwResult.matched.includes(stem(s.toLowerCase().replace(/[^a-z0-9]/g, '')))
  );
  const sugs = [];

  if (result.kwPct < 60) {
    sugs.push({
      level: 'high',
      title: 'Add missing keywords',
      body: `Include these terms in your resume: ${missing.slice(0, 4).join(', ')}. ATS systems filter by exact keyword matches before a human ever reads your resume.`
    });
  }
  if (result.cosPct < 55) {
    sugs.push({
      level: 'high',
      title: 'Mirror job-description language',
      body: `Your vocabulary diverges from how "${job}" roles are described. Reread 5–10 JD postings and adopt their exact phrasing in your bullet points.`
    });
  }
  if (result.skPct < 70) {
    sugs.push({
      level: 'med',
      title: 'Expand your skills section',
      body: `Missing coverage for: ${missing.slice(0, 3).join(', ')}. Add side projects, online courses, or certifications that demonstrate these.`
    });
  }
  sugs.push({
    level: 'med',
    title: 'Quantify your impact',
    body: 'Add numbers to every bullet: "Improved model accuracy by 12%", "Reduced pipeline runtime by 3 hours", "Led a team of 4 engineers".'
  });
  sugs.push({
    level: 'low',
    title: 'Tailor your summary',
    body: `Open with a 2-line summary that explicitly mentions "${job}" and your top 2 relevant skills. Recruiters spend 6 seconds on first read.`
  });

  const list = document.getElementById('improve-list');
  list.innerHTML = sugs.map(s => `
    <div class="improve-item">
      <div class="improve-badge badge-${s.level}">${s.level === 'high' ? '!' : s.level === 'med' ? '~' : '+'}</div>
      <div class="improve-text"><strong>${s.title}</strong>${s.body}</div>
    </div>
  `).join('');
}

/* ───────────────────────────────────────────
   escHtml(str)
   Escapes user input before inserting into DOM
─────────────────────────────────────────── */
function escHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}
