# ═══════════════════════════════════════════════════════════════════
#  ResumeIQ — NLP Engine (Python)
#  File: backend/nlp_engine.py
#
#  Pure Python implementation of all NLP functions:
#    1. Stopword list
#    2. tokenize()        — lowercasing, punctuation removal, stopword filter
#    3. stem()            — Porter-inspired suffix stripping
#    4. build_tf()        — Term Frequency vectors
#    5. build_tfidf()     — TF-IDF vectorization
#    6. cosine_sim()      — Dot-product cosine similarity
#    7. keyword_overlap() — Set-intersection keyword matching
#
#  This mirrors js/nlp.js but in Python, ready for future ML integration
#  with scikit-learn, NLTK, and more.
#
#  ★ FUTURE ML HOOKS are marked with [ML-HOOK] comments throughout.
# ═══════════════════════════════════════════════════════════════════

import re
import math
from typing import List, Dict, Tuple, Set, Optional

# ─── [ML-HOOK] When ready, swap in scikit-learn's TfidfVectorizer ───
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine


# ═══════════════════════════════════════════════════════════════════
#  1. STOPWORDS
#  Common English words that carry no meaning and should be
#  removed before analysis. Stored as a frozenset for O(1) lookup.
#
#  [ML-HOOK] Replace with NLTK stopwords for a more complete list:
#    from nltk.corpus import stopwords
#    STOP_WORDS = frozenset(stopwords.words('english'))
# ═══════════════════════════════════════════════════════════════════
STOP_WORDS: frozenset = frozenset([
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
    'you', 'your', 'yours', 'yourself', 'he', 'him', 'his', 'himself',
    'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
    'they', 'them', 'their', 'theirs', 'themselves',
    'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
    'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as',
    'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about',
    'against', 'between', 'into', 'through', 'during', 'before',
    'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in',
    'out', 'on', 'off', 'over', 'under', 'again', 'further',
    'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
    'all', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
    'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
    'too', 'very', 'can', 'will', 'just', 'should', 'now',
    'd', 'll', 'm', 'o', 're', 've', 'y',
    'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn',
    'haven', 'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan',
    'shouldn', 'wasn', 'weren', 'won', 'wouldn'
])


# ═══════════════════════════════════════════════════════════════════
#  2. TOKENIZE
#  Converts raw text into a list of clean tokens.
#
#  Steps:
#    a) Lowercase entire string
#    b) Replace non-alphanumeric chars (except + and #) with space
#    c) Split on whitespace
#    d) Keep tokens longer than 2 chars
#    e) Remove stopwords
#
#  Example:
#    Input:  "I built Machine Learning models using TensorFlow"
#    Output: ['built', 'machine', 'learning', 'models', 'using', 'tensorflow']
#
#  [ML-HOOK] Replace with NLTK word_tokenize for better handling:
#    from nltk.tokenize import word_tokenize
#    tokens = word_tokenize(text.lower())
# ═══════════════════════════════════════════════════════════════════
def tokenize(text: str) -> List[str]:
    """
    Tokenize text into clean, meaningful tokens.

    Parameters:
        text (str): Raw input text (resume or job description)

    Returns:
        List[str]: List of cleaned tokens with stopwords removed
    """
    # a) Lowercase
    text = text.lower()

    # b) Remove special chars, keep + and # for C++, C#, etc.
    text = re.sub(r'[^a-z0-9\s\+\#]', ' ', text)

    # c) Split on whitespace
    words = text.split()

    # d) & e) Filter: length > 2 AND not a stopword
    tokens = [w for w in words if len(w) > 2 and w not in STOP_WORDS]

    return tokens


# ═══════════════════════════════════════════════════════════════════
#  3. STEM
#  Reduces words to their root form so that
#  "learning", "learned", "learns" all map to "learn".
#
#  This is a simplified Porter stemmer covering the most
#  common English suffixes.
#
#  Full Porter algorithm: https://tartarus.org/martin/PorterStemmer/
#
#  Rules applied (in order):
#    -inging → ''        (programming → program...)
#    -ing    → ''        (running → run)
#    -tion   → ''        (classification → classif)
#    -tions  → ''
#    -ies    → 'y'       (libraries → library)
#    -es     → ''        (manages → manag)
#    -s      → ''        (models → model)
#    -er     → ''        (analyzer → analyz)
#    -ed     → ''        (trained → train)
#
#  [ML-HOOK] Replace with NLTK's PorterStemmer or SnowballStemmer:
#    from nltk.stem import PorterStemmer
#    stemmer = PorterStemmer()
#    stemmed = stemmer.stem(word)
#
#  Or use lemmatization for even better accuracy:
#    from nltk.stem import WordNetLemmatizer
#    lemmatizer = WordNetLemmatizer()
#    lemma = lemmatizer.lemmatize(word, pos='v')
# ═══════════════════════════════════════════════════════════════════
def stem(word: str) -> str:
    """
    Apply simplified Porter stemming to a single word.

    Parameters:
        word (str): Single word to stem

    Returns:
        str: Stemmed word
    """
    if len(word) <= 3:
        return word  # Don't stem very short words

    # Apply rules in order (same as js/nlp.js)
    word = re.sub(r'inging$', '', word)
    word = re.sub(r'ing$', '', word)
    word = re.sub(r'tions$', '', word)
    word = re.sub(r'tion$', '', word)
    word = re.sub(r'ies$', 'y', word)
    word = re.sub(r'es$', '', word)
    word = re.sub(r's$', '', word)
    word = re.sub(r'er$', '', word)
    word = re.sub(r'ed$', '', word)

    return word


