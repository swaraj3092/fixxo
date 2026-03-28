# Changelog

All notable changes documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

---

## [1.0.0] — 2026-03-07 (Hackathon MVP)

### Added
- WhatsApp complaint submission via Twilio sandbox
- Keyword NLP classifier (ai_classifier_simple.py)
  - 8 categories: PLUMBING, ELECTRICAL, CLEANLINESS, SECURITY, WIFI, FOOD, FURNITURE, OTHER
  - Priority detection: URGENT, HIGH, MEDIUM
  - Hostel extraction: KP-7, Block A, Kaveri Hostel formats
  - Room extraction: "room 312", "rm 204", "#101" formats
- Supabase PostgreSQL database with full audit trail
- Cryptographic one-time resolve tokens (secrets.token_urlsafe)
- Resend API HTML emails with colour-coded priority banners
- One-click "Mark as Resolved" button in department emails
- WhatsApp resolution notification to student on resolve
- Flask REST API: /webhook, /resolve, /complaints, /
- Render deployment via render.yaml
- GitHub Actions CI pipeline
- Full test suite: test_classifier.py, test_database.py, test_email.py
- Apache 2.0 license

### Known Limitations
- English only (Hindi support planned for v1.1)
- Single category per complaint (multi-issue routing in v2.0)
- No LOW priority detection (planned v1.1)
- All emails route to one inbox in demo mode

---

## [Unreleased] — v1.1 Planned
- Groq LLM classification
- Hindi keyword support
- LOW priority detection
- Image analysis
```



Also add a test in tests/test_classifier.py for LOW priority.

**Files to edit:** src/ai_classifier_simple.py, tests/test_classifier.py
