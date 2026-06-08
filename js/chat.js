/* ═══════════════════════════════════════════════════════════════════
   ResumeIQ — Chat Module
   File: js/chat.js

   Handles the AI chatbot powered by Claude (Anthropic API).
   Injects resume analysis context so Claude gives specific,
   personalised advice rather than generic tips.
═══════════════════════════════════════════════════════════════════ */

// Conversation history — sent with every API call so Claude remembers context
let chatHistory = [];

// The system prompt injected before first API call
let systemContext = '';

/* ───────────────────────────────────────────
   buildSystemContext(result, resumeSnippet)
   Constructs the Claude system prompt using
   the user's actual analysis numbers.

   This is what makes the chatbot "smart" —
   Claude knows your exact scores and can give
   role-specific advice.
─────────────────────────────────────────── */
function buildSystemContext(result, resumeSnippet) {
  return `You are an expert career advisor and resume coach specialising in tech roles.
The user has just completed a resume analysis for the role: "${result.jobRole}".

ANALYSIS RESULTS:
  Overall match score : ${result.overall}%
  Keyword match       : ${result.kwPct}%   (weight: 40%)
  TF-IDF cosine sim   : ${result.cosPct}%  (weight: 30%)
  Skills coverage     : ${result.skPct}%   (weight: 20%)
  Experience relevance: ${result.expPct}%  (weight: 10%)

Matched keywords: ${result.kwResult.matched.slice(0, 15).join(', ')}

Resume snippet (first 400 chars):
"${resumeSnippet.substring(0, 400)}"

Your job:
  - Give specific, actionable advice referencing the actual numbers above.
  - Be encouraging but honest.
  - When suggesting skills, prioritise the missing high-weight ones.
  - Keep responses concise (3–5 sentences) unless the user asks for detail.
  - Never give generic advice — always tie it to their specific score and role.`;
}

/* ───────────────────────────────────────────
   activateChat()
   Opens chat panel and sends first bot message.
   Called from index.html button click.
─────────────────────────────────────────── */
function activateChat() {
  document.getElementById('chat-panel').classList.remove('hidden');
  setStepDone(4);

  if (chatHistory.length === 0) {
    // First greeting references actual score
    const score = window._analysisResult ? window._analysisResult.overall : '?';
    const jobRole = window._currentJob || 'this role';

    sendBotMessage(
      `Hi! 👋 I've analysed your resume for <strong>${jobRole}</strong>. ` +
      `You scored <strong>${score}%</strong> overall. ` +
      `I'm here to give you specific advice based on your actual results. What would you like to know?`
    );

    // Suggested starter questions
    setTimeout(() => {
      const qs = document.getElementById('suggested-qs');
      qs.innerHTML = '';
      [
        'What should I improve first?',
        'Which skills am I missing?',
        'How can I reach 80%+ match?',
        'Help me rewrite my summary'
      ].forEach(q => {
        const btn = document.createElement('button');
        btn.className = 'sq-btn';
        btn.textContent = q;
        btn.onclick = () => {
          document.getElementById('chat-input').value = q;
          sendMessage();
        };
        qs.appendChild(btn);
      });
    }, 600);
  }
}

/* ───────────────────────────────────────────
   sendMessage()
   1. Reads user input from textarea
   2. Appends user bubble to chat
   3. Calls Claude API with full history
   4. Displays Claude's response
─────────────────────────────────────────── */
async function sendMessage() {
  const input = document.getElementById('chat-input');
  const msg = input.value.trim();
  if (!msg) return;

  input.value = '';
  document.getElementById('suggested-qs').innerHTML = '';   // hide starter Qs
  document.getElementById('send-btn').disabled = true;

  // Add user message to chat and history
  appendUserMsg(msg);
  chatHistory.push({ role: 'user', content: msg });

  // Show typing indicator
  const typingEl = showTyping();

  try {
    /* ── Gemini API call (via backend proxy) ──
       Model:      gemini-2.0-flash (configured in server.js)
       System:     Resume analysis context (built once in activateChat)
       Messages:   Full conversation history for multi-turn memory
       The API key is stored securely in .env on the server side.
    */
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        systemContext: systemContext,
        messages: chatHistory.slice(-16)
      })
    });

    const data = await response.json();
    typingEl.remove();

    if (data.error) {
      sendBotMessage(`⚠️ API error: ${data.error.message}. Check your API key in the .env file.`);
      return;
    }

    const reply = data.candidates?.[0]?.content?.parts?.[0]?.text || 'Sorry, I could not process that.';
    sendBotMessage(reply);
    chatHistory.push({ role: 'assistant', content: reply });

  } catch (err) {
    typingEl.remove();
    sendBotMessage(
      `⚠️ Could not connect to Claude. Make sure you've added your Anthropic API key ` +
      `to js/chat.js (ANTHROPIC_API_KEY) or are running through a proxy.`
    );
    console.error('Chat error:', err);
  }

  document.getElementById('send-btn').disabled = false;
}

/* ───────────────────────────────────────────
   appendUserMsg(text)
   Renders a user chat bubble
─────────────────────────────────────────── */
function appendUserMsg(text) {
  const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const msgs = document.getElementById('chat-msgs');
  msgs.innerHTML += `
    <div class="msg user">
      <div class="msg-avatar">U</div>
      <div>
        <div class="msg-bubble">${escHtml(text)}</div>
        <div class="msg-time">${now}</div>
      </div>
    </div>`;
  msgs.scrollTop = msgs.scrollHeight;
}

/* ───────────────────────────────────────────
   sendBotMessage(text)
   Renders a bot chat bubble.
   Supports **bold** markdown syntax.
─────────────────────────────────────────── */
function sendBotMessage(text) {
  const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const msgs = document.getElementById('chat-msgs');
  const html = text
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');
  msgs.innerHTML += `
    <div class="msg bot">
      <div class="msg-avatar">AI</div>
      <div>
        <div class="msg-bubble">${html}</div>
        <div class="msg-time">${now}</div>
      </div>
    </div>`;
  msgs.scrollTop = msgs.scrollHeight;
}

/* ───────────────────────────────────────────
   showTyping()
   Renders the animated three-dot typing indicator
   Returns the DOM element so caller can remove it
─────────────────────────────────────────── */
function showTyping() {
  const msgs = document.getElementById('chat-msgs');
  const el = document.createElement('div');
  el.className = 'msg bot';
  el.innerHTML = `
    <div class="msg-avatar">AI</div>
    <div class="msg-bubble">
      <div class="typing"><span></span><span></span><span></span></div>
    </div>`;
  msgs.appendChild(el);
  msgs.scrollTop = msgs.scrollHeight;
  return el;
}
