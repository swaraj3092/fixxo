"""
AI Complaint Classifier Module

Classifies hostel maintenance complaints using keyword-based NLP.
Extracts structured data from free-form WhatsApp messages including:
  - Complaint category (PLUMBING, ELECTRICAL, WIFI, etc.)
  - Priority level (URGENT, HIGH, MEDIUM)
  - Hostel/block name (supports KP-7, Block A, Kaveri Hostel, etc.)
  - Room number (supports "room 312", "rm 204", "#101" formats)

This is v1.0 — rule-based classifier. No external API required.
v1.1 will add LLM-based classification for higher accuracy on
ambiguous or multi-issue complaints.

Author: Team Smart Hostel
Version: 1.0.0
License: Apache 2.0
"""

import re

# Maps each complaint category to its responsible department email.
# Replace these with real department emails before production deployment.
DEPARTMENT_EMAILS = {
    "PLUMBING": "swarajbehera923@gmail.com",
    "ELECTRICAL": "swarajbehera923@gmail.com",
    "CLEANLINESS": "swarajbehera923@gmail.com",
    "SECURITY": "swarajbehera923@gmail.com",
    "WIFI": "swarajbehera923@gmail.com",
    "FOOD": "swarajbehera923@gmail.com",
    "FURNITURE": "swarajbehera923@gmail.com",
    "OTHER": "swarajbehera923@gmail.com"
}

# Keyword lists per category. Each matching keyword scores 1 point.
# The category with the highest score wins.
CATEGORY_KEYWORDS = {
    "PLUMBING": [
        "tap", "water", "leak", "pipe", "flush", "toilet",
        "bathroom", "shower", "drain", "plumb"
    ],
    "ELECTRICAL": [
        "light", "electricity", "power", "bulb", "switch",
        "fan", "ac", "socket"
    ],
    "CLEANLINESS": [
        "clean", "dirty", "garbage", "trash", "smell",
        "hygiene", "pest", "insect", "rodent"
    ],
    "SECURITY": [
        "security", "lock", "key", "door", "stranger", "theft",
        "safety", "cctv", "guard", "intruder", "break-in"
    ],
    "WIFI": [
        "wifi", "internet", "network", "connection", "slow",
        "disconnect", "signal", "router", "bandwidth", "latency",
        "data", "speed", "access", "coverage", "outage",
        "login", "password", "portal"
    ],
    "FOOD": [
        "food", "mess", "meal", "quality", "taste", "hygiene",
        "menu", "cooking", "vegetarian", "non-vegetarian",
        "snack", "breakfast", "lunch", "dinner", "bottle", "canteen"
    ],
    "FURNITURE": [
        "bed", "chair", "table", "furniture", "sofa", "desk",
        "cupboard", "drawer", "shelf", "couch", "furnishings",
        "fixture", "mattress", "wardrobe", "fitting", "cabinet",
        "stool", "bench", "dining", "furnishing", "upholstery"
    ]
}


def extract_hostel_name(text):
    """
    Extract hostel or block name from common formats used in
    university hostel systems.

    Supported formats:
        - KP-7, KP7, KP 7         (KIIT Patliputra style)
        - Block A, Block C         (block + letter)
        - C Block, A Block         (letter + block)
        - Kaveri Hostel            (name + hostel)
        - Hostel KP-7              (hostel prefix)

    Args:
        text (str): Raw WhatsApp complaint message from the student.

    Returns:
        str or None: Hostel identifier in uppercase with spaces removed
                     (e.g. "KP-7", "BLOCKA", "KAVERIHOSTEL"),
                     or None if no hostel name is found.

    Examples:
        >>> extract_hostel_name("KP-7 hostel room 312 fan not working")
        'KP-7'
        >>> extract_hostel_name("WiFi down in Block A Room 204")
        'BLOCKA'
        >>> extract_hostel_name("The tap is leaking in my room")
        None
    """
    text_lower = text.lower()

    patterns = [
        r"\b(kp[\s\-]?\d+)\b",        # KP-7, KP7, kp 7
        r"\b(block[\s\-]?[a-z])\b",   # Block A, block c
        r"\b([a-z][\s\-]?block)\b",   # C Block, A Block
        r"\b([a-z]+\s+hostel)\b",     # Kaveri Hostel, Ganga Hostel
        r"\bhostel[\s\-]?([a-z0-9\-]+)\b"  # Hostel KP-7, hostel kp7
    ]

    for pattern in patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            hostel = match.group(1).upper().replace(" ", "")
            return hostel

    return None