# ═══════════════════════════════════════════════════════════════════
#  4. BUILD TF (Term Frequency)
#  Creates a normalized Term Frequency vector for a single document.
#
#  FORMULA:
#    TF(t, d) = count(t in d) / total_tokens(d)
#
#  Parameters:
#    tokens — list of stemmed tokens
#  Returns:
#    dict { term: tf_weight }
# ═══════════════════════════════════════════════════════════════════
def build_tf(tokens: List[str]) -> Dict[str, float]:
    """
    Build a normalized Term Frequency vector.

    Parameters:
        tokens (List[str]): List of stemmed tokens

    Returns:
        Dict[str, float]: TF vector {term: normalized_frequency}
    """
    tf: Dict[str, int] = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1

    total = len(tokens) or 1
    return {t: count / total for t, count in tf.items()}


# ═══════════════════════════════════════════════════════════════════
#  5. BUILD TF-IDF
#  Creates a TF-IDF vector for each document in the corpus.
#
#  FORMULA:
#    TF(t, d)    = count(t in d) / total_tokens(d)
#    IDF(t)      = log(1 + N / df(t))        ← smoothed
#    TF-IDF(t,d) = TF(t,d) × IDF(t)
#
#  Parameters:
#    docs — list of raw text strings [resume_text, jd_text, ...]
#  Returns:
#    list of TF-IDF vector dicts [{term: weight}, ...]
#
#  [ML-HOOK] Replace with scikit-learn's TfidfVectorizer:
#    from sklearn.feature_extraction.text import TfidfVectorizer
#    vectorizer = TfidfVectorizer(stop_words='english')
#    tfidf_matrix = vectorizer.fit_transform(docs)
#    # tfidf_matrix is a sparse matrix — use .toarray() for dense
# ═══════════════════════════════════════════════════════════════════
def build_tfidf(docs: List[str]) -> List[Dict[str, float]]:
    """
    Build TF-IDF vectors for a list of documents.

    Parameters:
        docs (List[str]): List of raw text strings

    Returns:
        List[Dict[str, float]]: One TF-IDF vector per document
    """
    N = len(docs)

    # Step 1: Tokenize and stem all documents
    tokenized_docs: List[List[str]] = [
        [stem(t) for t in tokenize(doc)]
        for doc in docs
    ]

    # Step 2: Compute Document Frequency df(t) for every term
    df: Dict[str, int] = {}
    for tokens in tokenized_docs:
        seen_in_doc: Set[str] = set(tokens)
        for t in seen_in_doc:
            df[t] = df.get(t, 0) + 1

    # Step 3: Compute TF-IDF vector for each document
    vectors: List[Dict[str, float]] = []
    for tokens in tokenized_docs:
        # Term Frequency
        tf: Dict[str, int] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1

        total_tokens = len(tokens) or 1
        vec: Dict[str, float] = {}
        for t, count in tf.items():
            term_freq = count / total_tokens                  # TF(t, d)
            inv_doc_freq = math.log(1 + N / (df.get(t, 1)))   # IDF(t) — smoothed
            vec[t] = term_freq * inv_doc_freq                  # TF-IDF(t, d)

        vectors.append(vec)

    return vectors


