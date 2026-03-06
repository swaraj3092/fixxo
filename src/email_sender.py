"""
Email Notification Module

Sends styled HTML complaint notification emails to departments via Resend API.

Each email contains:
  - Complaint metadata (category, priority, hostel, room, student phone)
  - The student's original message in a quote block
  - A colour-coded priority banner (red=URGENT, orange=HIGH, yellow=MEDIUM)
  - A prominent green "Mark as Resolved" button linked to the /resolve endpoint

When the department clicks the resolve button:
  - The complaint is updated to RESOLVED in the database
  - The student receives an automatic WhatsApp notification

Author: Team Smart Hostel
Version: 1.0.0
License: Apache 2.0
"""

import os
import resend
from dotenv import load_dotenv

load_dotenv()

# Resend API key — set RESEND_API_KEY in your .env file or Render env vars
resend.api_key = os.getenv("RESEND_API_KEY")

# Sender display name shown to department recipients
GMAIL_USER = os.getenv("GMAIL_USER")

# Colour coding for the priority banner in the email header
PRIORITY_COLORS = {
    "URGENT": "#ef4444",  # Red
    "HIGH": "#f97316",    # Orange
    "MEDIUM": "#eab308",  # Yellow
    "LOW": "#22c55e"      # Green
}

# Emoji icons displayed in the email subject line and body heading
CATEGORY_ICONS = {
    "PLUMBING": "🔧",
    "ELECTRICAL": "⚡",
    "CLEANLINESS": "🧹",
    "SECURITY": "🔒",
    "WIFI": "📶",
    "FOOD": "🍽️",
    "FURNITURE": "🪑",
    "OTHER": "📋"
}


def send_department_email(complaint, resolve_base_url):
    """
    Send a styled HTML notification email to the responsible department.

    Builds a full HTML email with complaint metadata and a one-click
    resolve button, then delivers it via the Resend API. Returns True
    on success so app.py can log the outcome without crashing.

    Args:
        complaint (dict): The saved complaint record from the database.
                          Required keys: id, student_phone, hostel_name,
                          room_number, category, priority, raw_message,
                          department_email, confidence, resolve_token.
        resolve_base_url (str): Public base URL of the server used to build
                                the resolve link inside the email button.
                                Example: "https://app.onrender.com"

    Returns:
        bool: True if email was sent successfully via Resend, False on any error.

    Example:
        >>> success = send_department_email(saved_complaint, "https://app.onrender.com")
        >>> print(success)
        True
    """
    print("=" * 60)
    print("📧 EMAIL FUNCTION STARTED")
    print(f"To: {complaint.get('department_email')}")
    print("=" * 60)

    try:
        # Build the one-time resolve URL embedded in the button
        resolve_link = f"{resolve_base_url}/resolve?token={complaint['resolve_token']}"

        priority = complaint.get("priority", "MEDIUM")
        category = complaint.get("category", "OTHER")
        priority_color = PRIORITY_COLORS.get(priority, "#eab308")
        category_icon = CATEGORY_ICONS.get(category, "📋")

        # Short 8-char display ID shown in subject and body
        complaint_id = str(complaint["id"])[:8].upper()

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f5f5f5;">

            <!-- Header -->
            <div style="background: #1e293b; color: white; padding: 25px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="margin: 0; font-size: 22px;">🏠 Hostel Complaint System</h1>
                <p style="margin: 5px 0 0 0; color: #94a3b8;">New complaint assigned to your department</p>
            </div>

            <!-- Priority Banner -->
            <div style="background: {priority_color}; color: white; padding: 12px; text-align: center;">
                <strong>⚡ PRIORITY: {priority}</strong>
            </div>

            <!-- Complaint Details -->
            <div style="background: white; padding: 25px;">

                <h2 style="color: #1e293b;">
                    {category_icon} {category} Issue — #{complaint_id}
                </h2>

                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 5px;"><strong>Student Phone</strong></td>
                        <td style="padding: 8px 5px;">{complaint.get('student_phone')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 5px;"><strong>Hostel</strong></td>
                        <td style="padding: 8px 5px;">{complaint.get('hostel_name') or 'Not specified'}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 5px;"><strong>Room</strong></td>
                        <td style="padding: 8px 5px;">{complaint.get('room_number') or 'Not specified'}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 5px;"><strong>Category</strong></td>
                        <td style="padding: 8px 5px;">{category}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 5px;"><strong>Priority</strong></td>
                        <td style="padding: 8px 5px;">{priority}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 5px;"><strong>Confidence</strong></td>
                        <td style="padding: 8px 5px;">{complaint.get('confidence', 0)}%</td>
                    </tr>
                </table>

                <br>

                <div style="background: #f8fafc; padding: 15px; border-radius: 8px;">
                    <strong>Student Message:</strong>
                    <p>{complaint.get('raw_message')}</p>
                </div>

                <br>

                <div style="text-align: center;">
                    <a href="{resolve_link}"
                       style="background: #22c55e; color: white; padding: 15px 40px;
                              text-decoration: none; border-radius: 8px; font-size: 16px;
                              font-weight: bold; display: inline-block;">
                        ✅ Mark as Resolved
                    </a>
                </div>

            </div>

            <!-- Footer -->
            <div style="background: #f1f5f9; padding: 15px; text-align: center;">
                <p style="font-size: 13px; color: #94a3b8; margin: 0;">
                    Automated email from Hostel Complaint System. Do not reply.
                </p>
            </div>

        </body>
        </html>
        """

        print("📧 Sending email via Resend API...")

        params = {
            "from": "Hostel Complaint System <onboarding@resend.dev>",
            "to": [complaint.get("department_email")],
            "subject": f"[{priority}] {category_icon} New Complaint #{complaint_id}",
            "html": html_content,
        }

        resend.Emails.send(params)

        print("=" * 60)
        print("✅ EMAIL SENT SUCCESSFULLY via Resend")
        print("=" * 60)
        return True

    except Exception as e:
        print("=" * 60)
        print(f"❌ EMAIL ERROR: {e}")
        print("=" * 60)
        return False
