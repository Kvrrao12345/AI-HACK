import re

EMAIL_PATTERN = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

PHONE_PATTERN = r"\+?\d[\d\s().-]{7,}\d"


def extract_emails(text):
    emails = re.findall(EMAIL_PATTERN, text)
    return list(set(emails))


def extract_phones(text):
    phones = re.findall(PHONE_PATTERN, text)
    return list(set(phones))