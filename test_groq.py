import os
os.environ["GROQ_API_KEY"] = "your_groq_api_key_here"  # paste your key

from ai_classifier import classify_complaint

# Test 1 - Electrical
result = classify_complaint("fan is not working since 2 days urgent")
print("Test 1:", result)

# Test 2 - Plumbing
result = classify_complaint("water is leaking from the bathroom tap")
print("Test 2:", result)

# Test 3 - Wifi
result = classify_complaint("internet is very slow cant attend online class")
print("Test 3:", result)