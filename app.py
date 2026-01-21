import os
from dataclasses import dataclass
from typing import Any

import requests
from flask import Flask, jsonify, render_template, request

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency at runtime
    load_dotenv = None

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency at runtime
    OpenAI = None

if load_dotenv:
    load_dotenv()

app = Flask(__name__)

assistant_name = os.environ.get("AGENT_NAME", "Kikibot")
company_name = os.environ.get("COMPANY_NAME", "Kikibot Support")
support_email = os.environ.get("ESCALATION_EMAIL", "support@example.com")
support_phone = os.environ.get("ESCALATION_PHONE", "+1-555-0100")
openai_model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
ollama_model = os.environ.get("OLLAMA_MODEL", "llama3.1")
ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")
openai_api_key = os.environ.get("OPENAI_API_KEY")

openai_client = OpenAI(api_key=openai_api_key) if OpenAI and openai_api_key else None


@dataclass
class ChatTurn:
    role: str
    content: str


def build_system_prompt() -> str:
    return (
        "You are a helpful customer service chatbot. "
        "Resolve common issues, ask clarifying questions, and collect key details. "
        "If the user needs human help, respond with an escalation plan, including "
        f"{support_email} and {support_phone}. Keep replies concise and friendly. "
        "Format responses with short paragraphs and bullet lists when helpful."
    )


def fetch_ollama_reply(messages: list[dict[str, str]]) -> str:
    payload = {
        "model": ollama_model,
        "messages": messages,
        "stream": False,
    }
    response = requests.post(ollama_url, json=payload, timeout=30)
    response.raise_for_status()
    data: dict[str, Any] = response.json()
    message = data.get("message", {})
    content = message.get("content", "")
    return str(content).strip()


def generate_reply(history: list[ChatTurn], user_message: str) -> str:
    messages: list[dict[str, str]] = [{"role": "system", "content": build_system_prompt()}]
    for turn in history:
        messages.append({"role": turn.role, "content": turn.content})
    messages.append({"role": "user", "content": user_message})

    if openai_client:
        completion = openai_client.chat.completions.create(
            model=openai_model,
            messages=messages,
            max_tokens=220,
            temperature=0.4,
        )
        reply = completion.choices[0].message.content or ""
        reply = reply.strip() or "Could you share more details?"
        return reply

    try:
        reply = fetch_ollama_reply(messages)
        return reply or "Could you share more details?"
    except requests.RequestException:
        return (
            "Thanks for reaching out. I can help with account access, billing, and "
            "product questions. If you need a human, I can escalate to "
            f"{support_email}. What can I help with today?"
        )


@app.route("/")
def index() -> str:
    return render_template(
        "index.html",
        assistant_name=assistant_name,
        company_name=company_name,
    )


@app.route("/api/chat", methods=["POST"])
def chat() -> tuple[str, int] | tuple[dict[str, str], int]:
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()
    history_payload = payload.get("history", [])

    if not message:
        return {"error": "Message is required."}, 400

    history: list[ChatTurn] = []
    for item in history_payload:
        role = str(item.get("role", "")).strip()
        content = str(item.get("content", "")).strip()
        if role in {"user", "assistant"} and content:
            history.append(ChatTurn(role=role, content=content))

    reply = generate_reply(history, message)
    return jsonify({"reply": reply})


@app.route("/health")
def health() -> str:
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
