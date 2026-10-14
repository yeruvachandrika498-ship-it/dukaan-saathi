# Dukaan Saathi: AI Freshness Clock for Local Shops and Farmers

Built for **Prompt Wars x Creative Community VVITU** (AI for Better Living and Smarter Communities).

## Problem
Small neighbourhood shops and farmers lose money every day to spoiled produce and poor demand guesses, while nearby buyers run short of the same items. Existing platforms mostly serve large aggregators and need sales data that tiny vendors do not have.

## Solution
Photograph a stall. Gemini Vision reads the produce and estimates quantity, freshness and hours left. The app shows a live **Freshness Clock**, a suggested discount, and a **second-life ladder** (tiffin centre, hostel mess, donation, animal feed, compost). Farmers speak or type what they have and get matched to the best nearby buyer. A counter tracks kg of food saved.

## What makes it different
- Works from **one photo and a voice note**; no billing data or software setup
- Focuses on the **last hours of freshness**, not just forecasting
- **Second-life routing** so unsellable produce still gets used
- Telugu and English output

## How Gemini is used
| Capability | Use |
|---|---|
| Vision | Reads produce, quantity and freshness from a photo |
| Reasoning | Estimates shelf life and chooses the best next use |
| Structured output | Schema-validated JSON drives the whole UI |
| Multilingual | Advice in English or Telugu |

Prompts follow a structure of role, task, rules, output format and a worked example (see `app.py`).

## Reliability and safety
- Server-side clamping of AI values, input validation, one automatic retry, per-IP rate limit
- API key kept on the server as an environment variable
- Clear on-screen notice that values are AI estimates
- Unit tests in `tests/`

## Architecture
Browser (HTML/JS, image resized to 1024px) -> Flask API (`/api/analyze`, `/api/farmer`) -> Gemini API -> validated JSON -> UI

## Run locally
```bash
pip install -r requirements.txt
export GEMINI_API_KEY=your_key      # from aistudio.google.com
python app.py                       # http://localhost:8080
# tests: pip install -r requirements-dev.txt && pytest
```

## Deploy on Render
Language Python 3, build `pip install -r requirements.txt`, start `gunicorn app:app --timeout 120`, env var `GEMINI_API_KEY`.

## Limitations and next steps
- Nearby partners are demo data; a full product would use real local listings
- Freshness values are estimates, not lab measurements
- Next: real partner directory, WhatsApp voice notes, price data from local mandis