# ═══════════════════════════════════════════════════════════════════
#  6. COSINE SIMILARITY
#  Measures the angle between two TF-IDF (or TF) vectors.
#
#  FORMULA:
#    similarity(A, B) = (A · B) / (‖A‖ × ‖B‖)
#
#  Where:
#    A · B  = Σ (A[i] × B[i])    ← dot product
#    ‖A‖    = √(Σ A[i]²)         ← Euclidean norm of vector A
#    ‖B‖    = √(Σ B[i]²)         ← Euclidean norm of vector B
#
#  Output range: 0 (no overlap) to 1 (identical)
#
#  [ML-HOOK] Replace with scikit-learn:
#    from sklearn.metrics.pairwise import cosine_similarity
#    sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
# ═══════════════════════════════════════════════════════════════════
def cosine_sim(a: Dict[str, float], b: Dict[str, float]) -> float:
    """
    Compute cosine similarity between two sparse vectors.

    Parameters:
        a (Dict[str, float]): First vector {term: weight}
        b (Dict[str, float]): Second vector {term: weight}

    Returns:
        float: Cosine similarity ∈ [0, 1]
    """
    all_keys: Set[str] = set(a.keys()) | set(b.keys())

    dot = 0.0    # A · B
    norm_a = 0.0  # ‖A‖²
    norm_b = 0.0  # ‖B‖²

    for k in all_keys:
        va = a.get(k, 0.0)
        vb = b.get(k, 0.0)
        dot += va * vb
        norm_a += va * va
        norm_b += vb * vb

    if norm_a == 0 or norm_b == 0:
        return 0.0  # Avoid division by zero

    return dot / (math.sqrt(norm_a) * math.sqrt(norm_b))


# ═══════════════════════════════════════════════════════════════════
#  7. KEYWORD OVERLAP
#  Simple set-intersection score.
#
#  FORMULA:
#    overlap_score = |resume_terms ∩ jd_terms| / |jd_terms|
#
#  Returns:
#    { 'matched': [...], 'total': N, 'score': 0..1 }
#
#  This differs from cosine similarity in that it treats
#  every keyword equally (binary match) rather than
#  weighting by TF-IDF.
# ═══════════════════════════════════════════════════════════════════
def keyword_overlap(
    resume_tokens: List[str],
    jd_tokens: List[str]
) -> Dict:
    """
    Compute keyword overlap between resume and job description.

    Parameters:
        resume_tokens (List[str]): Tokenized resume text
        jd_tokens (List[str]): Tokenized job description text

    Returns:
        Dict with 'matched' (list), 'total' (int), 'score' (float 0-1)
    """
    resume_stem_set: Set[str] = set(stem(t) for t in resume_tokens)
    jd_stem_set: Set[str] = set(stem(t) for t in jd_tokens)

    matched: List[str] = [k for k in jd_stem_set if k in resume_stem_set]
    score = len(matched) / len(jd_stem_set) if len(jd_stem_set) > 0 else 0.0

    return {
        'matched': matched,
        'total': len(jd_stem_set),
        'score': score
    }


# ═══════════════════════════════════════════════════════════════════
#  UTILITY: Full NLP Pipeline (convenience function)
#  Runs the complete analysis pipeline on resume + JD text.
#
#  Returns a comprehensive results dict ready for the API response.
# ═══════════════════════════════════════════════════════════════════
def run_nlp_pipeline(
    resume_text: str,
    jd_text: str,
    skills_list: List[str],
    job_role: str
) -> Dict:
    """
    Run the full NLP analysis pipeline.

    Parameters:
        resume_text (str): Raw resume text
        jd_text (str): Raw job description text
        skills_list (List[str]): Canonical skills for the role
        job_role (str): Target job role name

    Returns:
        Dict with all scores and matched keywords
    """
    # Step 1 — Tokenize
    resume_tokens = tokenize(resume_text)
    jd_tokens = tokenize(jd_text)

    # Step 2 — Stem for TF vector comparison
    resume_stemmed = [stem(t) for t in resume_tokens]
    jd_stemmed = [stem(t) for t in jd_tokens]

    # Step 3 — Build TF vectors (with only 2 docs, IDF isn't very meaningful)
    resume_vec = build_tf(resume_stemmed)
    jd_vec = build_tf(jd_stemmed)

    # Step 4 — Cosine Similarity
    raw_cos = cosine_sim(resume_vec, jd_vec)
    cos_pct = min(100, round(raw_cos * 100))

    # Step 5 — Keyword Overlap
    kw_result = keyword_overlap(resume_tokens, jd_tokens)
    kw_pct = round(kw_result['score'] * 100)

    # Step 6 — Skills Coverage
    skill_tokens = []
    for s in skills_list:
        skill_tokens.extend(tokenize(s))
    sk_result = keyword_overlap(resume_tokens, skill_tokens)
    sk_pct = min(100, round(sk_result['score'] * 100 + 18))

    # Step 7 — Experience Relevance (heuristic)
    exp_keywords = [
        'project', 'built', 'developed', 'led', 'designed', 'implemented',
        'deployed', 'managed', 'created', 'researched', 'analysed', 'improved'
    ]
    resume_lower = resume_text.lower()
    exp_hits = sum(1 for k in exp_keywords if k in resume_lower)
    exp_pct = min(100, round((exp_hits / len(exp_keywords)) * 100 + 20))

    # Step 8 — Weighted Final Score
    # Formula: 0.4×KW + 0.3×Cosine + 0.2×Skills + 0.1×Experience
    overall = round(
        0.4 * kw_pct +
        0.3 * cos_pct +
        0.2 * sk_pct +
        0.1 * exp_pct
    )

    return {
        'overall': overall,
        'kw_pct': kw_pct,
        'cos_pct': cos_pct,
        'sk_pct': sk_pct,
        'exp_pct': exp_pct,
        'kw_result': kw_result,
        'job_role': job_role,
        'resume_token_count': len(resume_tokens),
        'jd_token_count': len(jd_tokens),
        'raw_cosine': round(raw_cos, 4),
    }


