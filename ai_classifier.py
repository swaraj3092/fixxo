import os
import re
import json
import logging

from groq import Groq

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Groq client ──────────────────────────────────────────────────────────────
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ── Department emails ─────────────────────────────────────────────────────────
DEPARTMENT_EMAILS = {
    "PLUMBING":    "swarajbehera923@gmail.com",
    "ELECTRICAL":  "swarajbehera923@gmail.com",
    "CLEANLINESS": "prajaktakuila19@gmail.com",
    "SECURITY":    "prajaktakuila19@gmail.com",
    "WIFI":        "swarajbehera923@gmail.com",
    "FOOD":        "anupamyagnish87@gmail.com",
    "FURNITURE":   "swarajbehera923@gmail.com",
    "OTHER":       "anupamyagnish87@gmail.com",
}

VALID_CATEGORIES = set(DEPARTMENT_EMAILS.keys())

# ── System prompt (classification only) ──────────────────────────────────────
SYSTEM_PROMPT = """
You are an AI complaint classifier for Fixxo, a university hostel management system.

A student has already provided their hostel name and room number separately.
Your ONLY job is to read their complaint message and return:

1. "category" - ONE of: PLUMBING, ELECTRICAL, CLEANLINESS, SECURITY, WIFI, FOOD, FURNITURE, OTHER
   - PLUMBING    → tap, water, leak, pipe, flush, toilet, bathroom, shower, drain
   - ELECTRICAL  → light, electricity, power, bulb, switch, fan, ac, socket
   - CLEANLINESS → dirty, garbage, trash, smell, hygiene, pest, insect, rodent
   - SECURITY    → lock, key, door, stranger, theft, safety, cctv, guard, intruder
   - WIFI        → wifi, internet, network, connection, slow, signal, router, speed
   - FOOD        → food, mess, meal, quality, taste, canteen, breakfast, lunch, dinner
   - FURNITURE   → bed, chair, table, sofa, desk, cupboard, mattress, wardrobe
   - OTHER       → anything else

2. "priority" - ONE of: URGENT, HIGH, MEDIUM
   - URGENT → urgent, emergency, immediately, asap, dangerous, fire, flood
   - HIGH   → not working, broken, serious, since yesterday
   - MEDIUM → everything else

3. "summary" - One clean sentence describing the issue.

4. "confidence" - Your confidence as a float between 0 and 100.

Reply ONLY with valid JSON. No explanation, no markdown, no code fences.
Example: {"category":"ELECTRICAL","priority":"HIGH","summary":"Fan in the room is not working","confidence":92.0}
""".strip()


# ── Keyword fallback (if Groq is down) ───────────────────────────────────────
CATEGORY_KEYWORDS = {
    "PLUMBING":    ["tap", "water", "leak", "pipe", "flush", "toilet", "bathroom", "shower", "drain", "plumb"],
    "ELECTRICAL":  ["light", "electricity", "power", "bulb", "switch", "fan", "ac", "socket"],
    "CLEANLINESS": ["clean", "dirty", "garbage", "trash", "smell", "hygiene", "pest", "insect", "rodent"],
    "SECURITY":    ["security", "lock", "key", "door", "stranger", "theft", "safety", "cctv", "guard", "intruder", "break-in"],
    "WIFI":        ["wifi", "internet", "network", "connection", "slow", "disconnect", "signal", "router", "bandwidth", "speed", "coverage"],
    "FOOD":        ["food", "mess", "meal", "quality", "taste", "menu", "cooking", "breakfast", "lunch", "dinner", "canteen"],
    "FURNITURE":   ["bed", "chair", "table", "furniture", "sofa", "desk", "cupboard", "drawer", "mattress", "wardrobe"],
}

def _keyword_fallback(message_text):
    t = message_text.lower()
    scores = {c: sum(1 for k in kws if k in t) for c, kws in CATEGORY_KEYWORDS.items()}
    category = max(scores, key=scores.get) if any(scores.values()) else "OTHER"

    if any(k in t for k in ["urgent", "emergency"]):        priority = "URGENT"
    elif any(k in t for k in ["not working", "broken"]):    priority = "HIGH"
    else:                                                    priority = "MEDIUM"

    logger.warning(f"[Fixxo] Using keyword fallback. Category={category}, Priority={priority}")

    return {
        "category":         category,
        "priority":         priority,
        "summary":          message_text[:100],
        "department_email": DEPARTMENT_EMAILS.get(category, DEPARTMENT_EMAILS["OTHER"]),
        "confidence":       60.0,
    }


# ── Main classify function ────────────────────────────────────────────────────
def classify_complaint(message_text, image_url=None):
    """
    Classify a hostel complaint using Groq LLM (Llama 3).
    hostel_name and room_number are collected by the app separately —
    this function only classifies category and priority.

    Returns dict with keys:
        category, priority, summary, department_email, confidence
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": message_text.strip()},
            ],
            max_tokens=100,
            temperature=0.1,
        )

        raw = response.choices[0].message.content.strip()
        logger.info(f"[Fixxo] Groq response: {raw}")

        # Strip accidental markdown fences
        raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()

        result = json.loads(raw)

        # Validate category
        category = str(result.get("category", "OTHER")).upper()
        if category not in VALID_CATEGORIES:
            category = "OTHER"

        # Validate priority
        priority = str(result.get("priority", "MEDIUM")).upper()
        if priority not in ("URGENT", "HIGH", "MEDIUM"):
            priority = "MEDIUM"

        return {
            "category":         category,
            "priority":         priority,
            "summary":          result.get("summary", message_text[:100]),
            "department_email": DEPARTMENT_EMAILS.get(category, DEPARTMENT_EMAILS["OTHER"]),
            "confidence":       float(result.get("confidence", 90.0)),
        }

    except json.JSONDecodeError as e:
        logger.error(f"[Fixxo] JSON parse error: {e}")
        return _keyword_fallback(message_text)

    except Exception as e:
        logger.error(f"[Fixxo] Groq API error: {e}")
        return _keyword_fallback(message_text)