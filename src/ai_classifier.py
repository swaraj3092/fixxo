import re

DEPARTMENT_EMAILS = {
    "PLUMBING": "swarajbehera3092@gmail.com",
    "ELECTRICAL": "swarajbehera3092@gmail.com",
    "CLEANLINESS": "swarajbehera3092@gmail.com",
    "SECURITY": "swarajbehera3092@gmail.com",
    "WIFI": "swarajbehera3092@gmail.com",
    "FOOD": "swarajbehera3092@gmail.com",
    "FURNITURE": "swarajbehera3092@gmail.com",
    "OTHER": "swarajbehera3092@gmail.com"
}

CATEGORY_KEYWORDS = {
    "PLUMBING": ["tap", "water", "leak", "pipe", "flush", "toilet", "bathroom", "shower", "drain", "geyser"],
    "ELECTRICAL": ["light", "electricity", "power", "bulb", "switch", "fan", "ac", "socket", "wire"],
    "CLEANLINESS": ["clean", "dirty", "garbage", "trash", "smell", "dust", "sweep"],
    "SECURITY": ["security", "lock", "key", "door", "stranger", "theft", "safety"],
    "WIFI": ["wifi", "internet", "network", "connection", "router"],
    "FOOD": ["food", "mess", "meal", "dinner", "lunch", "quality"],
    "FURNITURE": ["bed", "chair", "table", "furniture", "cupboard", "mattress"]
}

URGENT_KEYWORDS = ["urgent", "emergency", "asap", "no water", "no power", "fire"]
HIGH_KEYWORDS = ["not working", "broken", "major", "serious"]

def extract_hostel_name(text):
    """Extract hostel or block name from text."""
    patterns = [r"(block\s+[a-z])", r"([a-z]+\s+hostel)", r"(hostel\s+[a-z]+)"]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).title()
    return None

def extract_room_number(text):
    """Extract room number from text."""
    patterns = [r"room\s*[#]?\s*(\d{3,4})", r"\b(\d{3,4})\b"]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return match.group(1)
    return None

def classify_category(text):
    """Classify complaint into category based on keywords."""
    text_lower = text.lower()
    scores = {}
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[category] = score
    
    return max(scores, key=scores.get) if scores else "OTHER"

def classify_priority(text):
    """Determine priority level."""
    text_lower = text.lower()
    
    if any(kw in text_lower for kw in URGENT_KEYWORDS):
        return "URGENT"
    if any(kw in text_lower for kw in HIGH_KEYWORDS):
        return "HIGH"
    
    return "MEDIUM"

def classify_complaint(message_text, image_url=None):
    """
    Main classification function.
    
    Args:
        message_text: The complaint message
        image_url: Optional image URL (not used in v1.0)
    
    Returns:
        dict: Classification result with category, priority, etc.
    """
    try:
        hostel_name = extract_hostel_name(message_text)
        room_number = extract_room_number(message_text)
        category = classify_category(message_text)
        priority = classify_priority(message_text)
        department_email = DEPARTMENT_EMAILS.get(category, DEPARTMENT_EMAILS["OTHER"])
        
        result = {
            "hostel_name": hostel_name,
            "room_number": room_number,
            "category": category,
            "priority": priority,
            "summary": message_text[:100],
            "department_email": department_email,
            "confidence": 85.0
        }
        
        print(f"✅ Classification: {category} - {priority}")
        return result
        
    except Exception as e:
        print(f"❌ Classification error: {e}")
        return {
            "hostel_name": None,
            "room_number": None,
            "category": "OTHER",
            "priority": "MEDIUM",
            "summary": message_text[:100],
            "department_email": DEPARTMENT_EMAILS["OTHER"],
            "confidence": 0
        }


# For testing
if __name__ == "__main__":
    test_messages = [
        "WiFi not working in Kaveri Hostel Room 305 urgent",
        "Bathroom tap leaking in Block A Room 204",
        "There is a stranger in corridor at night"
    ]
    
    for msg in test_messages:
        print(f"\nTest: {msg}")
        result = classify_complaint(msg)
        print(f"Result: {result}")