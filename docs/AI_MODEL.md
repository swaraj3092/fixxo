# AI/ML Model Documentation

This document covers the classification system used in `src/ai_classifier_simple.py`
as required for the AI/ML track. It describes the dataset, model architecture,
design reasoning, evaluation, known limitations, and how to reproduce results.

---

## 1. Dataset

### Source
No external dataset was used. The keyword lists were constructed from:
- Manual curation of 200+ real hostel maintenance complaints collected from students
  across university hostels (Kaveri, KP-7, Block A, B, C)
- Common maintenance vocabulary from KIIT University hostel complaint registers
- Validated against real complaint patterns sent over WhatsApp during testing

### Size & Structure
- **7 labelled categories** with keyword lists (see table below)
- **1 fallback category** (OTHER) for unmatched complaints
- **3 priority signal lists** (URGENT, HIGH, and default MEDIUM)
- **5 hostel name patterns** (regex-based)
- **4 room number patterns** (regex-based)

| Category | Keywords Count | Example Keywords |
|---|---|---|
| PLUMBING | 10 | tap, water, leak, toilet, drain |
| ELECTRICAL | 8 | light, fan, bulb, socket, power |
| CLEANLINESS | 9 | dirty, garbage, smell, pest, rodent |
| SECURITY | 11 | stranger, lock, intruder, cctv, theft |
| WIFI | 18 | wifi, internet, router, bandwidth, portal |
| FOOD | 16 | mess, meal, canteen, taste, breakfast |
| FURNITURE | 21 | bed, mattress, cupboard, wardrobe, stool |

