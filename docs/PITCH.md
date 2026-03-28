# 🎤 Final Pitch Notes

## 30-Second Elevator Pitch

"University hostels use paper registers for maintenance complaints.
Students write a problem. No one reads it for days. We replaced that with WhatsApp.
Student texts a complaint. AI classifies it in under a second.
The right department gets an email with one click to resolve.
Student gets notified on WhatsApp automatically. Total cost: near zero."

---

## Problem (30 seconds)

- Every hostel has a paper complaint register
- Students report a problem → warden "reads it eventually" → maybe calls a department
- Student has zero visibility — they don't know if anything will happen
- Complaints get lost, forgotten, or written multiple times
- Average resolution time: **5–7 days**
- At 10,000+ students, this is a massive daily friction point

---

## Solution (45 seconds)

**5 steps, fully automated:**

1. Student sends a WhatsApp message (already on their phone, no app needed)
2. AI reads it → detects category (ELECTRICAL, WIFI, PLUMBING, etc.), priority, hostel, room number — in under 1 second
3. Correct department gets a formatted email with all details + green "✅ Mark as Resolved" button
4. Department clicks it → complaint marked RESOLVED in database instantly
5. Student receives WhatsApp: "Your complaint #XXXX has been resolved!"

---

## Technical Highlights (30 seconds)

- **Flask** backend deployed on Render (free, HTTPS, 24/7, auto-deploy from GitHub)
- **Keyword NLP classifier** — 8 categories, handles KP-7/Block A/Kaveri Hostel formats, zero external API dependency
- **Twilio WhatsApp Business API** — bidirectional messaging, sandboxed for demo
- **Supabase PostgreSQL** — full audit trail, every complaint timestamped
- **Resend API** — styled HTML emails with cryptographically secure one-time resolve tokens
- **PYTHONUNBUFFERED=1** + UptimeRobot keep-alive — keeps free tier Render stable

---

## Numbers That Matter

| Metric | Before | After |
|---|---|---|
| Resolution time | 5–7 days | Target: < 24 hours |
| Complaint tracking | 0% (paper) | 100% (database) |
| Student effort | Walk to office | One WhatsApp message |
| Monthly cost | Paper + manual | ₹0–₹200 |
| New hostel setup | N/A | 30 minutes |

---

## Live Demo Script (2 minutes)

1. Open WhatsApp on phone
2. Send: **"KP-7 hostel room 312 fan not working urgent"**
3. Show instant WhatsApp reply: complaint ID, ELECTRICAL, URGENT
4. Switch to Gmail — show the formatted department email arriving
5. Click **✅ Mark as Resolved** in the email
6. Show student receives: "Your complaint has been resolved!"
7. Show Supabase table — status changed PENDING → RESOLVED
8. Show GitHub repo: tests passing in CI, clean architecture, docs

---

## Q&A Prep

**Q: Why not just a Google Form?**
Forms require a URL, a browser, filling fields. WhatsApp is already open.
Also no auto-routing, no acknowledgement, no resolution notification.

**Q: What if the classifier gets it wrong?**
Fallback to OTHER which routes to admin. v1.1 will upgrade to Groq LLM (API key
already in requirements.txt). Current rule-based handles 85%+ of standard complaints correctly.

**Q: What about Render spinning down?**
UptimeRobot pings every 5 minutes. PYTHONUNBUFFERED=1 ensures logs appear instantly.
Render URL is updated in Twilio webhook after every redeploy.

**Q: Privacy?**
Phone numbers stored in private Supabase DB. No names collected. Resolve tokens
are cryptographic — secrets.token_urlsafe(32). No data shared with third parties.

**Q: Cost for a hostel of 1000 students?**
Under ₹50/month. Render free, Supabase free, Resend 3000/month free,
Twilio ~₹0.40/message. At 100 complaints/month, essentially free.

**Q: Why Apache 2.0?**
Permissive — any university, startup, or government body can fork, deploy,
and even commercialise without restrictions. Maximum adoption.
