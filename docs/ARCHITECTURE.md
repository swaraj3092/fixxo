# System Architecture

## Overview

A WhatsApp-native complaint system. Students send a message. The backend
classifies it, emails the correct department, and notifies the student
when it's resolved. No app download. No forms. No training needed.

---

## Data Flow

```
Student sends WhatsApp message
           │
           ▼
     Twilio API
  (Message Gateway)
           │  POST /webhook
           ▼
    Flask Backend (app.py)
           │
     ┌─────┴──────┐
     │            │
     ▼            ▼
AI Classifier  Save to DB
(ai_classifier (database.py
  _simple.py)   → Supabase)
     │            │
     └─────┬──────┘
           │
           ▼
    Send Email
  (email_sender.py)
    via Resend API
           │
           ▼
  Department receives email
  with ✅ "Mark as Resolved" button
           │
           ▼  GET /resolve?token=...
    Flask Backend (app.py)
           │
     ┌─────┴──────┐
     │            │
     ▼            ▼
 Update DB    Twilio API
  RESOLVED   sends WhatsApp
              to student
```

---

## Components

### 1. Flask Backend — `src/app.py`

Central orchestrator. All HTTP routes:

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Health check |
| `/test` | GET | Debug endpoint |
| `/webhook` | POST | Receives WhatsApp messages from Twilio |
| `/resolve` | GET | Department clicks to close a complaint |
| `/complaints` | GET | Admin JSON view of all complaints |

### 2. AI Classifier — `src/ai_classifier_simple.py`

Keyword-based NLP. No external API needed. Zero latency.

- Scores each category by counting matching keywords
- Detects priority from urgency words (urgent, emergency, broken, not working)
- Extracts hostel name with regex (KP-7, Block A, Kaveri Hostel, etc.)
- Extracts room number with regex (room 312, rm 204, #101, standalone numbers)

**Categories:** PLUMBING, ELECTRICAL, CLEANLINESS, SECURITY, WIFI, FOOD, FURNITURE, OTHER
**Priorities:** URGENT, HIGH, MEDIUM

### 3. Database Layer — `src/database.py`

Supabase PostgreSQL wrapper with 4 functions:

| Function | Purpose |
|---|---|
| `save_complaint()` | Insert new complaint, generate resolve token |
| `resolve_complaint()` | Update status → RESOLVED, set timestamp |
| `get_complaint_by_token()` | Fetch one complaint by resolve token |
| `get_all_complaints()` | Fetch all for admin view |

### 4. Email Sender — `src/email_sender.py`

Resend API integration.

- Builds styled HTML email with complaint details
- Colour-coded priority banner (red=URGENT, orange=HIGH, yellow=MEDIUM)
- Secure one-click "✅ Mark as Resolved" button
- Returns True/False for logging

---

## Database Schema

```sql
CREATE TABLE complaints (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_phone    VARCHAR(50)   NOT NULL,
    hostel_name      VARCHAR(100),
    room_number      VARCHAR(20),
    category         VARCHAR(50)   DEFAULT 'OTHER',
    priority         VARCHAR(20)   DEFAULT 'MEDIUM',
    raw_message      TEXT          NOT NULL,
    summary          TEXT,
    department_email VARCHAR(100),
    confidence       DECIMAL(5,2),
    status           VARCHAR(20)   DEFAULT 'PENDING',
    resolve_token    VARCHAR(100)  UNIQUE,
    resolution_note  TEXT,
    created_at       TIMESTAMPTZ   DEFAULT NOW(),
    resolved_at      TIMESTAMPTZ
);
```

---

## Deployment Architecture

```
Developer pushes to GitHub
          │
          ▼  auto-deploy on push
    Render Web Service
  (Python 3.10, HTTPS, free tier)
  Configured via render.yaml
          │
  ┌───────┼──────────┐
  ▼       ▼          ▼
Twilio  Supabase  Resend API
(WA)    (DB)      (Email)
```

**Keep-alive:** UptimeRobot pings `/` every 5 minutes to prevent
Render free tier from spinning down (spin-up takes 30–50 seconds,
Twilio webhook timeout is 15 seconds — spinning down causes missed messages).

---

## Security

- No secrets in code — all via `os.getenv()` from environment variables
- One-time resolve tokens — `secrets.token_urlsafe(32)` per complaint
- Double-resolve guard — status checked before processing any resolve
- `.env` in `.gitignore` — real keys never reach GitHub
- `.env.example` has placeholder values only
