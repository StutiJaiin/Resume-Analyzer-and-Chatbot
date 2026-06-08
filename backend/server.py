# ═══════════════════════════════════════════════════════════════════
#  ResumeIQ — Python Backend Server (Flask)
#  File: backend/server.py
#
#  ★ This is now the PRIMARY backend for ResumeIQ.
#    It serves both the frontend AND the API.
#    Node.js server.js is no longer needed.
#
#  Endpoints:
#    GET  /                 → Serve frontend (index.html)
#    POST /api/analyze      → Full NLP analysis pipeline
#    POST /api/chat         → AI chat (Groq / Llama 3.3 70B)
#    POST /api/extract      → Document text extraction
#    POST /api/ml/analyze   → [ML-HOOK] scikit-learn TF-IDF analysis
#    GET  /api/jobs         → List available job profiles
#    GET  /api/jobs/<role>  → Get specific job profile
#    GET  /api/health       → Health check
#
#  Run:
#    cd backend
#    pip install -r requirements.txt
#    python server.py
#
#  Opens at http://localhost:5000
# ═══════════════════════════════════════════════════════════════════

import os
import sys
import asyncio
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load .env from parent directory (same .env as the old Node.js server)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Import our modules
from nlp_engine import tokenize, stem, build_tf, build_tfidf, cosine_sim, keyword_overlap, run_nlp_pipeline
from job_profiles import get_job_profile, JOB_PROFILES
from doc_extractor import extract_text
from chat_handler import build_system_context, chat_with_groq, generate_suggestions

# ─── Flask App Setup ───
# Serve static files (CSS, JS, etc.) from the parent directory
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

PORT = 5000

# ─── In-memory session storage for chat ───
chat_sessions: dict = {}


# ═══════════════════════════════════════════════════════════════════
#  GET / — Serve Frontend (index.html)
#  Serves the main page — replaces the old Node.js static server
# ═══════════════════════════════════════════════════════════════════
@app.route('/')
def serve_index():
    """Serve the frontend index.html."""
    return send_from_directory(FRONTEND_DIR, 'index.html')


# ═══════════════════════════════════════════════════════════════════
#  Serve static files (CSS, JS, images, etc.)
#  Flask's static_folder handles most of this, but we add explicit
#  routes for the css/ and js/ subdirectories to be safe.
# ═══════════════════════════════════════════════════════════════════
@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'css'), filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'js'), filename)


# ═══════════════════════════════════════════════════════════════════
#  GET /api/health — Health Check
# ═══════════════════════════════════════════════════════════════════
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'service': 'ResumeIQ Python Backend',
        'version': '1.0.0',
        'mode': 'standalone (no Node.js needed)',
        'endpoints': [
            'POST /api/analyze',
            'POST /api/chat',
            'POST /api/extract',
            'POST /api/ml/analyze',
            'GET  /api/jobs',
            'GET  /api/jobs/<role>',
        ]
    })


