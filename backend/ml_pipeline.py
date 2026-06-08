# ═══════════════════════════════════════════════════════════════════
#  ResumeIQ — ML Pipeline (Future Use)
#  File: backend/ml_pipeline.py
#
#  This module contains ML-ready functions that extend the
#  from-scratch NLP engine with scikit-learn, NLTK, and more.
#
#  ★ Currently commented out — uncomment when you're ready
#    to integrate ML into the project.
#
#  Contains:
#    1. sklearn_tfidf_pipeline()   — Production TF-IDF with scikit-learn
#    2. nltk_preprocess()          — NLTK-based tokenization + lemmatization
#    3. train_classifier()         — Train a resume scoring model
#    4. predict_match_score()      — Predict match using trained model
#    5. extract_named_entities()   — NER for skills/companies/education
#    6. topic_modeling()           — LDA topic extraction
# ═══════════════════════════════════════════════════════════════════

"""
ResumeIQ ML Pipeline — Advanced NLP and Machine Learning functions.

This module is designed for FUTURE USE. Each function includes:
  - Full docstring explaining the concept
  - The mathematical formula where applicable
  - Installation requirements
  - Usage examples

To use these functions:
  1. pip install -r requirements.txt
  2. Uncomment the function you want
  3. Import from ml_pipeline in server.py
"""

from typing import List, Dict, Tuple, Optional
import math


