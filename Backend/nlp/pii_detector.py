import re

# Regex patterns for common PII
PII_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'\b(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?){1,2}\d{4}\b',
    'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
    'aadhaar': r'\b\d{4}\s\d{4}\s\d{4}\b'
}

def detect_pii_regex(text):
    
    matches = []
    for label, pattern in PII_PATTERNS.items():
        found = re.findall(pattern, text)
        matches.extend(found)
    return matches
