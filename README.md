
# RecallIQ — AI Customer Support That Remembers

Built by devsharonn for HackWithHyderabad 3.0.

RecallIQ is a customer support agent that remembers past customer issues and resolutions using Hindsight (long-term memory for AI agents), so customers never have to repeat themselves.

## How it works

1. **Recall** — pulls relevant past history for this customer from Hindsight
2. **Respond** — a Groq LLM answers, grounded in that recalled history
3. **Retain** — the new interaction is saved back into Hindsight for next time

## The demo

Ask the agent the same question before and after seeding history:

- **Before memory:** the agent is generic and asks basic clarifying questions
- **After memory:** the agent instantly recalls the customer's exact past issue and skips straight to the fix

## Setup