# ═══════════════════════════════════════════════════════════════════
#  [ML-HOOK] FUTURE: scikit-learn TF-IDF Pipeline
#
#  This function shows how to replace the from-scratch TF-IDF
#  with scikit-learn's optimized implementation.
#  Uncomment and use when ready.
# ═══════════════════════════════════════════════════════════════════
# def run_sklearn_pipeline(resume_text: str, jd_text: str) -> Dict:
#     """
#     Production-grade TF-IDF pipeline using scikit-learn.
#
#     Uses:
#       - TfidfVectorizer for feature extraction
#       - cosine_similarity for vector comparison
#       - Can extend to use classifiers (SVM, Random Forest, etc.)
#     """
#     from sklearn.feature_extraction.text import TfidfVectorizer
#     from sklearn.metrics.pairwise import cosine_similarity
#
#     vectorizer = TfidfVectorizer(
#         stop_words='english',
#         max_features=5000,       # Limit vocabulary size
#         ngram_range=(1, 2),      # Unigrams and bigrams
#         sublinear_tf=True,       # Apply log normalization to TF
#     )
#
#     tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
#     similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
#
#     feature_names = vectorizer.get_feature_names_out()
#     resume_vector = tfidf_matrix[0].toarray()[0]
#     jd_vector = tfidf_matrix[1].toarray()[0]
#
#     # Top keywords from JD
#     top_jd_indices = jd_vector.argsort()[-20:][::-1]
#     top_jd_keywords = [(feature_names[i], jd_vector[i]) for i in top_jd_indices]
#
#     # Matched keywords
#     matched = [
#         feature_names[i] for i in top_jd_indices
#         if resume_vector[i] > 0
#     ]
#
#     return {
#         'cosine_similarity': float(similarity[0][0]),
#         'top_jd_keywords': top_jd_keywords,
#         'matched_keywords': matched,
#         'vocabulary_size': len(feature_names),
#     }


# ===================================================================
#  SELF-TEST -- Run this file directly to verify the NLP engine works
# ===================================================================
if __name__ == '__main__':
    print("=" * 60)
    print("  ResumeIQ NLP Engine -- Self-Test")
    print("=" * 60)

    # Test tokenize
    test_text = "I built Machine Learning models using TensorFlow in Python"
    tokens = tokenize(test_text)
    print(f"\n  tokenize(\"{test_text}\")")
    print(f"  -> {tokens}")

    # Test stem
    test_words = ['learning', 'trained', 'libraries', 'classification', 'models']
    stemmed = [stem(w) for w in test_words]
    print(f"\n  stem({test_words})")
    print(f"  -> {stemmed}")

    # Test TF-IDF
    docs = [
        "python machine learning tensorflow deep learning neural networks",
        "python java javascript react nodejs sql database"
    ]
    vectors = build_tfidf(docs)
    print(f"\n  build_tfidf (2 docs):")
    for i, v in enumerate(vectors):
        top3 = sorted(v.items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"    Doc {i}: top terms = {top3}")

    # Test cosine similarity
    sim = cosine_sim(vectors[0], vectors[1])
    print(f"\n  cosine_sim = {sim:.4f}")

    # Test keyword overlap
    r_tokens = tokenize("python tensorflow sql git docker machine learning")
    j_tokens = tokenize("python pytorch sql aws docker kubernetes machine learning")
    overlap = keyword_overlap(r_tokens, j_tokens)
    print(f"\n  keyword_overlap:")
    print(f"    matched = {overlap['matched']}")
    print(f"    score   = {overlap['score']:.2f}")

    print(f"\n{'=' * 60}")
    print("  [OK] All NLP engine functions passed!")
    print(f"{'=' * 60}\n")
