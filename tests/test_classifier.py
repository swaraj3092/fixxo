"""
Unit Tests — AI Complaint Classifier

Tests all functions in ai_classifier_simple.py using real-world
complaint messages from the hostel system.

Run:  python -m pytest tests/ -v

Author: Team Smart Hostel
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ai_classifier_simple import (
    classify_complaint,
    extract_hostel_name,
    extract_room_number,
    classify_category,
    classify_priority,
    DEPARTMENT_EMAILS,
    CATEGORY_KEYWORDS,
)


# ──────────────────────────────────────────────
# HOSTEL NAME EXTRACTION
# ──────────────────────────────────────────────

class TestExtractHostelName:

    def test_kp7_with_dash(self):
        assert extract_hostel_name("KP-7 hostel room 312") == "KP-7"

    def test_kp7_no_dash(self):
        result = extract_hostel_name("KP7 room 312 fan not working")
        assert result is not None and "KP" in result

    def test_block_a_format(self):
        assert extract_hostel_name("WiFi down in Block A Room 204") == "BLOCKA"

    def test_block_lowercase(self):
        result = extract_hostel_name("problem in block b room 301")
        assert result is not None and "BLOCK" in result

    def test_kaveri_hostel(self):
        result = extract_hostel_name("Problem in Kaveri Hostel Room 101")
        assert result == "KAVERIHOSTEL"

    def test_no_hostel_mentioned(self):
        assert extract_hostel_name("The tap is leaking in my room") is None

    def test_result_is_uppercase(self):
        result = extract_hostel_name("block c room 204")
        if result:
            assert result == result.upper()


# ──────────────────────────────────────────────
# ROOM NUMBER EXTRACTION
# ──────────────────────────────────────────────

class TestExtractRoomNumber:

    def test_room_keyword_3_digit(self):
        assert extract_room_number("Tap leaking in Room 204") == "204"

    def test_room_keyword_4_digit(self):
        assert extract_room_number("Issue in Room 2041") == "2041"

    def test_rm_shorthand(self):
        assert extract_room_number("rm 101 has a leaking tap") == "101"

    def test_hash_prefix(self):
        assert extract_room_number("issue in #312") == "312"

    def test_standalone_3_digit(self):
        assert extract_room_number("KP-7 hostel room 312 fan not working urgent") == "312"

    def test_no_room_number(self):
        assert extract_room_number("WiFi is down in hostel") is None

    def test_room_no_format(self):
        result = extract_room_number("room no 204 has no water")
        assert result == "204"


# ──────────────────────────────────────────────
# CATEGORY CLASSIFICATION
# ──────────────────────────────────────────────

class TestClassifyCategory:

    def test_plumbing_tap(self):
        assert classify_category("The bathroom tap is leaking badly") == "PLUMBING"

    def test_plumbing_toilet(self):
        assert classify_category("Toilet flush is not working") == "PLUMBING"

    def test_electrical_fan(self):
        assert classify_category("The ceiling fan is not working in room") == "ELECTRICAL"

    def test_electrical_light(self):
        assert classify_category("Light bulb broken, room is dark") == "ELECTRICAL"

    def test_wifi(self):
        assert classify_category("Internet connection is very slow today") == "WIFI"

    def test_wifi_router(self):
        assert classify_category("The router is down, no network") == "WIFI"

    def test_security_stranger(self):
        assert classify_category("There is a stranger in the corridor") == "SECURITY"

    def test_security_lock(self):
        assert classify_category("The door lock is broken") == "SECURITY"

    def test_food(self):
        assert classify_category("The mess food quality is very bad") == "FOOD"

    def test_cleanliness(self):
        assert classify_category("The room is dirty and smells bad") == "CLEANLINESS"

    def test_furniture(self):
        assert classify_category("The bed is broken, mattress on floor") == "FURNITURE"

    def test_other_no_keywords(self):
        assert classify_category("Something is wrong here") == "OTHER"

    def test_case_insensitive(self):
        assert classify_category("TAP IS LEAKING IN BATHROOM") == "PLUMBING"

    def test_kp7_fan_complaint(self):
        """Actual test message from test_gemini.py."""
        assert classify_category("KP-7 hostel room 312 fan not working urgent") == "ELECTRICAL"


# ──────────────────────────────────────────────
# PRIORITY CLASSIFICATION
# ──────────────────────────────────────────────

class TestClassifyPriority:

    def test_urgent_keyword(self):
        assert classify_priority("No water since morning urgent") == "URGENT"

    def test_emergency_keyword(self):
        assert classify_priority("This is an emergency please fix") == "URGENT"

    def test_high_not_working(self):
        assert classify_priority("Fan is not working in room") == "HIGH"

    def test_high_broken(self):
        assert classify_priority("The tap is completely broken") == "HIGH"

    def test_medium_default(self):
        assert classify_priority("WiFi is a bit slow today") == "MEDIUM"

    def test_urgent_overrides_high(self):
        """Urgent check comes before high, so urgent should win."""
        result = classify_priority("broken pipe urgent emergency")
        assert result == "URGENT"

    def test_kp7_fan_urgent(self):
        """Actual test message from test_gemini.py."""
        assert classify_priority("KP-7 hostel room 312 fan not working urgent") == "URGENT"


# ──────────────────────────────────────────────
# FULL PIPELINE — classify_complaint()
# ──────────────────────────────────────────────

class TestClassifyComplaint:

    def test_kp7_fan_full_pipeline(self):
        """Exact message from test_gemini.py — should all match."""
        result = classify_complaint("KP-7 hostel room 312 fan not working urgent")
        assert result["category"] == "ELECTRICAL"
        assert result["priority"] == "URGENT"
        assert result["hostel_name"] == "KP-7"
        assert result["room_number"] == "312"

    def test_wifi_urgent_kaveri(self):
        result = classify_complaint("WiFi not working in Kaveri Hostel Room 305 urgent")
        assert result["category"] == "WIFI"
        assert result["priority"] == "URGENT"
        assert result["room_number"] == "305"

    def test_plumbing_block_a(self):
        result = classify_complaint("Bathroom tap leaking in Block A Room 204")
        assert result["category"] == "PLUMBING"
        assert result["hostel_name"] == "BLOCKA"
        assert result["room_number"] == "204"

    def test_security_complaint(self):
        result = classify_complaint("There is a stranger in corridor at night")
        assert result["category"] == "SECURITY"

    def test_result_has_all_required_keys(self):
        result = classify_complaint("Test complaint message")
        for key in ["hostel_name", "room_number", "category", "priority",
                    "summary", "department_email", "confidence"]:
            assert key in result

    def test_summary_max_100_chars(self):
        long_msg = "a" * 200
        result = classify_complaint(long_msg)
        assert len(result["summary"]) <= 100

    def test_department_email_is_valid_email(self):
        result = classify_complaint("Fan not working in room 204")
        assert "@" in result["department_email"]

    def test_confidence_is_85(self):
        result = classify_complaint("WiFi not working")
        assert result["confidence"] == 85.0

    def test_image_url_does_not_crash(self):
        """image_url is reserved for v1.1 — should be silently ignored."""
        result = classify_complaint("Pipe leaking", image_url="https://example.com/img.jpg")
        assert result["category"] is not None

    def test_all_categories_have_department_email(self):
        """Every category in CATEGORY_KEYWORDS must map to a department email."""
        for category in CATEGORY_KEYWORDS:
            assert category in DEPARTMENT_EMAILS
            assert "@" in DEPARTMENT_EMAILS[category]
