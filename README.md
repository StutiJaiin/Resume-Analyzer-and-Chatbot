# ResumeIQ — How to Run

## Quick Start (no installation needed)

1. Unzip `resumeiq.zip`
2. Open the `resumeiq/` folder
3. Double-click `index.html`
   → Opens directly in Chrome or Edge (no server needed)

## To Use the Chatbot (Phase 4)

The chatbot uses the Groq LLM API (Llama 3.3 70B).
Open `js/chat.js` and find this line near the top of `sendMessage()`:

```
headers: { 'Content-Type': 'application/json' },
```

Add the API Key, Save the file, refresh the browser — chatbot will work.

## Testing Without a Real Resume

The app includes a demo resume (Stuti Jain's profile) as fallback.
To test the full pipeline, create a plain text file:

1. Open Notepad
2. Paste your resume text (or any text)
3. Save as `myresume.txt`
4. Upload it in Phase 2

## File Structure

```
resumeiq/
├── index.html        → Open this in browser
├── css/style.css     → All styles
├── js/
│   ├── nlp.js        → All NLP math (TF-IDF, Cosine, Stemming)
│   ├── jobs.js       → Job description profiles
│   ├── ui.js         → UI rendering
│   ├── chat.js       → Claude chatbot
│   └── app.js        → Main controller
└── docs/
    └── concepts.txt  → Full NLP concepts explanation
```

## Supported Browsers

Chrome, Edge, Firefox, Safari (any modern browser)
No server. No Node.js. No installation.
