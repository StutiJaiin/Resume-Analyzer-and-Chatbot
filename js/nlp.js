/* ═══════════════════════════════════════════════════════════════════
   ResumeIQ — NLP Engine (COMMENTED OUT — Python Backend Mode)
   File: js/nlp.js

   ★ ALL NLP LOGIC NOW RUNS ON THE PYTHON BACKEND:
     backend/nlp_engine.py

   This file is kept for reference. The Python implementation mirrors
   every function below. To restore client-side NLP, uncomment this
   file and update app.js to use these functions again.

   Python equivalents:
     STOP_WORDS       → nlp_engine.py → STOP_WORDS (frozenset)
     tokenize()       → nlp_engine.py → tokenize()
     stem()           → nlp_engine.py → stem()
     buildTFIDF()     → nlp_engine.py → build_tfidf()
     cosineSim()      → nlp_engine.py → cosine_sim()
     keywordOverlap() → nlp_engine.py → keyword_overlap()
═══════════════════════════════════════════════════════════════════ */

/*
// ─────────────────────────────────────────────────────────────
//  EVERYTHING BELOW IS COMMENTED OUT — Python backend handles NLP
// ─────────────────────────────────────────────────────────────

const STOP_WORDS = new Set([
  'i','me','my','myself','we','our','ours','ourselves',
  'you','your','yours','yourself','he','him','his','himself',
  'she','her','hers','herself','it','its','itself',
  'they','them','their','theirs','themselves',
  'what','which','who','whom','this','that','these','those',
  'am','is','are','was','were','be','been','being',
  'have','has','had','having','do','does','did','doing',
  'a','an','the','and','but','if','or','because','as',
  'until','while','of','at','by','for','with','about',
  'against','between','into','through','during','before',
  'after','above','below','to','from','up','down','in',
  'out','on','off','over','under','again','further',
  'then','once','here','there','when','where','why','how',
  'all','both','each','few','more','most','other','some',
  'such','no','nor','not','only','own','same','so','than',
  'too','very','can','will','just','should','now',
  'd','ll','m','o','re','ve','y',
  'ain','aren','couldn','didn','doesn','hadn','hasn',
  'haven','isn','ma','mightn','mustn','needn','shan',
  'shouldn','wasn','weren','won','wouldn'
]);

function tokenize(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s\+\#]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 2 && !STOP_WORDS.has(w));
}

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

function buildTFIDF(docs) {
  const N = docs.length;
  const tokenizedDocs = docs.map(d => tokenize(d).map(stem));
  const df = {};
  tokenizedDocs.forEach(tokens => {
    const seenInThisDoc = new Set(tokens);
    seenInThisDoc.forEach(t => {
      df[t] = (df[t] || 0) + 1;
    });
  });
  const vectors = tokenizedDocs.map(tokens => {
    const tf = {};
    tokens.forEach(t => { tf[t] = (tf[t] || 0) + 1; });
    const vec = {};
    const totalTokens = tokens.length || 1;
    Object.keys(tf).forEach(t => {
      const termFreq  = tf[t] / totalTokens;
      const invDocFreq = Math.log(1 + N / (df[t] || 1));
      vec[t] = termFreq * invDocFreq;
    });
    return vec;
  });
  return vectors;
}

function cosineSim(a, b) {
  const allKeys = new Set([...Object.keys(a), ...Object.keys(b)]);
  let dot  = 0;
  let normA = 0;
  let normB = 0;
  allKeys.forEach(k => {
    const va = a[k] || 0;
    const vb = b[k] || 0;
    dot   += va * vb;
    normA += va * va;
    normB += vb * vb;
  });
  if (normA === 0 || normB === 0) return 0;
  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

function keywordOverlap(resumeTokens, jdTokens) {
  const resumeStemSet = new Set(resumeTokens.map(stem));
  const jdStemSet     = new Set(jdTokens.map(stem));
  const matched = [...jdStemSet].filter(k => resumeStemSet.has(k));
  const score   = jdStemSet.size > 0 ? matched.length / jdStemSet.size : 0;
  return {
    matched,
    total: jdStemSet.size,
    score
  };
}

*/
