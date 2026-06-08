/* ═══════════════════════════════════════════════════════════════════
   ResumeIQ — App Controller (Python Backend Mode)
   File: js/app.js

   Orchestrates the full user flow:
     Phase 1 → Job role selection
     Phase 2 → Resume upload (file stored, sent to Python backend)
     Phase 3 → NLP analysis (done by Python backend, results rendered here)
     Phase 4 → AI chatbot (handled by Python backend via chat.js)

   ★ ALL NLP LOGIC NOW RUNS ON THE PYTHON BACKEND (backend/server.py)
     - Text extraction:  Python (PyPDF2, python-docx)
     - Tokenization:     Python (backend/nlp_engine.py)
     - Stemming:         Python (backend/nlp_engine.py)
     - TF-IDF:           Python (backend/nlp_engine.py)
     - Cosine Similarity: Python (backend/nlp_engine.py)
     - Keyword Overlap:   Python (backend/nlp_engine.py)
     - Job Profiles:      Python (backend/job_profiles.py)
═══════════════════════════════════════════════════════════════════ */

// ─── Global state ───
let currentJob = '';          // user's target job role
let uploadedFile = null;      // the actual File object (sent to Python backend)
let uploadedFileName = 'resume';

// ─── Job input listener ───
document.getElementById('job-input').addEventListener('input', function () {
  const v = this.value.trim();
  currentJob = v;
  window._currentJob = v;
  document.getElementById('btn-next1').disabled = v.length < 2;
  document.querySelectorAll('.sug-chip').forEach(c => c.classList.remove('active'));
});

/* ───────────────────────────────────────────
   setJob(chipElement)
   Called when user clicks a suggestion chip
─────────────────────────────────────────── */
function setJob(el) {
  currentJob = el.textContent;
  window._currentJob = currentJob;
  document.getElementById('job-input').value = currentJob;
  document.getElementById('btn-next1').disabled = false;
  document.querySelectorAll('.sug-chip').forEach(c => c.classList.remove('active'));
  el.classList.add('active');
}

/* ───────────────────────────────────────────
   goPhase2()
   Transitions from Phase 1 → Phase 2
─────────────────────────────────────────── */
function goPhase2() {
  document.getElementById('job-name-display2').textContent = '"' + currentJob + '"';
  // Enable analyze button — demo text fallback is available even without file upload
  document.getElementById('btn-analyze').disabled = false;
  showPhase(2);
}

/* ───────────────────────────────────────────
   handleDrop(event)
   Handles drag-and-drop file upload
─────────────────────────────────────────── */
function handleDrop(ev) {
  ev.preventDefault();
  document.getElementById('upload-zone').classList.remove('dragover');
  const file = ev.dataTransfer.files[0];
  if (file) processFile(file);
}

/* ───────────────────────────────────────────
   handleFile(input)
   Handles <input type="file"> change
─────────────────────────────────────────── */
function handleFile(input) {
  if (input.files[0]) processFile(input.files[0]);
}

/* ───────────────────────────────────────────
   processFile(file)
   Validates file type, updates UI, stores file.

   ★ PYTHON BACKEND MODE:
     Text extraction is no longer done in the browser.
     The raw file is stored and sent to the Python backend
     during runAnalysis(). Python handles PDF/DOCX/TXT extraction.
─────────────────────────────────────────── */
function processFile(file) {
  const ext = file.name.split('.').pop().toLowerCase();
  const allowed = ['txt', 'docx', 'doc', 'pdf'];

  if (!allowed.includes(ext)) {
    alert('Please upload a .txt, .docx, .doc, or .pdf file');
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    alert('File is larger than 5MB. Please upload a shorter resume.');
    return;
  }

  // Store file for upload to Python backend
  uploadedFile = file;
  uploadedFileName = file.name;

  // Update UI
  document.getElementById('upload-zone').classList.add('has-file');
  document.getElementById('file-name').textContent = file.name;
  document.getElementById('file-size').textContent = (file.size / 1024).toFixed(1) + ' KB';
  document.getElementById('file-info').classList.add('show');
  document.getElementById('btn-analyze').disabled = false;

  console.log('File ready for Python backend:', file.name, (file.size / 1024).toFixed(1) + ' KB');
}

/*
 * ════════════════════════════════════════════════════════════════
 *  OLD CLIENT-SIDE EXTRACTION FUNCTIONS (COMMENTED OUT)
 *  These are no longer needed — Python backend handles extraction.
 * ════════════════════════════════════════════════════════════════
 *
 * async function extractPdfWithPdfJs(file) {
 *   // Was: Mozilla pdf.js for PDF text extraction
 *   // Now: Python backend uses PyPDF2
 * }
 *
 * async function extractDocxWithMammoth(file) {
 *   // Was: mammoth.js for DOCX text extraction
 *   // Now: Python backend uses python-docx
 * }
 */

