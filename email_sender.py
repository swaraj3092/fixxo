import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")


def send_department_email(complaint):
    """Send email notification to department with complaint details."""
    try:
        print("=" * 60)
        print("📧 EMAIL FUNCTION STARTED")
        print(f"   To: {complaint.get('department_email')}")

        resolve_link = f"{BASE_URL}/resolve?token={complaint['resolve_token']}"
        cant_resolve_link = f"{BASE_URL}/cant-resolve?token={complaint['resolve_token']}"

        priority_colors = {
            "URGENT": "#dc2626",
            "HIGH": "#ea580c",
            "MEDIUM": "#f59e0b",
            "LOW": "#3b82f6"
        }
        priority_color = priority_colors.get(complaint.get('priority', 'MEDIUM'), "#f59e0b")

        # Download image from Twilio for CID embedding (works in Gmail)
        image_attachment = None
        media_section = ""

        if complaint.get('media_url'):
            try:
                import requests as req
                twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
                twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
                img_response = req.get(
                    complaint['media_url'],
                    auth=(twilio_sid, twilio_token),
                    timeout=10
                )
                if img_response.status_code == 200:
                    img_data = img_response.content
                    img_mime = img_response.headers.get('Content-Type', 'image/jpeg')
                    # Use CID reference in HTML — this works in Gmail unlike data: URIs
                    media_section = """
                    <div style="margin:20px 0;">
                        <div style="font-weight:bold;color:#4b5563;margin-bottom:8px;">📷 Attached Photo:</div>
                        <img src="cid:complaint_image" style="max-width:100%;border-radius:8px;border:1px solid #e5e7eb;" />
                    </div>
                    """
                    image_attachment = (img_data, img_mime)
                    print(f"✅ Image downloaded: {len(img_data)} bytes")
                else:
                    print(f"⚠️ Image download failed: HTTP {img_response.status_code}")
            except Exception as img_err:
                print(f"⚠️ Could not embed image: {img_err}")

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f3f4f6; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; color: white; }}
                .header h1 {{ margin: 0; font-size: 28px; }}
                .content {{ padding: 30px; }}
                .priority-badge {{ display: inline-block; background-color: {priority_color}; color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold; font-size: 14px; }}
                .info-row {{ margin: 15px 0; padding: 12px; background-color: #f9fafb; border-left: 4px solid #667eea; border-radius: 4px; }}
                .info-label {{ font-weight: bold; color: #4b5563; margin-bottom: 5px; }}
                .info-value {{ color: #1f2937; font-size: 16px; }}
                .message-box {{ background-color: #eff6ff; border: 2px solid #3b82f6; border-radius: 8px; padding: 20px; margin: 20px 0; }}
                .resolve-button {{ display: inline-block; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px; margin: 20px 0; box-shadow: 0 4px 6px rgba(16,185,129,0.3); }}
                .footer {{ background-color: #f9fafb; padding: 20px; text-align: center; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏠 New Complaint Received</h1>
                    <p style="margin:10px 0 0 0;opacity:0.9;">Hostel Complaint Management System</p>
                </div>
                <div class="content">
                    <div style="text-align:center;margin-bottom:20px;">
                        <span class="priority-badge">⚡ {complaint.get('priority','MEDIUM')} PRIORITY</span>
                    </div>
                    <div class="info-row">
                        <div class="info-label">📋 Complaint ID:</div>
                        <div class="info-value">#{complaint['resolve_token']}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">👤 Student Name:</div>
                        <div class="info-value">{complaint.get('student_name','N/A')}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">📞 Contact:</div>
                        <div class="info-value">{complaint.get('student_phone','N/A')}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">🏢 Location:</div>
                        <div class="info-value">{complaint.get('hostel_name','N/A')}, Room {complaint.get('room_number','N/A')}</div>
                    </div>
                    <div class="info-row">
                        <div class="info-label">🏷️ Category:</div>
                        <div class="info-value">{complaint.get('category','OTHER')}</div>
                    </div>
                    <div class="message-box">
                        <div class="info-label">💬 Issue Description:</div>
                        <div class="info-value" style="margin-top:10px;">{complaint.get('raw_message','No description provided')}</div>
                    </div>

                    {media_section}

                    <div style="text-align:center;margin:30px 0;">
                        <a href="{resolve_link}" class="resolve-button">✅ Mark as Resolved</a>
                    </div>
                    <div style="text-align:center;margin:10px 0 30px 0;">
                        <a href="{cant_resolve_link}" style="color:#ef4444;font-size:14px;text-decoration:underline;">
                            ⚠️ Can't resolve this issue?
                        </a>
                    </div>
                    <p style="color:#6b7280;font-size:14px;text-align:center;">
                        Click the button above once the issue has been fixed. The student will be notified automatically.
                    </p>
                </div>
                <div class="footer">
                    <p style="margin:5px 0;">Powered by <strong>Fixxo</strong></p>
                    <p style="margin:5px 0;">Open Source Hostel Management System</p>
                </div>
            </div>
        </body>
        </html>
        """

        gmail_user = os.getenv("GMAIL_USER")
        gmail_pass = os.getenv("GMAIL_APP_PASSWORD")

        # Use 'related' for CID images, 'alternative' if no image
        if image_attachment:
            outer = MIMEMultipart("related")
            html_part = MIMEMultipart("alternative")
            html_part.attach(MIMEText(html_content, "html"))
            outer.attach(html_part)

            # Attach image with CID
            img_msg = MIMEImage(image_attachment[0])
            img_msg.add_header("Content-ID", "<complaint_image>")
            img_msg.add_header("Content-Disposition", "inline", filename="complaint.jpg")
            outer.attach(img_msg)
        else:
            outer = MIMEMultipart("alternative")
            outer.attach(MIMEText(html_content, "html"))

        outer["Subject"] = f"[{complaint.get('priority','MEDIUM')}] {complaint.get('category','NEW')} Issue - {complaint.get('hostel_name','Hostel')} Room {complaint.get('room_number','N/A')}"
        outer["From"] = f"Fixxo <{gmail_user}>"
        outer["To"] = complaint['department_email']

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, complaint['department_email'], outer.as_string())

        print("✅ EMAIL SENT SUCCESSFULLY")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"❌ EMAIL ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return False


def send_whatsapp_notification(complaint):
    """Send WhatsApp notification to student when complaint is resolved."""
    try:
        from twilio.rest import Client

        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        twilio_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

        client = Client(account_sid, auth_token)

        base_url = os.getenv("BASE_URL", "http://localhost:5000")
        feedback_link = f"{base_url}/feedback?token={complaint['resolve_token']}"

        message_body = f"""✅ Great news!

Your complaint #{complaint['resolve_token']} has been RESOLVED!

📋 Issue: {complaint['category']}
🏢 Location: {complaint.get('hostel_name', 'N/A')}, Room {complaint.get('room_number', 'N/A')}
✅ Resolved by: {complaint.get('resolved_by', 'Department')}

⭐ Share your feedback (optional):
{feedback_link}

Thank you for reporting! 🎉"""

        message = client.messages.create(
            from_=twilio_number,
            body=message_body,
            to=complaint['student_phone']
        )

        print(f"✅ WhatsApp notification sent: {message.sid}")
        return True

    except Exception as e:
        print(f"❌ Failed to send WhatsApp notification: {e}")
        return False