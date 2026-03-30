from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
from datetime import datetime
import time
import random

from database import (
    supabase,
    check_student_exists,
    register_student,
    get_student_by_phone,
    create_complaint,
    get_all_students,
    get_all_complaints,
    get_dashboard_stats,
    update_complaint_status,
    get_complaint_by_token
)
from ai_classifier import classify_complaint
from email_sender import send_department_email, send_whatsapp_notification

load_dotenv()

# Key fix: point Flask's static folder directly at build/static
# so /static/css/... and /static/js/... are served automatically
app = Flask(__name__, static_folder='build/static', static_url_path='/static')
app.secret_key = os.getenv("SECRET_KEY", "fixxo-super-secret-key-change-in-production-2026")

CORS(app,
     resources={r"/api/*": {"origins": ["http://localhost:3000", "https://hostel-complaint-system-1-r1g3.onrender.com" , "https://fixxo-v2.vercel.app"]}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])


# ─────────────────────────────────────────────
#  WhatsApp Webhook
# ─────────────────────────────────────────────

@app.route("/webhook", methods=["POST"])
def webhook():
    resp = MessagingResponse()
    msg = resp.message()

    try:
        incoming_msg = request.values.get("Body", "").strip()
        from_number = request.values.get("From", "")

        print("=" * 60)
        print("📱 INCOMING WHATSAPP MESSAGE")
        print(f"From: {from_number}")
        print(f"Message: {incoming_msg}")

        if not incoming_msg or not from_number:
            msg.body("Invalid request. Please try again.")
            return str(resp)

        student = check_student_exists(from_number)

        if not student:
            base_url = os.getenv("BASE_URL", "http://localhost:3000")
            phone = from_number.replace("whatsapp:+", "")
            registration_link = f"{base_url}/register?phone={phone}"

            msg.body(f"""👋 Welcome to Fixxo!

Please register first (one-time only):
🔗 {registration_link}

After registration, send your complaint again!""")

            print(f"✅ Registration link sent: {registration_link}")
            print("=" * 60)
            return str(resp)

        print(f"✅ Student found: {student.get('student_name', 'Unknown')}")
        print(f"   Hostel: {student.get('hostel_name', 'N/A')}")
        print(f"   Room: {student.get('room_number', 'N/A')}")

        classification = classify_complaint(incoming_msg)
        print(f"🤖 AI Classification: {classification.get('category', 'OTHER')}")

        complaint = create_complaint(
            student_id=student['id'],
            student_phone=from_number,
            student_name=student['student_name'],
            hostel_name=student['hostel_name'],
            room_number=student['room_number'],
            category=classification['category'],
            priority=classification['priority'],
            raw_message=incoming_msg,
            summary=classification['summary'],
            department_email=classification['department_email'],
            confidence=classification['confidence']
        )

        if not complaint:
            msg.body("Failed to save your complaint. Please try again.")
            print("=" * 60)
            return str(resp)

        print(f"✅ Complaint created: #{complaint['resolve_token']}")

        print("📧 Sending email...")
        send_department_email(complaint)

        dept_name = classification['department_email'].split('@')[0].replace('_', ' ').title()
        msg.body(f"""✅ Complaint Received!

📋 ID: #{complaint['resolve_token']}
👤 Name: {student['student_name']}
🏢 Location: {student['hostel_name']}, Room {student['room_number']}
🏷️ Category: {classification['category']}
⚡ Priority: {classification['priority']}
📧 Assigned to: {dept_name} Department

You'll be notified once resolved! 🔔""")

        print("✅ WhatsApp confirmation sent")
        print("=" * 60)
        return str(resp)

    except Exception as e:
        print(f"❌ WEBHOOK ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        msg.body("System error. Please try again or contact support.")
        return str(resp)


# ─────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────

@app.route("/api/check-phone", methods=["GET"])
def check_phone():
    phone = request.args.get("phone")
    if not phone:
        return jsonify({"error": "Phone number required"}), 400

    if not phone.startswith("whatsapp:"):
        if not phone.startswith("+"):
            phone = f"+{phone}"
        phone = f"whatsapp:{phone}"

    student = check_student_exists(phone)
    return jsonify({"registered": student is not None})


@app.route("/api/register", methods=["POST"])
def api_register():
    try:
        data = request.json

        print("=" * 60)
        print("📝 REGISTRATION REQUEST")
        print(f"Data: {data}")

        required_fields = ["phone_number", "roll_number", "student_name", "hostel_name", "room_number"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing field: {field}"}), 400

        if not data.get("college_id"):
            data["college_id"] = f"FIXXO{int(time.time())}"

        if check_student_exists(data["phone_number"]):
            return jsonify({"error": "Phone number already registered"}), 400

        student = register_student(
            phone_number=data["phone_number"],
            college_id=data["college_id"],
            roll_number=data["roll_number"],
            student_name=data["student_name"],
            hostel_name=data["hostel_name"],
            room_number=data["room_number"],
            email=data.get("email")
        )

        if student:
            print("✅ Registration successful")
            print("=" * 60)
            return jsonify({"success": True, "student": student}), 201
        else:
            return jsonify({"error": "Registration failed"}), 500

    except Exception as e:
        print(f"❌ Registration error: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
#  Admin Auth
# ─────────────────────────────────────────────

def require_admin(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "admin_id" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        print("=" * 60)
        print(f"🔐 ADMIN LOGIN: {username}")

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        response = supabase.table("admins").select("*").eq("username", username).eq("is_active", True).execute()

        if not response.data:
            return jsonify({"error": "Invalid credentials"}), 401

        admin = response.data[0]

        if admin['password_hash'] != password:
            return jsonify({"error": "Invalid credentials"}), 401

        session["admin_id"] = admin["id"]
        session["admin_username"] = admin["username"]

        try:
            supabase.table("admins").update({"last_login": datetime.utcnow().isoformat()}).eq("id", admin["id"]).execute()
        except Exception:
            pass

        print("✅ Login successful")
        print("=" * 60)
        return jsonify({
            "success": True,
            "admin": {
                "id": admin["id"],
                "username": admin["username"],
                "email": admin.get("email"),
                "full_name": admin.get("full_name")
            }
        }), 200

    except Exception as e:
        print(f"❌ Login error: {e}")
        print("=" * 60)
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/logout", methods=["POST"])
def admin_logout():
    session.clear()
    return jsonify({"success": True}), 200


# ─────────────────────────────────────────────
#  Admin Data Endpoints
# ─────────────────────────────────────────────

@app.route("/api/admin/stats", methods=["GET"])
@require_admin
def admin_stats():
    try:
        return jsonify(get_dashboard_stats()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/students", methods=["GET"])
@require_admin
def admin_get_students():
    try:
        return jsonify(get_all_students()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/complaints", methods=["GET"])
@require_admin
def admin_get_complaints():
    try:
        status = request.args.get("status")
        return jsonify(get_all_complaints(status=status)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/complaints/<complaint_id>", methods=["PUT"])
@require_admin
def admin_update_complaint(complaint_id):
    try:
        data = request.json
        complaint = update_complaint_status(
            complaint_id=complaint_id,
            status=data.get("status"),
            resolved_by=session.get("admin_username", "Admin"),
            admin_notes=data.get("admin_notes")
        )
        if complaint and data.get("status") == "RESOLVED":
            send_whatsapp_notification(complaint)
        return jsonify({"success": True, "complaint": complaint}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
#  Resolve via Email Link
# ─────────────────────────────────────────────

@app.route("/resolve", methods=["GET"])
def resolve_complaint():
    try:
        token = request.args.get("token")
        if not token:
            return "❌ Invalid resolution link", 400

        complaint = get_complaint_by_token(token)
        if not complaint:
            return "❌ Complaint not found", 404

        if complaint['status'] == 'RESOLVED':
            return f"""<!DOCTYPE html><html><head><title>Already Resolved</title></head>
<body style="font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;background:linear-gradient(135deg,#667eea,#764ba2);">
<div style="background:white;padding:40px;border-radius:20px;text-align:center;">
<div style="font-size:80px;">✅</div><h1>Already Resolved</h1>
<p>Complaint #{complaint['resolve_token']} was already resolved.</p>
</div></body></html>"""

        updated = update_complaint_status(
            complaint_id=complaint['id'],
            status='RESOLVED',
            resolved_by='Department'
        )

        if updated:
            send_whatsapp_notification(updated)

        return f"""<!DOCTYPE html><html><head><title>Resolved</title></head>
<body style="font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;background:linear-gradient(135deg,#10b981,#059669);">
<div style="background:white;padding:40px;border-radius:20px;text-align:center;">
<div style="font-size:80px;">🎉</div><h1>Complaint Resolved!</h1>
<p><strong>ID:</strong> #{complaint['resolve_token']}</p>
<p><strong>Category:</strong> {complaint['category']}</p>
<p style="color:#10b981;font-weight:bold;">✅ Student has been notified via WhatsApp</p>
</div></body></html>"""

    except Exception as e:
        print(f"❌ Resolution error: {e}")
        return f"❌ Error: {str(e)}", 500


# ─────────────────────────────────────────────
#  Serve React Build (must come LAST)
# ─────────────────────────────────────────────

BUILD_DIR = os.path.join(os.path.dirname(__file__), 'build')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(BUILD_DIR, 'favicon.ico')


@app.route('/manifest.json')
def manifest():
    return send_from_directory(BUILD_DIR, 'manifest.json')


@app.route('/logo192.png')
def logo192():
    return send_from_directory(BUILD_DIR, 'logo192.png')


@app.route('/logo512.png')
def logo512():
    return send_from_directory(BUILD_DIR, 'logo512.png')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    """Catch-all: serve React index.html for any non-API route."""
    # Let the explicit API/webhook/resolve routes handle their own 404s
    if path.startswith(('api/', 'webhook', 'resolve', 'static/')):
        return jsonify({"error": "Not found"}), 404

    # If it's a real file in the build folder, serve it directly
    full_path = os.path.join(BUILD_DIR, path)
    if path and os.path.isfile(full_path):
        return send_from_directory(BUILD_DIR, path)

    # Otherwise hand off to React Router
    return send_from_directory(BUILD_DIR, 'index.html')


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)