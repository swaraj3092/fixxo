<div align="center">

# 🔧 FIXXO
### Smart Hostel Complaint Management System

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-fixxo--v2.vercel.app-00d4ff?style=for-the-badge)](https://fixxo-v2.vercel.app)
[![Built with Flask](https://img.shields.io/badge/Flask-Backend-000000?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react)](https://react.dev/)
[![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E?style=for-the-badge&logo=supabase)](https://supabase.com/)
[![WhatsApp](https://img.shields.io/badge/Twilio-WhatsApp_API-25D366?style=for-the-badge&logo=whatsapp)](https://www.twilio.com/)

> **FIXXO** is a WhatsApp-first hostel complaint management system built for KIIT University. Students submit complaints via WhatsApp in plain text — Groq AI classifies the issue, routes it to the right department, and keeps everyone notified until resolution.

</div>

---

## ✨ What Makes Fixxo Different

- 📱 **No app download needed** — students use WhatsApp they already have
- 🤖 **AI-powered classification** — Groq AI auto-detects category and priority
- 📧 **Department email routing** — relevant teams get notified with one-click resolution
- 🔔 **Real-time WhatsApp updates** — students notified on every status change
- 🛡️ **Admin mission-control dashboard** — full overview with live complaint feed
- 🔐 **OTP-verified registration** — restricted to `@kiit.ac.in` emails

---

## 📸 Screenshots

### 🏠 Student Registration (One-Time Setup)

When a new student messages Fixxo for the first time, they receive a registration link on WhatsApp.

| First-Time WhatsApp Prompt | Registration Form |
|:-:|:-:|
| ![First Time Registration](docs/screenshots/Fixxo_Student_1_time_registeration.png) | ![Registration Page](docs/screenshots/Fixxo_student_registeration_page.png) |

---

### 💬 Submitting a Complaint via WhatsApp

After registration, students simply describe their issue in plain text — Fixxo handles the rest.

| Complaint Submitted via WhatsApp |
|:-:|
| ![WhatsApp Complaint](docs/screenshots/Fixxo_wp_complaint.png) |

Groq AI classifies the message into a category (ELECTRICAL, PLUMBING, FURNITURE, etc.), assigns a priority (LOW / MEDIUM / HIGH), and generates a unique complaint ID.

---

### 🛠️ Admin Dashboard

Admins get a live mission-control view of all complaints across the hostel.

| Admin Login | Admin Overview |
|:-:|:-:|
| ![Login Page](docs/screenshots/Fixxo_login_page.png) | ![Admin Dashboard](docs/screenshots/Fixxo_admin_page_content.png) |

The dashboard shows total complaints, pending, in-progress, resolved, and "can't resolve" counts — plus average feedback rating and recent complaint feed.

---

### 📧 Department Email Notification

When a complaint is submitted, the relevant department receives a structured email with a one-click **Mark as Resolved** button.

| Department Email |
|:-:|
| ![Department Mailing](docs/screenshots/Fixxo_department_mailing.png) |

---

### ✅ Resolution Flow

When the department marks the complaint as resolved (or already resolved), a confirmation page is shown and the student is **automatically notified on WhatsApp**.

| Already Resolved Page | Student Notified via WhatsApp |
|:-:|:-:|
| ![Already Resolved](docs/screenshots/Fixxo_department_marked_as_resolved.png) | ![Notified on WhatsApp](docs/screenshots/Fixxo_notified_in_wp_as_resolved.png) |

---

## 🔄 System Flow

```
Student sends WhatsApp message
        ↓
Twilio Webhook → Flask Backend
        ↓
Groq AI classifies: Category + Priority
        ↓
Complaint stored in Supabase PostgreSQL
        ↓
Department notified via Email (Resend/Gmail)
        ↓
Department clicks "Mark as Resolved" in email
        ↓
Status updated in DB → Student notified on WhatsApp
```

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React.js, Tailwind CSS |
| **Backend** | Python Flask |
| **Database** | Supabase (PostgreSQL) |
| **WhatsApp API** | Twilio WhatsApp Sandbox |
| **Email** | Resend / Gmail SMTP |
| **AI Classification** | Groq API (LLaMA 3) |
| **Deployment** | Vercel (frontend) + Render (backend) |

---

## 🚀 Getting Started

### Prerequisites

```bash
Python 3.10+
Node.js 18+
Supabase account
Twilio account (WhatsApp Sandbox)
Groq API key
```

### 1. Clone the repository

```bash
git clone https://github.com/swaraj3092/fixxo.git
cd fixxo
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
GROQ_API_KEY=your_groq_api_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
RESEND_API_KEY=your_resend_api_key
ADMIN_EMAIL=your_admin_email
FRONTEND_URL=http://localhost:5173
```

```bash
python app.py
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## 📁 Project Structure

```
fixxo/
├── backend/
│   ├── app.py              # Flask main app
│   ├── routes/
│   │   ├── whatsapp.py     # Twilio webhook handler
│   │   ├── complaints.py   # Complaint CRUD
│   │   ├── admin.py        # Admin auth & dashboard
│   │   └── register.py     # Student registration
│   └── utils/
│       ├── groq_classify.py # AI classification
│       └── email_sender.py  # Email notification
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── AdminDashboard.jsx
│   │   │   ├── Register.jsx
│   │   │   └── ResolveConfirm.jsx
│   │   └── components/
└── docs/
    └── screenshots/
```

---

## 👥 Team

Built by **CodeSync** for KIIT University

| | |
|---|---|
| **Swaraj Kumar Behera** | Backend, Deployment, AI Integration |
| **Prajakta Kuila** | Frontend, UI/UX Design |

---

## 🏆 Achievements

- 🥇 Submitted at **Open Source Forge Hackathon** — KIIT Fest
- 🚀 Submitted at **HackRent 2026** — Systems Track
- ⭐ 5.0/5 avg feedback rating (from real test users)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">
  Made with ❤️ at KIIT University, Bhubaneswar
  <br/>
  <a href="https://fixxo-v2.vercel.app">🌐 Live Demo</a> · <a href="https://github.com/swaraj3092/fixxo/issues">🐛 Report Bug</a>
</div>