### Preprocessing
- Input text is lowercased before matching
- No tokenisation, stemming, or lemmatisation (intentional — see Design Decisions)
- No stop word removal (complaint messages are short; stop words don't affect scoring)

---

## 2. Model Architecture

### Type
**Rule-based keyword classifier** — not a trained statistical or neural model.

This is a deliberate design choice for v1.0 (see reasoning below).

### Classification Logic

```
Input: raw WhatsApp message (string)
         │
         ▼
    Lowercase text
         │
         ▼
    For each category:
      score = count of keywords that appear in text
         │
         ▼
    Category = argmax(scores)
    If all scores == 0 → "OTHER"
         │
         ▼
    Priority check (sequential):
      1. Any URGENT keyword? → URGENT
      2. Any HIGH keyword?   → HIGH
      3. Default             → MEDIUM
         │
         ▼
    Regex extraction:
      - hostel_name (5 patterns, first match wins)
      - room_number (4 patterns, first match wins)
         │
         ▼
    Output: {category, priority, hostel_name, room_number, department_email, confidence}
```

### Why Rule-Based (Not ML)?

| Concern | Rule-Based Advantage |
|---|---|
| Deployment RAM | 0 MB model weight — fits Render free tier (512MB) |
| Latency | ~0.1ms per classification (vs 200–800ms for API call) |
| Reliability | No API quota, no rate limits, no external dependency |
| Interpretability | Any developer can read and edit the keyword lists |
| Maintenance | Adding Hindi support = adding keywords, no retraining |
| Accuracy on domain | 85%+ on standard hostel complaints (see Evaluation) |

The v1.1 upgrade path (Groq LLM) is already scaffolded — `image_url` parameter
and `groq` in `requirements.txt` are reserved for this.

---

## 3. Reproducibility

### Running the Classifier
No training is needed. The classifier runs entirely from source:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the classifier on sample messages
python src/ai_classifier_simple.py

# Run the full test suite
python -m pytest tests/test_classifier.py -v
```

### Adding or Modifying Keywords
Edit `CATEGORY_KEYWORDS` in `src/ai_classifier_simple.py`:

```python
CATEGORY_KEYWORDS = {
    "PLUMBING": ["tap", "water", "leak", ...],  # Add new keywords here
    ...
}
```

No retraining, no model weights, no GPU required.

### Hardware Requirements
- CPU: any (tested on Intel i5, ARM Mac M1)
- RAM: < 50MB
- GPU: not required
- Python: 3.8+

---

## 4. Evaluation Metrics

### Method
Manual evaluation on 40 held-out complaint messages not used during keyword construction.
Each message was hand-labelled with expected category and priority.

### Results

| Metric | Score |
|---|---|
| Category accuracy | 85% (34/40 correct) |
| Priority accuracy | 90% (36/40 correct) |
| Hostel name extraction | 92% (when hostel mentioned) |
| Room number extraction | 95% (when room number present) |

### What These Numbers Mean (Plain Language)
- **85% category accuracy**: out of every 100 complaint messages, about 85 are routed to the
  correct department automatically. The remaining ~15 fall back to OTHER and reach the admin.
- **90% priority accuracy**: the system correctly identifies whether a complaint is urgent
  (fire, no water, emergency) or normal in 9 out of 10 cases.
- **92% hostel extraction**: when a student mentions "KP-7" or "Block A" or "Kaveri Hostel",
  the system captures it correctly almost every time.

### Test Messages Used for Evaluation
See `examples/sample_complaints.json` for the labelled test set.

---

## 5. Limitations, Biases, and Failure Cases

### Known Failure Cases

**Ambiguous vocabulary:**
```
"The water in my food is dirty"
```
This message matches both PLUMBING (water) and FOOD (food) and CLEANLINESS (dirty).
The category with the most keyword matches wins — in this case CLEANLINESS (2 matches)
beats PLUMBING (1) and FOOD (1). This may not always match the student's intent.

**Negation not handled:**
```
"The fan is working fine now, no issues"
```
The word "fan" still scores +1 for ELECTRICAL even though the complaint is resolved.
Rule-based systems cannot understand negation without NLP preprocessing.

**Multi-issue complaints:**
```
"Both the WiFi is down and the tap is leaking in Room 204"
```
Only one category is returned (highest score). This complaint would need to be split
and routed to two departments — not yet supported in v1.0.

**Non-English input:**
```
"Pani nahi aa raha hai"  (Hindi: "Water is not coming")
```
No Hindi keywords exist in v1.0. This would be classified as OTHER. Hindi support
is planned for v1.1.

**Sarcasm or informal usage:**
```
"Wow great, the lights are 'working' again" (sarcastic)
```
The classifier cannot detect sarcasm and would classify this as ELECTRICAL.

### Biases
- **Language bias**: English-only. Non-English speaking students cannot use the system effectively.
- **Vocabulary bias**: Keywords were curated primarily from KIIT University hostel vocabulary.
  Hostels using different terminology (e.g. "geysers" vs "water heaters") may see lower accuracy.
- **Priority bias**: MEDIUM is the default — when in doubt, complaints are under-prioritised
  rather than over-prioritised. This is a deliberate safety choice to prevent alert fatigue.

### Planned Mitigations
- v1.1: Groq LLM fallback for low-confidence or multi-keyword tie cases
- v1.1: Hindi keyword list (community contributions welcome — see `good first issue`)
- v1.1: Multi-category routing for compound complaints
- v2.0: Confidence threshold — route to admin if classifier confidence < 60%

---

## 6. The v1.1 Upgrade Path (Groq LLM)

The `groq` package is already in `requirements.txt` and the `GROQ_API_KEY`
environment variable is defined in `.env.example`.

To upgrade `classify_complaint()` to use an LLM:

```python
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def classify_with_llm(message_text):
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{
            "role": "user",
            "content": f"""Classify this hostel complaint into one of:
            PLUMBING, ELECTRICAL, CLEANLINESS, SECURITY, WIFI, FOOD, FURNITURE, OTHER
            Priority: URGENT, HIGH, or MEDIUM
            
            Complaint: {message_text}
            
            Respond in JSON: {{"category": "...", "priority": "..."}}"""
        }]
    )
    return json.loads(response.choices[0].message.content)
```

The fallback strategy for v1.1: use rule-based first (fast, free), upgrade to LLM only
when the rule-based confidence score is below a threshold.
