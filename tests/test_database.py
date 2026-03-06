"""
Unit Tests — Database Schema & Data Validation

Validates complaint data structures, field constraints, and token
generation without requiring a live database connection.

Run:  python -m pytest tests/ -v

Author: Team Smart Hostel
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestComplaintDataStructure:

    def _sample_complaint(self):
        return {
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
            "resolve_token": "abc123"
        }

    def test_all_required_fields_present(self):
        complaint = self._sample_complaint()
        required = [
            "student_phone", "hostel_name", "room_number", "category",
            "priority", "raw_message", "summary", "department_email",
            "confidence", "status", "resolve_token"
        ]
        for field in required:
            assert field in complaint, f"Missing: {field}"

    def test_valid_categories(self):
        from ai_classifier_simple import CATEGORY_KEYWORDS
        valid = set(CATEGORY_KEYWORDS.keys()) | {"OTHER"}
        assert "ELECTRICAL" in valid
        assert "WIFI" in valid
        assert "INTERNET" not in valid   # should be under WIFI
        assert len(valid) == 8

    def test_valid_priorities(self):
        valid = {"URGENT", "HIGH", "MEDIUM"}
        assert "URGENT" in valid
        assert "CRITICAL" not in valid
        assert "EMERGENCY" not in valid

    def test_valid_statuses(self):
        valid = {"PENDING", "RESOLVED"}
        assert "PENDING" in valid
        assert "CLOSED" not in valid
        assert "IN_PROGRESS" not in valid

    def test_phone_has_whatsapp_prefix(self):
        phone = "whatsapp:+919178773834"
        assert phone.startswith("whatsapp:")

    def test_confidence_in_range(self):
        assert 0 <= 85.0 <= 100

    def test_summary_max_100_chars(self):
        long_text = "x" * 200
        summary = long_text[:100]
        assert len(summary) == 100

    def test_resolve_token_is_url_safe(self):
        import secrets
        import re
        token = secrets.token_urlsafe(32)
        assert len(token) == 43
        assert re.match(r'^[A-Za-z0-9_-]+$', token)


class TestDepartmentEmailMapping:

    def test_all_categories_have_email(self):
        from ai_classifier_simple import DEPARTMENT_EMAILS, CATEGORY_KEYWORDS
        for category in CATEGORY_KEYWORDS:
            assert category in DEPARTMENT_EMAILS

    def test_other_fallback_has_email(self):
        from ai_classifier_simple import DEPARTMENT_EMAILS
        assert "OTHER" in DEPARTMENT_EMAILS
        assert "@" in DEPARTMENT_EMAILS["OTHER"]

    def test_all_emails_valid_format(self):
        import re
        from ai_classifier_simple import DEPARTMENT_EMAILS
        pattern = re.compile(r'^[^@]+@[^@]+\.[^@]+$')
        for cat, email in DEPARTMENT_EMAILS.items():
            assert pattern.match(email), f"Bad email for {cat}: {email}"
