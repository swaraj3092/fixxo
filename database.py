from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime
import uuid

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def check_student_exists(phone_number):
    """Check if student exists in database."""
    try:
        response = supabase.table("students").select("*").eq("phone_number", phone_number).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"❌ Error checking student: {e}")
        return None


def get_student_by_phone(phone_number):
    """Get student details by phone number."""
    try:
        response = supabase.table("students").select("*").eq("phone_number", phone_number).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"❌ Error getting student: {e}")
        return None


def register_student(phone_number, college_id, roll_number, student_name, hostel_name, room_number, email=None):
    """Register a new student."""
    try:
        data = {
            "phone_number": phone_number,
            "college_id": college_id,
            "roll_number": roll_number,
            "student_name": student_name,
            "hostel_name": hostel_name,
            "room_number": room_number,
            "email": email,
            "is_approved": True
        }
        
        response = supabase.table("students").insert(data).execute()
        
        if response.data and len(response.data) > 0:
            print(f"✅ Student registered: {student_name}")
            return response.data[0]
        return None
    except Exception as e:
        print(f"❌ Error registering student: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_complaint(student_id, student_phone, student_name, hostel_name, room_number,
                    category, priority, raw_message, summary, department_email, confidence,
                    media_url=None):
    """Create a new complaint."""
    try:
        resolve_token = str(uuid.uuid4())[:8].upper()
        
        data = {
            "student_id": student_id,
            "student_phone": student_phone,
            "student_name": student_name,
            "hostel_name": hostel_name,
            "room_number": room_number,
            "category": category,
            "priority": priority,
            "raw_message": raw_message,
            "summary": summary,
            "department_email": department_email,
            "confidence": confidence,
            "status": "PENDING",
            "resolve_token": resolve_token,
            "media_url": media_url  # optional photo from WhatsApp
        }
        
        print(f"📝 Creating complaint with data: {data}")
        
        response = supabase.table("complaints").insert(data).execute()
        
        if response.data and len(response.data) > 0:
            print(f"✅ Complaint created: {resolve_token}")
            return response.data[0]
        return None
    except Exception as e:
        print(f"❌ Error creating complaint: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_all_students():
    """Get all students."""
    try:
        response = supabase.table("students").select("*").order("created_at", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Error getting students: {e}")
        return []


def get_all_complaints(status=None):
    """Get all complaints, optionally filtered by status."""
    try:
        query = supabase.table("complaints").select("*")
        
        if status:
            query = query.eq("status", status)
        
        response = query.order("created_at", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Error getting complaints: {e}")
        return []


def get_dashboard_stats():
    """Get dashboard statistics."""
    try:
        students_response = supabase.table("students").select("id", count="exact").execute()
        total_students = students_response.count if students_response.count else 0
        
        complaints_response = supabase.table("complaints").select("id", count="exact").execute()
        total_complaints = complaints_response.count if complaints_response.count else 0
        
        pending_response = supabase.table("complaints").select("id", count="exact").eq("status", "PENDING").execute()
        pending = pending_response.count if pending_response.count else 0
        
        resolved_response = supabase.table("complaints").select("id", count="exact").eq("status", "RESOLVED").execute()
        resolved = resolved_response.count if resolved_response.count else 0
        
        return {
            "total_students": total_students,
            "total_complaints": total_complaints,
            "pending": pending,
            "resolved": resolved
        }
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return {
            "total_students": 0,
            "total_complaints": 0,
            "pending": 0,
            "resolved": 0
        }


def update_complaint_status(complaint_id, status, resolved_by=None, admin_notes=None):
    """Update complaint status."""
    try:
        data = {
            "status": status,
            "resolved_at": datetime.utcnow().isoformat() if status == "RESOLVED" else None,
            "resolved_by": resolved_by,
            "admin_notes": admin_notes
        }
        
        response = supabase.table("complaints").update(data).eq("id", complaint_id).execute()
        
        if response.data and len(response.data) > 0:
            print(f"✅ Complaint status updated: {status}")
            return response.data[0]
        return None
    except Exception as e:
        print(f"❌ Error updating complaint: {e}")
        return None


def get_complaint_by_token(resolve_token):
    """Get complaint by resolve token."""
    try:
        response = supabase.table("complaints").select("*").eq("resolve_token", resolve_token).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"❌ Error getting complaint by token: {e}")
        return None