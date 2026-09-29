# RecallIQ

AI customer support that remembers what fixed it last time.

Built for Hack With Hyderabad 3.0.

## The problem

Customers repeat their story every time they contact support, and support AI gives the same generic answers. Past problems and the fixes that worked are never remembered.

## The solution

Before RecallIQ answers, it recalls the customer's history from Hindsight and uses it to write a personalised reply. The customer then confirms whether the fix worked. Only a confirmed fix is stored, so the memory stays trustworthy and support gets better with every resolved ticket.

## The loop

Recall, Understand, Resolve, Verify, Remember.

1. Recall: search Hindsight for this customer's past issues.
2. Understand: build context from the recalled history.
3. Resolve: answer using the fix that worked before.
4. Verify: the customer confirms the fix worked.
5. Remember: the confirmed outcome is stored in Hindsight.

## Demo

1. Choose a customer and save their past tickets.
2. Report an issue. The page shows the answer without memory next to the answer with memory, and the recalled memories as cards in the customer file.
3. Click "It worked". The confirmed fix is stored in Hindsight.
4. Report a related issue. RecallIQ recalls the fix it just learned.

## Architecture

Browser, then Flask, then Hindsight recall, then Groq (openai/gpt-oss-120b) for the answer. When the customer confirms, the outcome is retained in Hindsight.

## How Hindsight is used

- One memory bank per customer and demo session.
- Recall runs before every answer, and the recalled memories are shown on screen as Hindsight returns them.
- Retain runs only after the customer confirms the fix.

## Files

- `app.py`: Flask server and API routes
- `memory.py`: Hindsight recall and retain, called safely from Flask
- `page.html`: the dashboard
- `support_agent.py`: the original command line version and the shared Groq and Hindsight setup

## Tech

Python, Flask, Hindsight, Groq, HTML, CSS and JavaScript.

## Run it

```
git clone https://github.com/devsharonn/recalliq.git
cd recalliq
pip install -r requirements.txt
copy .env.example .env
```

Put your Hindsight and Groq keys in `.env`, then start the app:

```
py app.py
```

Open http://127.0.0.1:5077

## Honest limits

- The demo customers are sample data.
- If a customer has no history, RecallIQ says so and the ticket goes to a human agent.
- Hindsight needs about 15 to 30 seconds to process newly stored memories.

## Team

Add team name and members here.
