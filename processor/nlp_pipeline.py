# processor/nlp_pipeline.py
import spacy, re
from dotenv import load_dotenv
load_dotenv()

nlp = spacy.load("en_core_web_sm")

WALLET_RE = re.compile(r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b')
KEYWORDS = ["ransomware","ransom","leak","dump","database","exploit","malware"]

def analyze_text(text):
    labels = []
    score = 0.0
    txt = (text or "").lower()
    for k in KEYWORDS:
        if k in txt:
            labels.append(k)
            score += 0.15
    if WALLET_RE.search(text or ""):
        labels.append("wallet")
        score += 0.2
    try:
        doc = nlp(text[:4000])
        orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        if orgs:
            labels.append("victim_org")
            score += 0.2
    except Exception:
        orgs = []
    score = min(score,1.0)
    return score, list(set(labels))
