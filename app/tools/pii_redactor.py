import re
from typing import Tuple, List, Dict

# Regex patterns for synthetic identifier formats
AADHAAR_PATTERN = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+91[-.\s]?|[0]?)?[6-9]\d{9}\b")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
NAME_LABEL_PATTERN = re.compile(r"(?i)\b(?:patient(?:\s+name)?|insured(?:\s+name)?|name)\s*:\s*([A-Za-z\s.]+)(?=\n|,|;|\band\b|$)")
ADDRESS_PATTERN = re.compile(r"(?i)\b(?:address|residence)\s*:\s*([^\n,;]+(?:,\s*[^\n,;]+){1,3})")

def redact_pii(text: str) -> Tuple[str, List[str]]:
    """
    Strips direct identifiers from text before cloud transmission.
    Returns:
        redacted_text (str): Safe text with placeholders.
        redacted_types (list): List of unique redacted categories (no raw values).
    """
    redacted_types: List[str] = []
    sanitized = text

    if AADHAAR_PATTERN.search(sanitized):
        sanitized = AADHAAR_PATTERN.sub("[GOVT_ID_REDACTED]", sanitized)
        redacted_types.append("GOVERNMENT_ID")

    if PHONE_PATTERN.search(sanitized):
        sanitized = PHONE_PATTERN.sub("[PHONE_REDACTED]", sanitized)
        redacted_types.append("PHONE_NUMBER")

    if EMAIL_PATTERN.search(sanitized):
        sanitized = EMAIL_PATTERN.sub("[EMAIL_REDACTED]", sanitized)
        redacted_types.append("EMAIL_ADDRESS")

    if NAME_LABEL_PATTERN.search(sanitized):
        sanitized = NAME_LABEL_PATTERN.sub("Patient Name: [NAME_REDACTED]", sanitized)
        redacted_types.append("PATIENT_NAME")

    if ADDRESS_PATTERN.search(sanitized):
        sanitized = ADDRESS_PATTERN.sub("Address: [ADDRESS_REDACTED]", sanitized)
        redacted_types.append("POSTAL_ADDRESS")

    return sanitized, list(set(redacted_types))