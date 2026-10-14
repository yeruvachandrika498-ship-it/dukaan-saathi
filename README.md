# Dukaan Saathi: AI Freshness Clock for Local Shops and Farmers

Built for **Prompt Wars x Creative Community VVITU** (AI for Better Living and Smarter Communities).

## Problem
Small neighbourhood shops and local farmers lose money every day to spoiled produce and poor demand guesses, while nearby supply and demand never connect.

## Solution
Photograph a stall. Gemini Vision reads the produce and estimates quantity, freshness and hours left. The app shows a live **Freshness Clock**, a suggested discount, and a **second-life ladder** (nearby tiffin centre, hostel mess, donation, animal feed, compost). Farmers can speak or type what they have and get matched to the best nearby buyer. A counter tracks kg of food saved.

## How Gemini is used
- **Vision:** reads produce, quantity and freshness from a photo
- **Reasoning:** estimates shelf life and picks the best next use
- **Structured output:** schema-validated JSON, no hard-coded results
- **Multilingual:** English or Telugu

## Tech stack
Python (Flask), Gemini API, HTML/JS frontend, deployed on Render.

## Run locally
```bash
pip install -r requirements.txt
export GEMINI_API_KEY=your_key      # from aistudio.google.com
python app.py                       # http://localhost:8080
```

## Deploy on Render
- Language: Python 3
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app --timeout 120`
- Environment variable: `GEMINI_API_KEY`

## Notes
- The API key stays on the server as an environment variable.
- Nearby partners are demo data in `app.py`.
- Freshness values are AI estimates, not lab measurements.
