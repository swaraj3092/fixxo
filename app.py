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

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fixxo-super-secret-key-change-in-production-2026")

# CORS Configuration
CORS(app, 
     resources={r"/api/*": {"origins": ["http://localhost:3000", "https://hostel-complaint-system-1-r1g3.onrender.com"]}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])


@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming WhatsApp messages."""
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
            print("❌ Missing message or phone number")
            msg.body("Invalid request. Please try again.")
            return str(resp)
        
        # Check if student is registered
        student = check_student_exists(from_number)
        
        if not student:
            print(f"❌ Student not registered: {from_number}")
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
        
        # Student is registered - process complaint
        print(f"✅ Student found: {student.get('student_name', 'Unknown')}")
        print(f"   Hostel: {student.get('hostel_name', 'N/A')}")
        print(f"   Room: {student.get('room_number', 'N/A')}")
        
        # Classify the complaint
        classification = classify_complaint(incoming_msg)
        print(f"🤖 AI Classification: {classification.get('category', 'OTHER')}")
        
        # Create complaint
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
        
        # Send email
        print("📧 Sending email...")
        send_department_email(complaint)
        
        # Send confirmation
        dept_name = classification['department_email'].split('@')[0].replace('_', ' ').title()
        confirmation_message = f"""✅ Complaint Received!

📋 ID: #{complaint['resolve_token']}
👤 Name: {student['student_name']}
🏢 Location: {student['hostel_name']}, Room {student['room_number']}
🏷️ Category: {classification['category']}
⚡ Priority: {classification['priority']}
📧 Assigned to: {dept_name} Department

You'll be notified once resolved! 🔔"""
        
        msg.body(confirmation_message)
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


@app.route("/api/check-phone", methods=["GET"])
def check_phone():
    """Check if phone number is registered."""
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
    """Register new student."""
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
        
        existing_student = check_student_exists(data["phone_number"])
        if existing_student:
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


def require_admin(f):
    """Decorator to require admin authentication."""
    def decorated_function(*args, **kwargs):
        if "admin_id" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    """Admin login."""
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")
        
        print("=" * 60)
        print("🔐 ADMIN LOGIN ATTEMPT")
        print(f"Username: {username}")
        
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        
        response = supabase.table("admins").select("*").eq("username", username).eq("is_active", True).execute()
            
        if not response.data or len(response.data) == 0:
            return jsonify({"error": "Invalid credentials"}), 401
        
        admin = response.data[0]
        
        if admin['password_hash'] != password:
            return jsonify({"error": "Invalid credentials"}), 401
        
        session["admin_id"] = admin["id"]
        session["admin_username"] = admin["username"]
        
        try:
            supabase.table("admins").update({"last_login": datetime.utcnow().isoformat()}).eq("id", admin["id"]).execute()
        except:
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
    """Admin logout."""
    session.clear()
    return jsonify({"success": True}), 200


@app.route("/api/admin/stats", methods=["GET"])
@require_admin
def admin_stats():
    """Get dashboard statistics."""
    try:
        stats = get_dashboard_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/students", methods=["GET"])
@require_admin
def admin_get_students():
    """Get all students."""
    try:
        students = get_all_students()
        return jsonify(students), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/complaints", methods=["GET"])
@require_admin
def admin_get_complaints():
    """Get all complaints."""
    try:
        status = request.args.get("status")
        complaints = get_all_complaints(status=status)
        return jsonify(complaints), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/complaints/<complaint_id>", methods=["PUT"])
@require_admin
def admin_update_complaint(complaint_id):
    """Update complaint status."""
    try:
        data = request.json
        status = data.get("status")
        admin_notes = data.get("admin_notes")
        resolved_by = session.get("admin_username", "Admin")
        
        complaint = update_complaint_status(
            complaint_id=complaint_id,
            status=status,
            resolved_by=resolved_by,
            admin_notes=admin_notes
        )
        
        if complaint and status == "RESOLVED":
            send_whatsapp_notification(complaint)
        
        return jsonify({"success": True, "complaint": complaint}), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/resolve", methods=["GET"])
def resolve_complaint():
    """Resolve complaint via email link."""
    try:
        token = request.args.get("token")
        if not token:
            return "❌ Invalid resolution link", 400
        
        complaint = get_complaint_by_token(token)
        if not complaint:
            return "❌ Complaint not found", 404
        
        if complaint['status'] == 'RESOLVED':
            return f"""<!DOCTYPE html>
<html><head><title>Already Resolved</title></head>
<body style="font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
<div style="background: white; padding: 40px; border-radius: 20px; text-align: center;">
<div style="font-size: 80px;">✅</div>
<h1>Already Resolved</h1>
<p>Complaint #{complaint['resolve_token']} was already resolved.</p>
</div></body></html>"""
        
        updated_complaint = update_complaint_status(
            complaint_id=complaint['id'],
            status='RESOLVED',
            resolved_by='Department'
        )
        
        if updated_complaint:
            send_whatsapp_notification(updated_complaint)
        
        return f"""<!DOCTYPE html>
<html><head><title>Resolved</title></head>
<body style="font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
<div style="background: white; padding: 40px; border-radius: 20px; text-align: center;">
<div style="font-size: 80px;">🎉</div>
<h1>Complaint Resolved!</h1>
<p><strong>ID:</strong> #{complaint['resolve_token']}</p>
<p><strong>Category:</strong> {complaint['category']}</p>
<p style="color: #10b981; font-weight: bold;">✅ Student has been notified via WhatsApp</p>
</div></body></html>"""
        
    except Exception as e:
        print(f"❌ Resolution error: {e}")
        return f"❌ Error: {str(e)}", 500


# === REACT FRONTEND SERVING ===
# This MUST be at the end, after all API routes!

@app.route('/static/<path:filename>')
def serve_static_files(filename):
    """Serve static files (CSS, JS, images) from React build."""
    return send_from_directory(os.path.join(app.root_path, 'build', 'static'), filename)


@app.route('/favicon.ico')
def favicon():
    """Serve favicon."""
    return send_from_directory(os.path.join(app.root_path, 'build'), 'favicon.ico')


@app.route('/manifest.json')
def manifest():
    """Serve manifest."""
    return send_from_directory(os.path.join(app.root_path, 'build'), 'manifest.json')


@app.route('/logo192.png')
def logo192():
    """Serve logo."""
    return send_from_directory(os.path.join(app.root_path, 'build'), 'logo192.png')


@app.route('/logo512.png')
def logo512():
    """Serve logo."""
    return send_from_directory(os.path.join(app.root_path, 'build'), 'logo512.png')


# Catch-all route - MUST be absolute last!
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    """
    Serve React app for all non-API routes.
    This handles React Router paths like /register, /admin/login, etc.
    """
    # Skip if it's an API route (these should be handled by specific routes above)
    if path.startswith('api/'):
        return jsonify({"error": "API endpoint not found"}), 404
    
    if path.startswith('webhook'):
        return jsonify({"error": "Invalid webhook request"}), 404
    
    if path.startswith('resolve'):
        return jsonify({"error": "Invalid resolution link"}), 404
    
    # Check if it's a static file request
    file_path = os.path.join(app.root_path, 'build', path)
    if path and os.path.isfile(file_path):
        return send_from_directory(os.path.join(app.root_path, 'build'), path)
    
    # Otherwise, serve index.html for React Router to handle
    return send_from_directory(os.path.join(app.root_path, 'build'), 'index.html')


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)