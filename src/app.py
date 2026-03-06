"""
Smart Hostel Complaint Management System — Flask Application

Core server that handles:
  - Receiving WhatsApp messages via Twilio webhook (/webhook)
  - Classifying complaints and saving them to Supabase
  - Routing HTML email notifications to the responsible department
  - One-click complaint resolution for departments (/resolve)
  - Sending WhatsApp resolution notifications back to students (/resolve)

Run locally:
    python src/app.py

Deploy:
    Configured for Render via render.yaml
    See docs/INSTALLATION.md for full setup guide.

Author: Team Smart Hostel
Version: 1.0.0
License: Apache 2.0
"""

from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv
from ai_classifier_simple import classify_complaint
from database import save_complaint, resolve_complaint, get_complaint_by_token
from email_sender import send_department_email
import os

load_dotenv()

app = Flask(__name__)

# Twilio client — used for sending outbound WhatsApp resolution messages
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

# Public server URL — used to build the resolve link inside department emails
BASE_URL = os.getenv("BASE_URL", "https://hostel-complaint-system-1-r1g3.onrender.com")


@app.route("/", methods=["GET"])
def home():
    """Health check — confirms the server is live."""
    return "🏠 Hostel Complaint System is running!", 200


@app.route("/test", methods=["GET"])
def test():
    """Debug route — verifies Flask is responding correctly."""
    return "Test successful!", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Main webhook — Twilio calls this on every incoming WhatsApp message.

    Flow:
        1. Parse the message body, sender phone, and optional image URL
        2. Classify complaint (category, priority, hostel name, room number)
        3. Save the complaint to Supabase with a secure one-time resolve token
        4. Email the correct department with a "Mark as Resolved" button
        5. Send an acknowledgement WhatsApp reply to the student

    Returns:
        str: TwiML XML response consumed by Twilio.
    """
    incoming_message = request.form.get("Body", "").strip()
    sender_phone = request.form.get("From", "")
    media_url = request.form.get("MediaUrl0", None)

    print(f"\n📨 New message from {sender_phone}")
    print(f"📝 Message: {incoming_message}")

    response = MessagingResponse()

    if not incoming_message:
        response.message("Please send a text description of your complaint.")
        return str(response)

    # Step 1: Classify
    print("🤖 Classifying complaint...")
    ai_result = classify_complaint(incoming_message, media_url)
    print(f"   Category: {ai_result['category']}, Priority: {ai_result['priority']}")

    # Step 2: Save to database
    print("💾 Saving to database...")
    saved = save_complaint(sender_phone, incoming_message, ai_result)

    if saved:
        complaint_id = str(saved["id"])[:8].upper()
        print(f"✅ Saved! ID: {complaint_id}")

        # Step 3: Send email to department
        print(f"📧 Sending email to {saved['department_email']}...")
        email_sent = send_department_email(saved, BASE_URL)

        if email_sent:
            print("✅ Email sent successfully!")
        else:
            print("⚠️ Email failed but complaint is saved")

        # Step 4: Reply to student
        response.message(
            f"✅ Complaint Received!\n\n"
            f"📋 ID: #{complaint_id}\n"
            f"🏷️ Category: {ai_result.get('category')}\n"
            f"⚡ Priority: {ai_result.get('priority')}\n"
            f"🏢 Assigned to: {ai_result.get('department_email')}\n\n"
            f"You will be notified on WhatsApp once resolved. Thank you!"
        )
    else:
        print("❌ Failed to save to database")
        response.message(
            "✅ Complaint received! Our team will look into it shortly."
        )

    return str(response)


@app.route("/resolve", methods=["GET"])
def resolve():
    """
    Resolution endpoint — departments click this link from their email to close a complaint.

    Query Parameters:
        token (str): Unique secure resolve token embedded in the email link.
        note (str, optional): Resolution message from the department.

    Flow:
        1. Validate the token
        2. Look up the complaint in the database
        3. Guard against double-resolution (already RESOLVED check)
        4. Mark complaint as RESOLVED, set resolved_at timestamp
        5. Send WhatsApp notification to student
        6. Return a styled HTML confirmation page

    Returns:
        str: HTML confirmation page (200) or plain error string (400/404/500).
    """
    token = request.args.get("token")
    note = request.args.get("note", "Issue has been resolved.")

    if not token:
        return "❌ Invalid link.", 400

    complaint = get_complaint_by_token(token)

    if not complaint:
        return "❌ Complaint not found.", 404

    if complaint["status"] == "RESOLVED":
        return "✅ This complaint was already resolved.", 200

    updated = resolve_complaint(token, note)

    if updated:
        # Notify student via WhatsApp
        try:
            print(f"📲 Sending resolution notification to {complaint['student_phone']}")
            twilio_client.messages.create(
                from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
                to=complaint["student_phone"],
                body=(
                    f"✅ Great news!\n\n"
                    f"Your complaint #{str(complaint['id'])[:8].upper()} has been resolved!\n\n"
                    f"🏷️ Issue: {complaint.get('summary', complaint.get('category'))}\n"
                    f"🏢 Resolved by: {complaint.get('department_email')}\n\n"
                    f"Thank you for reporting. — Hostel Management"
                )
            )
            print("✅ Resolution notification sent!")
        except Exception as e:
            print(f"⚠️ WhatsApp notification failed: {e}")

        return f"""
        <html>
        <body style="font-family: Arial; text-align: center; padding: 50px; background: #f0fdf4;">
            <div style="max-width: 500px; margin: 0 auto; background: white; padding: 40px;
                        border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
                <div style="font-size: 60px;">✅</div>
                <h1 style="color: #16a34a;">Complaint Resolved!</h1>
                <p style="color: #64748b;">The student has been notified via WhatsApp.</p>
                <hr style="border: 1px solid #e2e8f0; margin: 20px 0;">
                <p><b>Category:</b> {complaint['category']}</p>
                <p><b>Student:</b> {complaint['student_phone']}</p>
                <p><b>Issue:</b> {complaint.get('summary', '')}</p>
            </div>
        </body>
        </html>
        """, 200

    return "❌ Something went wrong.", 500


@app.route("/complaints", methods=["GET"])
def view_complaints():
    """
    Admin endpoint — returns all complaints as JSON, newest first.

    Returns:
        JSON: Array of all complaint records from the database.
    """
    from database import get_all_complaints
    complaints = get_all_complaints()
    return jsonify(complaints), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