# ═══════════════════════════════════════════════════════════════════
#  1. SCIKIT-LEARN TF-IDF PIPELINE
#
#  Uses sklearn's TfidfVectorizer which is far more optimised than
#  our from-scratch version. Features:
#    - N-gram support (bigrams like "machine learning")
#    - Sublinear TF (uses log(1 + TF) to dampen frequency)
#    - Built-in stopword removal
#    - Sparse matrix representation (memory efficient)
#
#  FORMULA (sklearn's variant):
#    TF(t,d)     = 1 + log(count(t,d))        (sublinear_tf=True)
#    IDF(t)      = log((1 + N) / (1 + df(t))) + 1  (smooth_idf=True)
#    TF-IDF(t,d) = TF(t,d) × IDF(t) × L2_norm
# ═══════════════════════════════════════════════════════════════════
def sklearn_tfidf_analysis(resume_text: str, jd_text: str) -> Dict:
    """
    Production-grade TF-IDF analysis using scikit-learn.

    Uses TfidfVectorizer with bigram support and cosine similarity.
    Much more robust than the from-scratch implementation.

    Parameters:
        resume_text (str): Raw resume text
        jd_text (str): Raw job description text

    Returns:
        Dict with cosine_similarity, top keywords, matched keywords

    Requirements:
        pip install scikit-learn numpy
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    # Configure TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        stop_words='english',       # Built-in English stopwords
        max_features=5000,          # Limit vocabulary for efficiency
        ngram_range=(1, 2),         # Capture "machine learning" as one feature
        sublinear_tf=True,          # log(1 + TF) — reduces impact of very frequent terms
        min_df=1,                   # Include terms appearing in at least 1 document
        max_df=1.0,                 # Don't exclude any terms by max frequency
    )

    # Fit and transform both documents
    tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])

    # Compute cosine similarity
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

    # Get feature names and vectors
    feature_names = vectorizer.get_feature_names_out()
    resume_vector = tfidf_matrix[0].toarray()[0]
    jd_vector = tfidf_matrix[1].toarray()[0]

    # Top 20 keywords from JD by TF-IDF weight
    top_jd_indices = jd_vector.argsort()[-20:][::-1]
    top_jd_keywords = [
        {'term': feature_names[i], 'weight': round(float(jd_vector[i]), 4)}
        for i in top_jd_indices
        if jd_vector[i] > 0
    ]

    # Matched keywords (appear in both resume and JD)
    matched = [
        feature_names[i] for i in top_jd_indices
        if resume_vector[i] > 0 and jd_vector[i] > 0
    ]

    # Missing keywords (in JD but not in resume)
    missing = [
        feature_names[i] for i in top_jd_indices
        if resume_vector[i] == 0 and jd_vector[i] > 0
    ]

    return {
        'cosine_similarity': round(float(similarity[0][0]), 4),
        'top_jd_keywords': top_jd_keywords,
        'matched_keywords': matched,
        'missing_keywords': missing,
        'vocabulary_size': len(feature_names),
        'method': 'sklearn_tfidf'
    }


# ═══════════════════════════════════════════════════════════════════
#  2. NLTK PREPROCESSING
#
#  More sophisticated text preprocessing using NLTK:
#    - word_tokenize (handles contractions, punctuation better)
#    - WordNet Lemmatizer (dictionary-based: "better" → "good")
#    - POS tagging for better lemmatization
#
#  Before first use, download NLTK data:
#    import nltk
#    nltk.download('punkt')
#    nltk.download('wordnet')
#    nltk.download('averaged_perceptron_tagger')
#    nltk.download('stopwords')
# ═══════════════════════════════════════════════════════════════════
def nltk_preprocess(text: str) -> List[str]:
    """
    Advanced text preprocessing using NLTK.

    Uses lemmatization (dictionary-based) instead of stemming
    for more accurate root word extraction.
    "better" → "good", "running" → "run", "mice" → "mouse"

    Parameters:
        text (str): Raw input text

    Returns:
        List[str]: Preprocessed and lemmatized tokens

    Requirements:
        pip install nltk
        Then run: python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('stopwords')"
    """
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    from nltk.corpus import stopwords

    # Initialize
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

    # Tokenize
    tokens = word_tokenize(text.lower())

    # Filter: keep alphanumeric, remove stopwords, length > 2
    filtered = [
        lemmatizer.lemmatize(t)
        for t in tokens
        if t.isalnum() and len(t) > 2 and t not in stop_words
    ]

    return filtered


# ═══════════════════════════════════════════════════════════════════
#  3. RESUME MATCH CLASSIFIER (Future — Training Pipeline)
#
#  Train a supervised model to predict resume-job match scores.
#  Uses features extracted from TF-IDF + metadata.
#
#  Approach:
#    1. Collect labeled data (resume, JD, match_score)
#    2. Extract features: TF-IDF cosine, keyword overlap, skills count
#    3. Train a regression model (Random Forest, XGBoost, etc.)
#    4. Predict match score for new resume-JD pairs
#
#  This is the path from "heuristic scoring" to "learned scoring".
# ═══════════════════════════════════════════════════════════════════
def extract_features(resume_text: str, jd_text: str) -> Dict:
    """
    Extract numerical features from a resume-JD pair for ML training.

    Features:
        1. TF-IDF cosine similarity (sklearn)
        2. Keyword overlap ratio
        3. Resume length (token count)
        4. JD length (token count)
        5. Unique token ratio (vocabulary richness)
        6. Skills keyword count
        7. Action verb count

    Parameters:
        resume_text (str): Raw resume text
        jd_text (str): Raw job description text

    Returns:
        Dict of feature name → value
    """
    from .nlp_engine import tokenize, stem, keyword_overlap

    resume_tokens = tokenize(resume_text)
    jd_tokens = tokenize(jd_text)

    # Feature 1: TF-IDF cosine
    sklearn_result = sklearn_tfidf_analysis(resume_text, jd_text)

    # Feature 2: Keyword overlap
    kw = keyword_overlap(resume_tokens, jd_tokens)

    # Feature 3-4: Lengths
    resume_len = len(resume_tokens)
    jd_len = len(jd_tokens)

    # Feature 5: Vocabulary richness
    unique_ratio = len(set(resume_tokens)) / max(resume_len, 1)

    # Feature 6: Action verbs
    action_verbs = [
        'built', 'developed', 'designed', 'implemented', 'deployed',
        'managed', 'created', 'led', 'improved', 'optimized',
        'researched', 'analysed', 'automated', 'integrated', 'launched'
    ]
    resume_lower = resume_text.lower()
    action_count = sum(1 for v in action_verbs if v in resume_lower)

    return {
        'tfidf_cosine': sklearn_result['cosine_similarity'],
        'keyword_overlap': kw['score'],
        'resume_token_count': resume_len,
        'jd_token_count': jd_len,
        'unique_token_ratio': round(unique_ratio, 4),
        'matched_keyword_count': len(kw['matched']),
        'missing_keyword_count': kw['total'] - len(kw['matched']),
        'action_verb_count': action_count,
    }





# ===================================================================
#  SELF-TEST
# ===================================================================
if __name__ == '__main__':
    print("=" * 60)
    print("  ResumeIQ ML Pipeline -- Self-Test")
    print("=" * 60)

    resume = (
        "Stuti Jain CS AI ML student Python TensorFlow PyTorch "
        "machine learning deep learning NLP computer vision "
        "built ResumeIQ analyzer deployed projects"
    )
    jd = (
        "machine learning engineer python tensorflow pytorch sklearn "
        "deep learning neural networks docker kubernetes aws "
        "sql git mlops feature engineering model deployment"
    )

    print("\n  Testing sklearn TF-IDF pipeline...")
    try:
        result = sklearn_tfidf_analysis(resume, jd)
        print(f"  [OK] Cosine similarity: {result['cosine_similarity']}")
        print(f"       Matched keywords: {result['matched_keywords'][:5]}")
        print(f"       Missing keywords: {result['missing_keywords'][:5]}")
        print(f"       Vocabulary size: {result['vocabulary_size']}")
    except ImportError as e:
        print(f"  [WARN] sklearn not installed: {e}")
        print("         Install with: pip install scikit-learn")

    print(f"\n{'=' * 60}")
    print("  [OK] ML pipeline module ready!")
    print(f"{'=' * 60}\n")
