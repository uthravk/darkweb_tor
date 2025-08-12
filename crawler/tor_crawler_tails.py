# crawler/tor_crawler_tails.py
import os, time, requests, hashlib, logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from stem import Signal
from stem.control import Controller

load_dotenv()

INGEST_API = f"http://{os.getenv('INGEST_HOST','127.0.0.1')}:{os.getenv('INGEST_PORT','8000')}/ingest"
MENTOR_APPROVAL_FILE = os.getenv('MENTOR_APPROVAL_FILE', './MENTOR_APPROVAL.txt')
RATE = float(os.getenv('RATE_LIMIT_SECONDS', '10'))
USER_AGENT = os.getenv('USER_AGENT', 'DarkWebIntelBot/1.0 (+research)')
SEEDS = os.path.join(os.path.dirname(__file__), 'seeds_onion.txt')
TOR_SOCKS = "socks5h://127.0.0.1:9050"
LOGFILE = os.path.join(os.getcwd(), 'crawler_tor.log')

logging.basicConfig(filename=LOGFILE, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

def require_approval():
    if not os.path.exists(MENTOR_APPROVAL_FILE):
        raise RuntimeError("MENTOR_APPROVAL.txt missing. Place mentor-signed approval file in repo root to enable Tor crawling.")
    with open(MENTOR_APPROVAL_FILE, 'r') as f:
        content = f.read().strip()
    if not content:
        raise RuntimeError("MENTOR_APPROVAL.txt is empty. It must contain mentor approval text.")

def rotate_tor_identity():
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
            logging.info("Tor NEWNYM requested.")
            time.sleep(3)
    except Exception as e:
        logging.warning(f"Tor rotate identity failed: {e}")

def load_seeds(path=SEEDS):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Seeds file not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip() and not l.strip().startswith('#')]
    return lines

def fetch_via_tor(url, timeout=60):
    session = requests.Session()
    session.headers.update({'User-Agent': USER_AGENT})
    session.proxies = {'http': TOR_SOCKS, 'https': TOR_SOCKS}
    r = session.get(url, timeout=timeout, stream=False)
    r.raise_for_status()
    ctype = r.headers.get('Content-Type','').lower()
    if any(x in ctype for x in ['application/octet-stream','application/zip','application/pdf','application/x-']):
        logging.warning(f"Attachment-like content-type {ctype} at {url} — skipping.")
        return None, {'content-type': ctype}
    return r.text, {'content-type': ctype}

def extract_text(html):
    if not html:
        return ''
    soup = BeautifulSoup(html, 'html.parser')
    for s in soup(['script','style','noscript','iframe']):
        s.decompose()
    return soup.get_text(separator=' ', strip=True)

def sha256_hex(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def ingest_post(source, url, title, text, metadata=None):
    payload = {
        'source': source,
        'url': url,
        'title': title,
        'text': text[:20000],
        'metadata': metadata or {}
    }
    try:
        r = requests.post(INGEST_API, json=payload, timeout=15)
        if r.status_code in (200,201):
            logging.info(f"Ingested {url} -> OK")
            return True
        else:
            logging.error(f"Ingest POST failed {r.status_code} {r.text}")
            return False
    except Exception as e:
        logging.error(f"Ingest POST error for {url}: {e}")
        return False

def crawl_once():
    seeds = load_seeds()
    for s in seeds:
        try:
            if not s.endswith('.onion'):
                logging.info(f"Skipping non-onion seed: {s}")
                continue
            logging.info(f"Fetching (via Tor) {s}")
            html, headers = fetch_via_tor(s)
            if html is None:
                logging.info(f"Skipped saving content for {s} (headers: {headers})")
                continue
            text = extract_text(html)
            title = ''
            try:
                soup = BeautifulSoup(html, 'html.parser')
                title = soup.title.string.strip() if soup.title and soup.title.string else ''
            except Exception:
                title = ''
            h = sha256_hex(text)
            metadata = {'hash': h, 'headers': headers}
            ingest_post('onion-seed', s, title, text, metadata)
        except Exception as e:
            logging.error(f"Error fetching {s}: {e}")
        logging.info(f"Sleeping {RATE}s")
        time.sleep(RATE)

def main():
    logging.info("Starting Tor crawler (approval gated).")
    require_approval()
    try:
        rotate_tor_identity()
    except Exception as e:
        logging.warning(f"Tor rotation check: {e}")
    crawl_once()
    logging.info("Crawl finished.")

if __name__ == '__main__':
    main()
