/* ═══════════════════════════════════════════════════════════════════
   ResumeIQ — Express Backend Server
   
   Serves the frontend AND proxies AI chat calls through Groq API.
   Groq is free, fast, and has generous rate limits (14,400 req/day).
═══════════════════════════════════════════════════════════════════ */

require('dotenv').config();
const express = require('express');
const path    = require('path');

const app  = express();
const PORT = 3000;

// Parse JSON bodies
app.use(express.json());

// Serve all static frontend files (HTML, CSS, JS) with NO caching
app.use(express.static(path.join(__dirname), {
  etag: false,
  lastModified: false,
  setHeaders: (res) => {
    res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate');
    res.setHeader('Pragma', 'no-cache');
    res.setHeader('Expires', '0');
  }
}));

/* ───────────────────────────────────────────
   POST /api/chat
   Proxies chat requests to Groq API.
   Groq uses OpenAI-compatible format, making it simple.
   Model: llama-3.3-70b-versatile (free, powerful)
─────────────────────────────────────────── */
app.post('/api/chat', async (req, res) => {
  const apiKey = process.env.GROQ_API_KEY;

  if (!apiKey || apiKey === 'YOUR_GROQ_KEY_HERE') {
    return res.json({
      error: { message: 'No API key configured. Add your Groq API key to the .env file.' }
    });
  }

  try {
    const { systemContext, messages } = req.body;

    const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: 'llama-3.3-70b-versatile',
        max_tokens: 1000,
        messages: [
          { role: 'system', content: systemContext || '' },
          ...messages.map(msg => ({
            role: msg.role,
            content: msg.content
          }))
        ]
      })
    });

    const data = await response.json();

    // Convert Groq/OpenAI format to what frontend expects
    if (data.error) {
      res.json({ error: { message: data.error.message } });
    } else {
      const reply = data.choices?.[0]?.message?.content || 'Sorry, I could not process that.';
      // Send in a format the frontend can parse
      res.json({
        candidates: [{
          content: {
            parts: [{ text: reply }]
          }
        }]
      });
    }

  } catch (err) {
    console.error('Groq proxy error:', err);
    res.status(500).json({
      error: { message: 'Backend failed to reach Groq API: ' + err.message }
    });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`\n  ✅ ResumeIQ server running at: http://localhost:${PORT}\n`);
  console.log(`  Frontend: http://localhost:${PORT}`);
  console.log(`  Chat API: http://localhost:${PORT}/api/chat (Groq / Llama 3.3 70B)\n`);
});
