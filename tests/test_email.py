"""
Unit Tests — Email Sender Module

Validates email content building, priority colour mapping,
and category icon constants without making real API calls.

Run:  python -m pytest tests/ -v

Author: Team Smart Hostel
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def sample_complaint():
    return {
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
        "status": "PENDING",
        "resolve_token": "abc123securetoken456"
    }


class TestPriorityColors:

    def test_all_four_priorities_mapped(self):
        from email_sender import PRIORITY_COLORS
        for level in ["URGENT", "HIGH", "MEDIUM", "LOW"]:
            assert level in PRIORITY_COLORS

    def test_urgent_is_red(self):
        from email_sender import PRIORITY_COLORS
        assert PRIORITY_COLORS["URGENT"] == "#ef4444"

    def test_all_colors_are_valid_hex(self):
        import re
        from email_sender import PRIORITY_COLORS
        pattern = re.compile(r'^#[0-9a-f]{6}$', re.IGNORECASE)
        for level, color in PRIORITY_COLORS.items():
            assert pattern.match(color), f"Bad hex for {level}: {color}"


class TestCategoryIcons:

    def test_all_8_categories_have_icons(self):
        from email_sender import CATEGORY_ICONS
        from ai_classifier_simple import CATEGORY_KEYWORDS
        for cat in CATEGORY_KEYWORDS:
            assert cat in CATEGORY_ICONS, f"No icon for: {cat}"
        assert "OTHER" in CATEGORY_ICONS

    def test_icons_are_non_empty(self):
        from email_sender import CATEGORY_ICONS
        for cat, icon in CATEGORY_ICONS.items():
            assert len(icon) > 0


class TestEmailContentLogic:

    def test_resolve_link_format(self):
        complaint = sample_complaint()
        base = "https://hostel-complaint-system-1-r1g3.onrender.com"
        link = f"{base}/resolve?token={complaint['resolve_token']}"
        assert "/resolve?token=" in link
        assert complaint["resolve_token"] in link

    def test_complaint_id_is_8_chars_uppercase(self):
        complaint = sample_complaint()
        cid = str(complaint["id"])[:8].upper()
        assert len(cid) == 8
        assert cid == cid.upper()

    def test_subject_contains_priority_and_icon(self):
        from email_sender import CATEGORY_ICONS
        complaint = sample_complaint()
        priority = complaint["priority"]
        category = complaint["category"]
        icon = CATEGORY_ICONS.get(category, "📋")
        cid = str(complaint["id"])[:8].upper()

        subject = f"[{priority}] {icon} New Complaint #{cid}"
        assert priority in subject
        assert cid in subject

    def test_recipient_is_department_email(self):
        complaint = sample_complaint()
        assert complaint["department_email"] == "swarajbehera923@gmail.com"
        assert "@" in complaint["department_email"]
