# Installation Guide

## Prerequisites

- Python 3.8+
- [Twilio account](https://www.twilio.com) (free sandbox)
- [Supabase account](https://supabase.com) (free)
- [Resend account](https://resend.com) (free — 3000 emails/month)
- [Render account](https://render.com) (free)
- [ngrok](https://ngrok.com) (for local testing)

---

## Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/smart-hostel-complaint-system.git
cd smart-hostel-complaint-system

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file
cp .env.example .env
# Edit .env and fill in your real credentials
```

---

## Supabase Database Setup

1. Go to [supabase.com](https://supabase.com) → New Project
2. Open the SQL Editor and run this:

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

3. Copy your Project URL and service role key into `.env`

---

## Twilio WhatsApp Sandbox

1. Go to [console.twilio.com](https://console.twilio.com)
2. Messaging → Try it out → Send a WhatsApp message
3. Join the sandbox by sending the join code to **+1 415 523 8886**
4. Set the webhook URL:
   - When a message comes in: `https://YOUR_NGROK_URL/webhook`
   - Method: POST

---

## Running Locally

```bash
# Terminal 1 — Start Flask
python src/app.py

# Terminal 2 — Start ngrok tunnel
ngrok http 5000

# Copy the ngrok HTTPS URL → paste into Twilio webhook
# e.g. https://abc123.ngrok.io/webhook
```

Send a WhatsApp message to the sandbox number. You should see the
classification printed in Terminal 1 and receive an acknowledgement reply.

---

## Render Deployment

1. Push your code to GitHub (make sure `.env` is NOT committed)
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Render auto-detects `render.yaml` — settings are pre-filled
5. Add all environment variables from `.env.example` in the Render dashboard
6. Deploy → copy the `https://your-app.onrender.com` URL
7. Update `BASE_URL` in Render env vars to this URL
8. Update Twilio webhook to `https://your-app.onrender.com/webhook`

**Important:** Add UptimeRobot to ping `https://your-app.onrender.com/` every
5 minutes — prevents Render free tier from sleeping and missing Twilio webhooks.

---

## Quick Verification

```bash
# Test server is running
curl https://your-app.onrender.com/

# View all complaints (JSON)
curl https://your-app.onrender.com/complaints

# Run unit tests
python -m pytest tests/ -v

# Run classifier manually
python src/ai_classifier_simple.py
```
