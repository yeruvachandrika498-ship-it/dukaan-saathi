import os
import json
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="public", static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024

KEY = os.environ.get("GEMINI_API_KEY")
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

# Demo "nearby partners" (a full product would use real local listings)
PARTNERS = [
    {"name": "Sri Sai Tiffin Centre", "type": "tiffin centre", "km": 1.2, "uses": "tomato, onion, brinjal, leafy greens"},
    {"name": "Campus Hostel Mess", "type": "hostel mess", "km": 2.5, "uses": "bulk vegetables, potato, onion"},
    {"name": "Ravi Fruits & Kirana", "type": "kirana shop", "km": 3.1, "uses": "fruits, tomato, banana"},
    {"name": "Annapurna Community Kitchen", "type": "donation", "km": 4.0, "uses": "any edible produce"},
    {"name": "Lakshmi Dairy Farm", "type": "animal feed", "km": 5.0, "uses": "overripe vegetables, banana, greens"},
    {"name": "Ward Compost Point", "type": "compost", "km": 1.8, "uses": "spoiled produce"},
]


def gemini(parts, schema, system):
    if not KEY:
        raise RuntimeError("GEMINI_API_KEY is not set on the server")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": schema,
            "temperature": 0.3,
        },
    }
    r = requests.post(
        url,
        headers={"Content-Type": "application/json", "x-goog-api-key": KEY},
        json=body,
        timeout=100,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Gemini error {r.status_code}: {r.text[:300]}")
    return json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])


def S(t, **extra):
    return {"type": t, **extra}


ANALYZE_SCHEMA = S("OBJECT", properties={
    "summary": S("STRING"),
    "items": S("ARRAY", items=S("OBJECT", properties={
        "name": S("STRING"),
        "quantity_kg": S("NUMBER"),
        "freshness_score": S("INTEGER"),
        "hours_left": S("NUMBER"),
        "discount_percent": S("INTEGER"),
        "advice": S("STRING"),
        "second_life": S("ARRAY", items=S("OBJECT", properties={
            "partner": S("STRING"), "action": S("STRING"), "why": S("STRING"),
        }, required=["partner", "action", "why"])),
    }, required=["name", "quantity_kg", "freshness_score", "hours_left",
                 "discount_percent", "advice", "second_life"])),
}, required=["summary", "items"])

FARMER_SCHEMA = S("OBJECT", properties={
    "produce": S("STRING"),
    "quantity_kg": S("NUMBER"),
    "ready_by": S("STRING"),
    "best_partner": S("STRING"),
    "distance_km": S("NUMBER"),
    "reason": S("STRING"),
    "price_tip": S("STRING"),
}, required=["produce", "quantity_kg", "ready_by", "best_partner",
             "distance_km", "reason", "price_tip"])


def lang_name(code):
    return "Telugu" if code == "te" else "English"


@app.get("/")
def home():
    return send_from_directory("public", "index.html")


@app.get("/health")
def health():
    return "ok"


@app.post("/api/analyze")
def analyze():
    try:
        data = request.get_json(force=True)
        image = data.get("image")
        if not image:
            return jsonify(error="No image received"), 400
        system = f"""You help small Indian vegetable/fruit vendors cut food waste.
Look at the photo. For each distinct fruit or vegetable visible, estimate: quantity_kg (rough), freshness_score (0-100),
hours_left (realistic remaining sellable life at Indian room temperature), discount_percent (0-70; higher when hours_left is low),
a one-sentence advice, and up to 3 second_life options chosen ONLY from these nearby partners, best first:
{json.dumps(PARTNERS)}
Match partners to what they can use and to how little time is left. If produce is still very fresh, second_life may be empty.
If the photo has no produce, return an empty items array and explain in summary.
Write summary, advice, action and why in {lang_name(data.get('lang'))}. Keep partner names unchanged. Be honest about uncertainty."""
        out = gemini(
            [{"inlineData": {"mimeType": "image/jpeg", "data": image}}, {"text": "Analyse this stock."}],
            ANALYZE_SCHEMA, system)
        return jsonify(out)
    except Exception as e:
        app.logger.exception(e)
        return jsonify(error=str(e)), 500


@app.post("/api/farmer")
def farmer():
    try:
        data = request.get_json(force=True)
        text = (data.get("text") or "").strip()
        if not text:
            return jsonify(error="Please say or type your produce details"), 400
        system = f"""A local farmer describes produce ready to sell. Extract produce, quantity_kg and ready_by.
Then pick the single best buyer from these nearby partners (consider distance and what they use):
{json.dumps(PARTNERS)}
Explain briefly why, and give a fair-price tip (no made-up exact market prices; give a practical tip).
Write reason and price_tip in {lang_name(data.get('lang'))}. Keep partner names unchanged."""
        return jsonify(gemini([{"text": text}], FARMER_SCHEMA, system))
    except Exception as e:
        app.logger.exception(e)
        return jsonify(error=str(e)), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