/* ───────────────────────────────────────────
   runAnalysis()
   Core function — sends file to Python backend for analysis.

   ★ PYTHON BACKEND PIPELINE:
   1. Upload file to POST /api/analyze (multipart/form-data)
   2. Python extracts text (PyPDF2 / python-docx / plain read)
   3. Python runs NLP: tokenize → stem → TF-IDF → cosine sim → keyword overlap
   4. Python returns JSON with all scores
   5. Frontend renders results (ui.js — unchanged)
─────────────────────────────────────────── */
async function runAnalysis() {
  showLoading();

  try {
    // Build form data with file + job role
    const formData = new FormData();

    if (uploadedFile) {
      formData.append('file', uploadedFile);
    } else {
      // Fallback: send demo text if no file uploaded
      formData.append('resume_text_fallback', 'true');
    }
    formData.append('job_role', currentJob);

    // Animate loading steps while waiting for backend
    const analysisPromise = fetch('/api/analyze', {
      method: 'POST',
      body: uploadedFile ? formData : JSON.stringify({
        resume_text: getDemoResumeText(),
        job_role: currentJob
      }),
      headers: uploadedFile ? {} : { 'Content-Type': 'application/json' }
    });

    // Show animated loading steps
    await animateLoadingSteps();

    // Wait for backend response
    const response = await analysisPromise;
    const data = await response.json();

    hideLoading();

    if (data.error) {
      hideLoading();
      alert('Analysis error: ' + data.error);
      return;
    }

    // ── Map Python backend response to frontend format ──
    const result = {
      overall:  data.overall,
      kwPct:    data.kw_pct,
      cosPct:   data.cos_pct,
      skPct:    data.sk_pct,
      expPct:   data.exp_pct,
      kwResult: data.kw_result,
      profile:  data.profile,
      jobRole:  currentJob,
      fname:    uploadedFileName
    };

    window._analysisResult = result;   // expose for chat.js

    // Build chat system context using the result
    systemContext = buildSystemContext(result, getDemoResumeText());

    renderAnalysis(result);   // from ui.js
    showPhase(3);
    setStepDone(3);

    console.log('Analysis complete (Python backend):', result);

  } catch (err) {
    hideLoading();
    console.error('Python backend analysis failed:', err);
    alert(
      'Could not connect to the Python backend.\n\n' +
      'Make sure the server is running:\n' +
      '  cd backend\n' +
      '  python server.py\n\n' +
      'Error: ' + err.message
    );
  }
}

/* ───────────────────────────────────────────
   getDemoResumeText()
   Fallback resume used when no file is uploaded.
   Sent to the Python backend as plain text.
─────────────────────────────────────────── */
function getDemoResumeText() {
  return `
    Stuti Jain — CS + AI/ML Student
    B.Tech Computer Science with AI/ML specialisation, UPES Dehradun, CGPA 8.4
    Treasurer, ACM-W Student Chapter | Career Services Department

    Technical Skills:
    Python, Machine Learning, Deep Learning, TensorFlow, PyTorch, scikit-learn,
    NLP, Computer Vision, Java, Java Swing, JavaScript, SQL, MongoDB, Git, GitHub,
    Data Structures, Algorithms, Linear Algebra, Statistics, JDBC

    Projects:
    - ResumeIQ NLP Resume Analyzer (Python, TF-IDF, Cosine Similarity, Claude API)
    - Airport Management System (MongoDB, CRUD, six collections)
    - Business Management System (Java Swing, JDBC, MySQL)
    - Machine Learning Linear Regression from Scratch (Python, NumPy)
    - Life Map Force-Directed Graph (HTML5 Canvas, Physics simulation)
    - PCA + LDA + KNN on Iris Dataset (scikit-learn, matplotlib)

    Experience:
    - Treasurer, UPES ACM-W Student Chapter — event management, finance, leadership
    - Career Services Department — student placement coordination
    - Hackathon participant: WHCL, Adobe Hackathon
    - 1st place, Tech Chronicles technical competition
    - Speaker/participant, ICMLDE international conference

    Research Interests:
    Pattern recognition, cognitive architecture, human-centred AI, AI safety,
    generative models, reinforcement learning, interpretability
  `;
}

/* ───────────────────────────────────────────
   stem() — Minimal client-side stem function
   Needed by ui.js (renderKeywords, renderSuggestions)
   for displaying matched/missing keyword chips.

   This is a simplified version — the real stemming
   happens on the Python backend.
─────────────────────────────────────────── */
function stem(word) {
  if (word.length <= 3) return word;
  word = word.replace(/inging$/, '');
  word = word.replace(/ing$/, '');
  word = word.replace(/tions$/, '');
  word = word.replace(/tion$/, '');
  word = word.replace(/ies$/, 'y');
  word = word.replace(/es$/, '');
  word = word.replace(/s$/, '');
  word = word.replace(/er$/, '');
  word = word.replace(/ed$/, '');
  return word;
}
