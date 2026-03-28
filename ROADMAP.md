# Roadmap

## ✅ v1.0 — Hackathon MVP (Current)

- ✅ WhatsApp complaint submission via Twilio sandbox
- ✅ Keyword NLP classifier — 8 categories, KP-7/Block/Kaveri Hostel extraction
- ✅ Priority detection — URGENT, HIGH, MEDIUM
- ✅ Auto-routing to department via Resend HTML email
- ✅ One-click resolve from email (cryptographic token)
- ✅ WhatsApp resolution notification to student
- ✅ Supabase PostgreSQL audit trail
- ✅ Deployed on Render with `render.yaml`
- ✅ GitHub Actions CI pipeline
- ✅ Apache 2.0 open source

---

## 🔄 v1.1 — Smarter Classification (Next 2–4 weeks)

- 🔄 **Groq LLM integration** — API key already in `requirements.txt`. Upgrade `classify_complaint()` to use `grok-beta` for edge cases and multi-issue complaints
- 🔄 **Hindi language support** — Add keyword lists in Hindi for all 8 categories
- 🔄 **LOW priority detection** — Keyword list for cosmetic/minor issues
- 🔄 **Image analysis** — `image_url` parameter is already in the function signature, ready for multimodal classification

---

## 🎯 v2.0 — Full Platform (1–3 months)

- 📋 Admin dashboard — real-time complaint view, resolution time stats, category breakdown
- 📱 Department mobile app — push notifications instead of email
- ⏰ Auto-escalation — if unresolved after 24 hours, escalate to warden automatically
- 🔁 SMS fallback — for departments without smartphone access
- 📊 Monthly report generation — CSV export of all complaints
- 🌐 Multi-campus — single deployment supporting multiple hostels/universities

---

## 🤝 How to Contribute

Pick a `v1.1` or `v2.0` issue from the GitHub Issues tab.
See [CONTRIBUTING.md](CONTRIBUTING.md) to get started.
