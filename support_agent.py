"""
RecallIQ — AI Customer Support That Remembers
================================================
Built by: [TYPE YOUR NAME HERE]

Core loop: recall relevant history from Hindsight -> answer with Groq -> retain
the new interaction.

USAGE:
    py support_agent.py seed --customer alex
    py support_agent.py chat --customer alex

DEMO SCRIPT (the "before/after" moment):
    - First run `chat` WITHOUT seeding -> agent is generic, asks basic questions.
    - Then run `seed`, then `chat` again -> agent instantly recalls the
      customer's past issue and skips straight to the fix.
"""

import sys
import argparse

from hindsight_client import Hindsight
from groq import Groq

# ---- Your API keys go here ----
HINDSIGHT_API_KEY = "your-hindsight-key-here"
GROQ_API_KEY = "your-groq-key-here"
GROQ_MODEL = "openai/gpt-oss-120b"
# --------------------------------

hindsight = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=HINDSIGHT_API_KEY,
)

groq_client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = (
    "You are RecallIQ, a customer support agent. Use the CUSTOMER HISTORY below "
    "if it's relevant to answer the customer's message. If there is no history, "
    "just be a normal, friendly, but slightly generic support agent — ask "
    "clarifying questions like you've never spoken to them before. If there IS "
    "history, reference it specifically and naturally, the way a human who "
    "remembered the customer would — do not repeat the same clarifying questions."
)


def bank_id_for(customer: str) -> str:
    return f"support-{customer}"


def ensure_bank(bank_id):
    try:
        hindsight.create_bank(bank_id=bank_id, name=bank_id)
    except Exception:
        pass  # bank already exists, that's fine


def seed_history(customer: str):
    """Seed a few fake past tickets for this customer, so the agent has
    something to recall in the 'after' half of your demo."""
    bank_id = bank_id_for(customer)
    ensure_bank(bank_id)

    fake_tickets = [
        f"Customer {customer} contacted support on a previous occasion about "
        f"repeated login failures on the mobile app after a password reset. "
        f"Root cause was a stale auth token cache. Resolved by having them "
        f"clear the app's local storage and log in again.",

        f"Customer {customer} previously reported that exported CSV reports "
        f"were missing the last column of data. This was a known bug in the "
        f"export formatter that has since been patched in a later release.",

        f"Customer {customer} uses the Pro plan and has previously asked "
        f"about increasing their API rate limit for a batch-processing job "
        f"they run monthly.",
    ]
    for ticket in fake_tickets:
        hindsight.retain(bank_id=bank_id, content=ticket)
        print(f"[retained] {ticket[:70]}...")

    print(f"\nSeeded {len(fake_tickets)} past tickets for '{customer}'.")


def chat(customer: str):
    """Interactive chat loop demonstrating recall + retain in action."""
    bank_id = bank_id_for(customer)
    ensure_bank(bank_id)
    print(f"RecallIQ — chatting as customer '{customer}'. Type 'quit' to exit.\n")

    while True:
        user_msg = input("Customer: ").strip()
        if user_msg.lower() in ("quit", "exit"):
            break
        if not user_msg:
            continue

        # 1. RECALL — pull anything relevant from past interactions
        recalled = hindsight.recall(bank_id=bank_id, query=user_msg)
        history_text = "\n".join(f"- {m.text}" for m in recalled.results) or "(none)"

        # 2. RESPOND — ask Groq, grounded in recalled memory
        completion = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "system", "content": f"CUSTOMER HISTORY:\n{history_text}"},
                {"role": "user", "content": user_msg},
            ],
        )
        reply = completion.choices[0].message.content
        print(f"RecallIQ: {reply}\n")

        # 3. RETAIN — store this new interaction for next time
        hindsight.retain(
            bank_id=bank_id,
            content=f"Customer said: {user_msg}\nAgent replied: {reply}",
        )


def main():
    parser = argparse.ArgumentParser(description="RecallIQ — AI Customer Support That Remembers")
    subparsers = parser.add_subparsers(dest="command", required=True)

    seed_parser = subparsers.add_parser("seed", help="Seed fake ticket history")
    seed_parser.add_argument("--customer", required=True)

    chat_parser = subparsers.add_parser("chat", help="Chat with the agent")
    chat_parser.add_argument("--customer", required=True)

    args = parser.parse_args()

    if not HINDSIGHT_API_KEY or HINDSIGHT_API_KEY == "your-hindsight-key-here":
        print("ERROR: Set HINDSIGHT_API_KEY near the top of this file.")
        sys.exit(1)
    if not GROQ_API_KEY or GROQ_API_KEY == "your-groq-key-here":
        print("ERROR: Set GROQ_API_KEY near the top of this file.")
        sys.exit(1)

    if args.command == "seed":
        seed_history(args.customer)
    elif args.command == "chat":
        chat(args.customer)


if __name__ == "__main__":
    main()
