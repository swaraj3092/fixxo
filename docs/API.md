# API Documentation

The Hostel Complaint System exposes a simple REST API. All endpoints are
served over HTTPS from the Render deployment.

**Base URL:** `https://hostel-complaint-system-1-r1g3.onrender.com`

---

## Endpoints

### `GET /`
Health check. Confirms the server is live.

**Response:**
```
200 OK
🏠 Hostel Complaint System is running!
```

---

### `GET /test`
Debug endpoint. Used during deployment to verify Flask is responding.

**Response:**
```
200 OK
Test successful!
```

---

### `POST /webhook`
**Twilio webhook** — called automatically by Twilio on every incoming WhatsApp message.
Do not call this manually. Configure this URL in the Twilio console.

**Content-Type:** `application/x-www-form-urlencoded` (Twilio format)

**Form Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `Body` | string | The student's WhatsApp message text |
| `From` | string | Student's WhatsApp number (e.g. `whatsapp:+919178773834`) |
| `MediaUrl0` | string (optional) | URL of attached image, if any |

**Response:** TwiML XML consumed by Twilio.

**Example TwiML response:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Message>
    ✅ Complaint Received!

    📋 ID: #A3F8C201
    🏷️ Category: ELECTRICAL
    ⚡ Priority: URGENT
    🏢 Assigned to: electrical@university.edu

    You will be notified on WhatsApp once resolved. Thank you!
  </Message>
</Response>
```

**Side Effects:**
- Saves complaint to Supabase database
- Sends HTML email notification to the responsible department
- Generates a one-time cryptographic resolve token

---

### `GET /resolve`
**Resolution endpoint** — departments click this link in their email to close a complaint.
The link is generated automatically and embedded in the department email.

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `token` | string | Yes | Unique resolve token from the email link |
| `note` | string | No | Resolution message from the department |

**Example:**
```
GET /resolve?token=abc123securetoken&note=Fan+replaced
```

**Responses:**

| Status | Body | Condition |
|---|---|---|
| `200` | HTML confirmation page | Complaint successfully resolved |
| `200` | `✅ This complaint was already resolved.` | Token already used |
| `400` | `❌ Invalid link.` | No token provided |
| `404` | `❌ Complaint not found.` | Token not in database |
| `500` | `❌ Something went wrong.` | Database error |

**Side Effects (on success):**
- Updates complaint status to `RESOLVED` in database
- Sets `resolved_at` timestamp
- Sends WhatsApp notification to the student

---

### `GET /complaints`
**Admin endpoint** — returns all complaints as JSON, newest first.

**Response:** `200 OK` with JSON array.

**Example:**
```bash
curl https://hostel-complaint-system-1-r1g3.onrender.com/complaints
```

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "student_phone": "whatsapp:+919178773834",
    "hostel_name": "KP-7",
    "room_number": "312",
    "category": "ELECTRICAL",
    "priority": "URGENT",
    "raw_message": "KP-7 hostel room 312 fan not working urgent",
    "summary": "KP-7 hostel room 312 fan not working urgent",
    "department_email": "swarajbehera923@gmail.com",
    "confidence": 85.0,
    "status": "RESOLVED",
    "resolve_token": "[hidden]",
    "resolution_note": "Fan blade replaced",
    "created_at": "2026-03-06T09:30:00Z",
    "resolved_at": "2026-03-06T11:45:00Z"
  }
]
```

**Fields:**

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Auto-generated complaint identifier |
| `student_phone` | string | WhatsApp number with `whatsapp:` prefix |
| `hostel_name` | string\|null | Extracted hostel/block (e.g. KP-7, BLOCKA) |
| `room_number` | string\|null | Extracted room number |
| `category` | string | PLUMBING / ELECTRICAL / WIFI / SECURITY / FOOD / CLEANLINESS / FURNITURE / OTHER |
| `priority` | string | URGENT / HIGH / MEDIUM |
| `raw_message` | string | Original unmodified WhatsApp message |
| `summary` | string | First 100 characters of the message |
| `department_email` | string | Email address the complaint was routed to |
| `confidence` | float | Classifier confidence score (0–100) |
| `status` | string | PENDING or RESOLVED |
| `resolution_note` | string\|null | Department's resolution message |
| `created_at` | ISO 8601 | When the complaint was received |
| `resolved_at` | ISO 8601\|null | When the complaint was resolved |

---

## Classifier Output Reference

The internal classifier (`ai_classifier_simple.py`) returns this structure,
which is passed to the database and email modules:

```json
{
  "hostel_name": "KP-7",
  "room_number": "312",
  "category": "ELECTRICAL",
  "priority": "URGENT",
  "summary": "KP-7 hostel room 312 fan not working urgent",
  "department_email": "swarajbehera923@gmail.com",
  "confidence": 85.0
}
```

---

## Error Handling

All errors return a plain text body with an emoji prefix:
- `❌` — error / failure
- `✅` — success (including already-resolved)

The `/webhook` endpoint always returns `200 OK` with TwiML — Twilio requires
this even when the message cannot be processed. Errors are logged server-side.
