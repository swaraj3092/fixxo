"""
Database Operations Module

Handles all Supabase PostgreSQL interactions for the complaint system.
Every complaint flows through this module for creating, reading,
and updating records.

Database: Supabase (PostgreSQL)
Table: complaints

Schema:
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid()
    student_phone    VARCHAR(50)   — WhatsApp number e.g. "whatsapp:+919178773834"
    hostel_name      VARCHAR(100)  — extracted by classifier e.g. "KP-7", "BLOCKA"
    room_number      VARCHAR(20)   — extracted by classifier e.g. "312"
    category         VARCHAR(50)   — PLUMBING, ELECTRICAL, WIFI, etc.
    priority         VARCHAR(20)   — URGENT, HIGH, MEDIUM
    raw_message      TEXT          — original unmodified WhatsApp message
    summary          TEXT          — first 100 chars of message
    department_email VARCHAR(100)  — email routing destination
    confidence       DECIMAL(5,2)  — classifier confidence (85.0 for rule-based)
    status           VARCHAR(20)   — PENDING or RESOLVED
    resolve_token    VARCHAR(100) UNIQUE — secure one-time token for email link
    resolution_note  TEXT          — department's resolution message
    created_at       TIMESTAMPTZ   DEFAULT NOW()
    resolved_at      TIMESTAMPTZ   — set when complaint is closed

Author: Team Smart Hostel
Version: 1.0.0
License: Apache 2.0
"""

import os
import uuid
import secrets
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase connection from environment variables
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)


def save_complaint(student_phone, raw_message, ai_result):
    """
    Insert a new complaint record into the database.

    Generates a cryptographically secure resolve token automatically using
    secrets.token_urlsafe(32) — a 43-char URL-safe string that is embedded
    in the department email's "Mark as Resolved" link.

    Args:
        student_phone (str): WhatsApp number of the student.
                             Includes "whatsapp:" prefix from Twilio,
                             e.g. "whatsapp:+919178773834".
        raw_message (str): The original unmodified WhatsApp complaint text.
        ai_result (dict): Output from classify_complaint(). Must contain:
                          hostel_name, room_number, category, priority,
                          summary, department_email, confidence.

    Returns:
        dict or None: The full saved record including auto-generated id
                      and resolve_token, or None if the insert fails.

    Example:
        >>> saved = save_complaint("whatsapp:+91...", "Fan broken urgent", ai_result)
        >>> print(saved['id'])       # UUID string
        >>> print(saved['status'])   # 'PENDING'
    """
    try:
        resolve_token = secrets.token_urlsafe(32)

        complaint = {
            "student_phone": student_phone,
            "hostel_name": ai_result.get("hostel_name"),
            "room_number": ai_result.get("room_number"),
            "category": ai_result.get("category", "OTHER"),
            "priority": ai_result.get("priority", "MEDIUM"),
            "raw_message": raw_message,
            "summary": ai_result.get("summary", raw_message[:100]),
            "department_email": ai_result.get("department_email"),
            "confidence": ai_result.get("confidence", 0),
            "status": "PENDING",
            "resolve_token": resolve_token
        }

        response = supabase.table("complaints").insert(complaint).execute()

        saved_record = response.data[0]
        complaint_id = saved_record["id"]

        print(f"✅ Complaint saved to database!")
        print(f"   ID: {complaint_id}")
        print(f"   Status: PENDING")

        return saved_record

    except Exception as e:
        print(f"❌ Database error while saving: {e}")
        return None


def resolve_complaint(resolve_token, resolution_note=None):
    """
    Mark a complaint as RESOLVED using its unique resolve token.

    Called when a department clicks the "Mark as Resolved" button
    in their email notification.

    Updates:
        - status       → "RESOLVED"
        - resolved_at  → current UTC timestamp
        - resolution_note → department message or default

    Args:
        resolve_token (str): The unique token embedded in the email link.
        resolution_note (str, optional): Message from the department describing
                                         how the issue was fixed. Defaults to
                                         "Issue has been resolved."

    Returns:
        dict or None: Updated complaint record, or None if token not found or error.

    Example:
        >>> updated = resolve_complaint("abc123token", "Replaced the fan blade")
        >>> print(updated['status'])   # 'RESOLVED'
    """
    try:
        from datetime import datetime, timezone

        update_data = {
            "status": "RESOLVED",
            "resolved_at": datetime.now(timezone.utc).isoformat(),
            "resolution_note": resolution_note or "Issue has been resolved."
        }

        response = (
            supabase.table("complaints")
            .update(update_data)
            .eq("resolve_token", resolve_token)
            .execute()
        )

        if response.data:
            record = response.data[0]
            print(f"✅ Complaint {record['id']} marked as RESOLVED!")
            return record
        else:
            print(f"❌ No complaint found with that token")
            return None

    except Exception as e:
        print(f"❌ Database error while resolving: {e}")
        return None


def get_complaint_by_token(resolve_token):
    """
    Fetch a single complaint record using its resolve token.

    Used by the /resolve endpoint to look up the complaint before
    marking it resolved and notifying the student.

    Args:
        resolve_token (str): The unique resolve token from the email link.

    Returns:
        dict or None: Full complaint record, or None if the token is not found.
    """
    try:
        response = (
            supabase.table("complaints")
            .select("*")
            .eq("resolve_token", resolve_token)
            .execute()
        )

        if response.data:
            return response.data[0]
        return None

    except Exception as e:
        print(f"❌ Database error: {e}")
        return None


def get_all_complaints():
    """
    Fetch all complaint records ordered by creation time (newest first).

    Used by the /complaints admin endpoint to give wardens a complete
    overview of all pending and resolved issues.

    Returns:
        list: List of complaint dicts. Returns empty list on error.
    """
    try:
        response = (
            supabase.table("complaints")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return response.data

    except Exception as e:
        print(f"❌ Database error: {e}")
        return []


# Manual test — run directly: python src/database.py
if __name__ == "__main__":
    print("🧪 Testing database connection...")
    complaints = get_all_complaints()
    print(f"✅ Connected! Total complaints in DB: {len(complaints)}")
