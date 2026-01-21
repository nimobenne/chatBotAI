# AI Customer Support Chatbot

This project is a web-based AI chatbot that answers customer service questions
and escalates to a human when needed.

## Features
- Web chat UI with conversation history
- AI responses via OpenAI (fallback message if no key is set)
- Escalation guidance with email and phone contact

## Requirements
- Python 3.10+

## Setup
1. Install dependencies.

```bash
pip install -r requirements.txt
```

2. Create your environment file.

```bash
copy .env.example .env
```

3. Update `.env` with your details.

```
OPENAI_API_KEY=your_key_here
OLLAMA_MODEL=llama3.1
OLLAMA_URL=http://localhost:11434/api/chat
AGENT_NAME=Kikibot
COMPANY_NAME=Kikibot Support
ESCALATION_EMAIL=support@example.com
ESCALATION_PHONE=+1-555-0100
```

4. Start the app.

```bash
python app.py
```

5. Open the web UI.

```
http://127.0.0.1:5000
```

## Ollama (free local AI)
If you prefer to run AI locally without paying for an API key:

1. Install Ollama: https://ollama.com/download
2. Download a model:

```bash
ollama run llama3.1
```

3. Leave `OPENAI_API_KEY` empty in `.env` and keep the default OLLAMA settings.

## Project layout
- `app.py` - Flask API + HTML entrypoint
- `templates/index.html` - Web UI
- `static/styles.css` - Styling
- `static/app.js` - Chat client
- `.env.example` - Environment template
