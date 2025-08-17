import os, time, requests, hashlib, logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from stem import Signal
from stem.control import Controller

load_dotenv()

# === Config ===
SEEDS = os.path.join(os.path.dirname(__file__), 'seeds_onion.txt')
TOR_SOCKS = "socks5h://127.0.0.1:9050"
LOGFILE = os.path.join(os.getcwd(), 'crawler_tor.log')
USER_AGENT = os.getenv('USER_AGENT', 'DarkWebIntelBot/1.0 (+research)')
RATE = float(os.getenv('RATE_LIMIT_SECONDS', '10'))

logging.basicConfig(filename=LOGFILE, level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

def rotate_tor_identity():
    """Attempt to request new Tor circuit, skip if control port closed."""
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
            logging.info("Tor NEWNYM requested.")
            time.sleep(3)
    except Exception as e:
        logging.warning(f"Tor rotate identity failed (non-critical): {e}")

def load_seeds(path=SEEDS):
    """Load onion addresses from seeds file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Seeds file not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return [
            l.strip() for l in f
            if l.strip() and not l.strip().startswith('#')
        ]

def fetch_via_tor(url, timeout=60):
    """Fetch HTML via Tor SOCKS proxy."""
    try:
        session = requests.Session()
        session.headers.update({'User-Agent': USER_AGENT})
        session.proxies = {'http': TOR_SOCKS, 'https': TOR_SOCKS}
        r = session.get(url, timeout=timeout)
        r.raise_for_status()
        ctype = r.headers.get('Content-Type', '').lower()
        if any(x in ctype for x in [
            'application/octet-stream','application/zip',
            'application/pdf','application/x-']):
            logging.warning(f"Skipping binary content at {url} ({ctype})")
            return None, {'content-type': ctype}
        return r.text, {'content-type': ctype}
    except Exception as e:
        logging.error(f"Fetch failed for {url}: {e}")
        return None, {}

def extract_text(html):
    if not html:
        return ''
    soup = BeautifulSoup(html, 'html.parser')
    for s in soup(['script','style','noscript','iframe']):
        s.decompose()
    return soup.get_text(separator=' ', strip=True)

def sha256_hex(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def crawl_once():
    seeds = load_seeds()
    for s in seeds:
        if not s.endswith('.onion'):
            logging.info(f"Skipping non-onion: {s}")
            continue
        logging.info(f"Fetching via Tor: {s}")
        html, headers = fetch_via_tor(s)
        if not html:
            logging.info(f"No content saved for {s}")
            continue

        text = extract_text(html)
        title = ''
        try:
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.title.string.strip() if soup.title and soup.title.string else ''
        except:
            pass

        h = sha256_hex(text)
        logging.info(f"[HASH] {s} -> {h}")
        logging.info(f"[TITLE] {title}")
        logging.info(f"[TEXT_SNIPPET] {text[:200]}")

        time.sleep(RATE)

def main():
    logging.info("=== Starting Tor crawler ===")
    rotate_tor_identity()
    crawl_once()
    logging.info("=== Crawl finished ===")

if __name__ == '__main__':
    main()
