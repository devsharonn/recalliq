import os
import secrets
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, request, jsonify

import memory
from support_agent import groq_client, GROQ_MODEL, SYSTEM_PROMPT

app = Flask(__name__)

POOL = ThreadPoolExecutor(max_workers=4)
STYLE = " Reply in plain text, no markdown, under 90 words."

# Every demo session gets its own set of memory banks, so old test data never leaks in.
SESSION = secrets.token_hex(2)
READY = set()

TICKETS = [
    "Customer {c} contacted support about repeated login failures on the mobile app after a password reset. Root cause was a stale auth token cache. Resolved by clearing the app local storage and logging in again.",
    "Customer {c} reported exported CSV reports missing the last column. Known export formatter bug, fixed by a patch.",
    "Customer {c} uses the Pro plan and asked about a higher API rate limit for a monthly batch job.",
]


def clean(name):
    return (name or "").strip().lower()


def bank(name):
    return SESSION + "-" + clean(name)


def ensure(b):
    if b not in READY:
        memory.ensure_bank(b)
        READY.add(b)


def ask(history_text, msg):
    kwargs = dict(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT + STYLE},
            {"role": "system", "content": "CUSTOMER HISTORY:\n" + history_text},
            {"role": "user", "content": msg},
        ],
    )
    try:
        # low reasoning effort answers faster; fall back if this version does not accept it
        c = groq_client.chat.completions.create(reasoning_effort="low", **kwargs)
    except Exception:
        c = groq_client.chat.completions.create(**kwargs)
    return c.choices[0].message.content


@app.post("/api/new-session")
def new_session():
    global SESSION
    SESSION = secrets.token_hex(2)
    READY.clear()
    return jsonify(ok=True, session=SESSION)


@app.post("/api/seed")
def seed():
    try:
        name = clean(request.json.get("customer"))
        b = bank(name)
        ensure(b)
        tickets = request.json.get("tickets") or [t.format(c=name) for t in TICKETS]
        list(POOL.map(lambda t: memory.retain(b, t), tickets))
        return jsonify(ok=True, count=len(tickets))
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.post("/api/chat")
def chat():
    try:
        name = clean(request.json.get("customer"))
        msg = request.json.get("message", "").strip()
        b = bank(name)
        plain = POOL.submit(ask, "(none)", msg)  # does not need memory, so start it right away
        ensure(b)
        mems = memory.recall(b, msg)
        history = "\n".join("- " + m["text"] for m in mems) or "(none)"
        with_memory = POOL.submit(ask, history, msg)
        return jsonify(
            memories=mems,
            reply_plain=plain.result(),
            reply_memory=with_memory.result(),
        )
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.post("/api/resolve")
def resolve():
    try:
        d = request.json
        name = clean(d.get("customer"))
        if not d.get("worked"):
            return jsonify(retained=False)
        text = (
            "Verified support resolution for customer " + name + ". "
            "Issue reported: " + d["message"] + " "
            "Fix that worked: " + d["reply"][:600] + " "
            "Outcome: the customer confirmed this fix solved the problem."
        )
        memory.retain(bank(name), text)
        return jsonify(retained=True, text=text)
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.get("/")
def home():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "page.html"), encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    app.run(port=5077, debug=False)
