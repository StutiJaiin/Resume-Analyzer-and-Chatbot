# ═══════════════════════════════════════════════════════════════════
#  ResumeIQ — Chat Module (Python)
#  File: backend/chat_handler.py
#
#  Handles AI chat integration — mirrors js/chat.js logic.
#  Currently uses Groq API (Llama 3.3 70B) — free and fast.
#
#  [ML-HOOK] Future: swap in OpenAI, Anthropic, or local LLMs
# ═══════════════════════════════════════════════════════════════════

import os
from typing import List, Dict, Optional


def build_system_context(
    result: Dict,
    resume_snippet: str
) -> str:
    """
    Constructs the system prompt using the user's actual analysis numbers.
    This is what makes the chatbot "smart" — it knows exact scores
    and gives role-specific advice.

    Parameters:
        result (Dict): Analysis results from run_nlp_pipeline()
        resume_snippet (str): First 400 chars of the resume text

    Returns:
        str: System prompt for the LLM
    """
    return f"""You are an expert career advisor and resume coach specialising in tech roles.
The user has just completed a resume analysis for the role: "{result['job_role']}".

ANALYSIS RESULTS:
  Overall match score : {result['overall']}%
  Keyword match       : {result['kw_pct']}%   (weight: 40%)
  TF-IDF cosine sim   : {result['cos_pct']}%  (weight: 30%)
  Skills coverage     : {result['sk_pct']}%   (weight: 20%)
  Experience relevance: {result['exp_pct']}%  (weight: 10%)

Matched keywords: {', '.join(result['kw_result']['matched'][:15])}

Resume snippet (first 400 chars):
"{resume_snippet[:400]}"

Your job:
  - Give specific, actionable advice referencing the actual numbers above.
  - Be encouraging but honest.
  - When suggesting skills, prioritise the missing high-weight ones.
  - Keep responses concise (3–5 sentences) unless the user asks for detail.
  - Never give generic advice — always tie it to their specific score and role."""


async def chat_with_groq(
    system_context: str,
    messages: List[Dict[str, str]],
    api_key: str = None
) -> str:
    """
    Send a chat request to the Groq API (Llama 3.3 70B).

    Parameters:
        system_context (str): System prompt with analysis context
        messages (List[Dict]): Conversation history [{role, content}, ...]
        api_key (str): Groq API key (falls back to env var)

    Returns:
        str: The AI's response text
    """
    api_key = api_key or os.getenv('GROQ_API_KEY')

    if not api_key or api_key == 'YOUR_GROQ_KEY_HERE':
        return "⚠️ No API key configured. Add your Groq API key to the .env file."

    try:
        from groq import Groq

        client = Groq(api_key=api_key)

        # Build messages array with system prompt
        api_messages = [
            {"role": "system", "content": system_context}
        ]
        # Add conversation history (last 16 messages)
        for msg in messages[-16:]:
            api_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Call Groq API (Llama 3.3 70B — free tier)
        chat_completion = client.chat.completions.create(
            messages=api_messages,
            model="llama-3.3-70b-versatile",
            max_tokens=1000,
        )

        return chat_completion.choices[0].message.content

    except ImportError:
        # Fallback: use raw HTTP if groq SDK not installed
        return await _chat_with_groq_http(system_context, messages, api_key)
    except Exception as e:
        return f"⚠️ Groq API error: {str(e)}"


async def _chat_with_groq_http(
    system_context: str,
    messages: List[Dict[str, str]],
    api_key: str
) -> str:
    """
    Fallback: raw HTTP call to Groq API without SDK.
    Uses the same OpenAI-compatible format as server.js.
    """
    import json
    from urllib.request import Request, urlopen

    api_messages = [
        {"role": "system", "content": system_context}
    ]
    for msg in messages[-16:]:
        api_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "max_tokens": 1000,
        "messages": api_messages
    }).encode('utf-8')

    req = Request(
        'https://api.groq.com/openai/v1/chat/completions',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        },
        method='POST'
    )

    try:
        with urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if 'error' in data:
                return f"⚠️ API error: {data['error'].get('message', 'Unknown error')}"
            return data['choices'][0]['message']['content']
    except Exception as e:
        return f"⚠️ Failed to reach Groq API: {str(e)}"


def generate_suggestions(result: Dict) -> List[Dict]:
    """
    Generate improvement suggestions based on analysis results.
    Mirrors the logic from js/ui.js → renderSuggestions().

    Parameters:
        result (Dict): Analysis results from run_nlp_pipeline()

    Returns:
        List of suggestion dicts with level, title, body
    """
    job = result['job_role']
    suggestions = []

    if result['kw_pct'] < 60:
        suggestions.append({
            'level': 'high',
            'title': 'Add missing keywords',
            'body': (
                f"Include missing keywords from the job description. "
                f"ATS systems filter by exact keyword matches before "
                f"a human ever reads your resume."
            )
        })

    if result['cos_pct'] < 55:
        suggestions.append({
            'level': 'high',
            'title': 'Mirror job-description language',
            'body': (
                f'Your vocabulary diverges from how "{job}" roles are described. '
                f'Reread 5–10 JD postings and adopt their exact phrasing in '
                f'your bullet points.'
            )
        })

    if result['sk_pct'] < 70:
        suggestions.append({
            'level': 'med',
            'title': 'Expand your skills section',
            'body': (
                f"Add side projects, online courses, or certifications "
                f"that demonstrate missing skills for the {job} role."
            )
        })

    suggestions.append({
        'level': 'med',
        'title': 'Quantify your impact',
        'body': (
            'Add numbers to every bullet: "Improved model accuracy by 12%", '
            '"Reduced pipeline runtime by 3 hours", '
            '"Led a team of 4 engineers".'
        )
    })

    suggestions.append({
        'level': 'low',
        'title': 'Tailor your summary',
        'body': (
            f'Open with a 2-line summary that explicitly mentions "{job}" '
            f'and your top 2 relevant skills. Recruiters spend 6 seconds '
            f'on first read.'
        )
    })

    return suggestions