def extract_room_number(text):
    """
    Extract room number from a variety of formats used in complaints.

    Supported formats:
        - "room 312"       (room keyword + number)
        - "rm 101"         (rm shorthand)
        - "room no 204"    (room no prefix)
        - "#312"           (hash prefix)
        - "312"            (standalone 3-4 digit number, fallback)

    Args:
        text (str): Raw WhatsApp complaint message.

    Returns:
        str or None: Room number as string (e.g. "312"), or None if not found.

    Examples:
        >>> extract_room_number("Tap leaking in Room 204")
        '204'
        >>> extract_room_number("Issue in #101")
        '101'
        >>> extract_room_number("rm 312 fan broken")
        '312'
        >>> extract_room_number("WiFi is down in hostel")
        None
    """
    text_lower = text.lower()

    patterns = [
        r"\broom[\s\-]?(?:no[\s\-]?)?(\d{2,4})\b",  # room 312 / room no 204
        r"\brm[\s\-]?(\d{2,4})\b",                   # rm 312
        r"#(\d{2,4})",                                # #312
        r"\b(\d{3,4})\b"                              # fallback standalone number
    ]

    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return match.group(1)

    return None


def classify_category(text):
    """
    Classify the complaint into one of 8 maintenance categories.

    Uses keyword scoring — each matching keyword adds 1 point to that
    category's score. The category with the most matches is returned.
    Falls back to "OTHER" when no keywords match.

    Args:
        text (str): Complaint message text (any case).

    Returns:
        str: Category name — one of:
             PLUMBING, ELECTRICAL, CLEANLINESS, SECURITY,
             WIFI, FOOD, FURNITURE, OTHER

    Examples:
        >>> classify_category("The bathroom tap is leaking badly")
        'PLUMBING'
        >>> classify_category("WiFi is very slow, cannot connect to internet")
        'WIFI'
    """
    t = text.lower()
    scores = {c: sum(1 for k in kws if k in t) for c, kws in CATEGORY_KEYWORDS.items()}
    return max(scores, key=scores.get) if any(scores.values()) else "OTHER"


def classify_priority(text):
    """
    Determine the urgency/priority level of a complaint.

    Checks in this fixed order:
        1. URGENT — if "urgent" or "emergency" is present
        2. HIGH   — if "not working" or "broken" is present
        3. MEDIUM — default for everything else

    Args:
        text (str): Complaint message text.

    Returns:
        str: Priority level — URGENT, HIGH, or MEDIUM.

    Examples:
        >>> classify_priority("No water since morning urgent")
        'URGENT'
        >>> classify_priority("Fan is broken in room 204")
        'HIGH'
        >>> classify_priority("WiFi is a bit slow today")
        'MEDIUM'
    """
    t = text.lower()
    if any(k in t for k in ["urgent", "emergency"]):
        return "URGENT"
    if any(k in t for k in ["not working", "broken"]):
        return "HIGH"
    return "MEDIUM"


def classify_complaint(message_text, image_url=None):
    """
    Main entry point — classifies a student complaint into structured data.

    Combines all extraction and classification helpers into one result
    dictionary that is ready to be saved to the database.

    Args:
        message_text (str): The WhatsApp complaint message from the student.
        image_url (str, optional): URL of an attached photo.
                                   Reserved for v1.1 image analysis feature.

    Returns:
        dict: Structured complaint data with keys:
            - hostel_name (str or None): Extracted hostel/block identifier
            - room_number (str or None): Extracted room number
            - category (str): Complaint category
            - priority (str): URGENT / HIGH / MEDIUM
            - summary (str): First 100 chars of the original message
            - department_email (str): Email of the responsible department
            - confidence (float): Classification confidence (85.0 for v1.0)

    Examples:
        >>> result = classify_complaint("KP-7 hostel room 312 fan not working urgent")
        >>> result['category']
        'ELECTRICAL'
        >>> result['priority']
        'URGENT'
        >>> result['hostel_name']
        'KP-7'
        >>> result['room_number']
        '312'
    """
    category = classify_category(message_text)

    return {
        "hostel_name": extract_hostel_name(message_text),
        "room_number": extract_room_number(message_text),
        "category": category,
        "priority": classify_priority(message_text),
        "summary": message_text[:100],
        "department_email": DEPARTMENT_EMAILS.get(category, DEPARTMENT_EMAILS["OTHER"]),
        "confidence": 85.0
    }


# Manual test — run directly: python src/ai_classifier_simple.py
if __name__ == "__main__":
    test_messages = [
        "KP-7 hostel room 312 fan not working urgent",
        "WiFi not working in Kaveri Hostel Room 305 urgent",
        "Bathroom tap leaking in Block A Room 204",
        "There is a stranger in corridor at night",
        "The mess food quality is very bad today",
        "Room #101 has garbage piled up for 3 days"
    ]

    print("\n🧪 Running manual classifier test:\n")
    for msg in test_messages:
        result = classify_complaint(msg)
        print(f"Message : {msg}")
        print(f"Category: {result['category']} | Priority: {result['priority']} "
              f"| Hostel: {result['hostel_name']} | Room: {result['room_number']}")
        print()
