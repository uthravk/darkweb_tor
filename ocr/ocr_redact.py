# ocr/ocr_redact.py
import pytesseract, re, hashlib
from PIL import Image

EMAIL_RE = re.compile(r'[a-zA-Z0-9.\-+_]+@[a-zA-Z0-9.\-+_]+\.[a-zA-Z]+')
PHONE_RE = re.compile(r'\b\d{7,15}\b')

def ocr_and_redact(image_path):
    text = pytesseract.image_to_string(Image.open(image_path))
    redacted = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    redacted = PHONE_RE.sub("[REDACTED_PHONE]", redacted)
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return {"hash": h, "redacted_text": redacted}