# ═══════════════════════════════════════════════════════════════════
#  POST /api/analyze — Full NLP Analysis Pipeline
#
#  Request: multipart/form-data with:
#    file: resume.pdf/docx/txt
#    job_role: "ML Engineer"
#
#  OR JSON body:
#    { "resume_text": "...", "job_role": "ML Engineer" }
#
#  Response:
#    { overall, kw_pct, cos_pct, sk_pct, exp_pct, profile, suggestions, ... }
# ═══════════════════════════════════════════════════════════════════
@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Run the full NLP analysis pipeline on a resume."""
    try:
        resume_text = None
        job_role = None

        # Handle file upload (multipart/form-data)
        if request.files and 'file' in request.files:
            file = request.files['file']
            file_bytes = file.read()
            resume_text = extract_text(file_bytes=file_bytes, filename=file.filename)
            job_role = request.form.get('job_role', '')
        # Handle JSON body
        elif request.is_json:
            data = request.get_json()
            resume_text = data.get('resume_text', '')
            job_role = data.get('job_role', '')

        if not resume_text or len(resume_text) < 50:
            return jsonify({
                'error': 'Resume text is too short or could not be extracted. '
                         'Please upload a valid .txt, .pdf, or .docx file.'
            }), 400

        if not job_role:
            return jsonify({
                'error': 'Please provide a job_role field.'
            }), 400

        # Get job profile
        profile = get_job_profile(job_role)

        # Run NLP pipeline
        result = run_nlp_pipeline(
            resume_text=resume_text,
            jd_text=profile['description'],
            skills_list=profile['skills'],
            job_role=job_role
        )

        # Add profile info to result
        result['profile'] = {
            'role': profile['role'],
            'skills': profile['skills'],
            'sources': profile['sources'],
        }

        # Generate suggestions
        result['suggestions'] = generate_suggestions(result)

        # Store for chat context
        session_id = request.headers.get('X-Session-ID', 'default')
        chat_sessions[session_id] = {
            'result': result,
            'resume_snippet': resume_text[:400],
            'system_context': build_system_context(result, resume_text),
            'history': []
        }

        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════
#  POST /api/chat — AI Chat (Groq / Llama 3.3 70B)
#
#  Accepts the SAME format as the old Node.js server.js:
#    { "systemContext": "...", "messages": [...] }
#
#  Returns the SAME format the frontend expects:
#    { "candidates": [{ "content": { "parts": [{ "text": "..." }] } }] }
# ═══════════════════════════════════════════════════════════════════
@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle AI chat requests — compatible with frontend format."""
    try:
        data = request.get_json()

        # Frontend format (matches what chat.js sends)
        if 'systemContext' in data:
            system_context = data.get('systemContext', '')
            messages = data.get('messages', [])

            loop = asyncio.new_event_loop()
            reply = loop.run_until_complete(
                chat_with_groq(system_context, messages)
            )
            loop.close()

            # Return in the format the frontend expects
            return jsonify({
                'candidates': [{
                    'content': {
                        'parts': [{'text': reply}]
                    }
                }]
            })

        # Alternative: simple message format
        message = data.get('message', '')
        session_id = data.get('session_id', 'default')

        if not message:
            return jsonify({'error': 'message field is required'}), 400

        session = chat_sessions.get(session_id, {})
        system_context = session.get('system_context', 'You are a helpful career advisor.')
        history = session.get('history', [])

        history.append({'role': 'user', 'content': message})

        loop = asyncio.new_event_loop()
        reply = loop.run_until_complete(
            chat_with_groq(system_context, history)
        )
        loop.close()

        history.append({'role': 'assistant', 'content': reply})
        if session_id in chat_sessions:
            chat_sessions[session_id]['history'] = history

        return jsonify({
            'reply': reply,
            'session_id': session_id
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════
#  POST /api/extract — Document Text Extraction
# ═══════════════════════════════════════════════════════════════════
@app.route('/api/extract', methods=['POST'])
def extract():
    """Extract text from an uploaded document."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        file_bytes = file.read()
        text = extract_text(file_bytes=file_bytes, filename=file.filename)

        return jsonify({
            'filename': file.filename,
            'text': text,
            'char_count': len(text),
            'word_count': len(text.split()),
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════
#  POST /api/ml/analyze — scikit-learn TF-IDF Analysis
# ═══════════════════════════════════════════════════════════════════
@app.route('/api/ml/analyze', methods=['POST'])
def ml_analyze():
    """Advanced ML-based analysis using scikit-learn."""
    try:
        data = request.get_json()
        resume_text = data.get('resume_text', '')
        jd_text = data.get('jd_text', '')
        job_role = data.get('job_role', '')

        if not resume_text:
            return jsonify({'error': 'resume_text is required'}), 400

        if not jd_text and job_role:
            profile = get_job_profile(job_role)
            jd_text = profile['description']

        if not jd_text:
            return jsonify({'error': 'Either jd_text or job_role is required'}), 400

        try:
            from ml_pipeline import sklearn_tfidf_analysis, extract_features
            sklearn_result = sklearn_tfidf_analysis(resume_text, jd_text)
            features = extract_features(resume_text, jd_text)
            return jsonify({
                'sklearn_analysis': sklearn_result,
                'features': features,
            })
        except ImportError:
            return jsonify({
                'error': 'scikit-learn not installed. Run: pip install scikit-learn',
                'fallback': 'Using from-scratch NLP engine instead.'
            }), 501

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════
#  GET /api/jobs — List All Available Job Profiles
# ═══════════════════════════════════════════════════════════════════
@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all available job profiles."""
    return jsonify({
        'jobs': [
            {
                'role': key,
                'skill_count': len(profile['skills']),
                'skills': profile['skills']
            }
            for key, profile in JOB_PROFILES.items()
        ]
    })


# ═══════════════════════════════════════════════════════════════════
#  GET /api/jobs/<role> — Get Specific Job Profile
# ═══════════════════════════════════════════════════════════════════
@app.route('/api/jobs/<role>', methods=['GET'])
def get_job(role: str):
    """Get a specific job profile by role name."""
    profile = get_job_profile(role)
    return jsonify(profile)


# ═══════════════════════════════════════════════════════════════════
#  START SERVER
# ═══════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print(f"""
  ============================================================
  ResumeIQ Python Backend -- RUNNING
  ============================================================

  Frontend:   http://localhost:{PORT}
  API:        http://localhost:{PORT}/api/analyze
  Chat:       http://localhost:{PORT}/api/chat
  ML:         http://localhost:{PORT}/api/ml/analyze
  Jobs:       http://localhost:{PORT}/api/jobs
  Health:     http://localhost:{PORT}/api/health

  ------------------------------------------------------------
  Node.js server.js is NO LONGER NEEDED.
  This Python server handles everything.
  ------------------------------------------------------------
""")

    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=True
    )
