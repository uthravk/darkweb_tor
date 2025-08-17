import requests
import stem.process
from stem import Signal
from stem.control import Controller
from bs4 import BeautifulSoup

TOR_SOCKS_PORT = 9050
TOR_CONTROL_PORT = 9051

def renew_tor_ip():
    with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
        controller.authenticate() # CookieAuth in Tails
        controller.signal(Signal.NEWNYM)

def get_via_tor(url):
    session = requests.Session()
    session.proxies = {
        'http': f'socks5h://127.0.0.1:{TOR_SOCKS_PORT}',
        'https': f'socks5h://127.0.0.1:{TOR_SOCKS_PORT}'
    }
    r = session.get(url, timeout=30)
    return r.text

if __name__ == "__main__":
    print("[*] Renewing Tor identity...")
    renew_tor_ip()

    target = "http://expyuzz4wqqyqhjn.onion" # Example onion site
    print(f"[*] Fetching: {target}")
    html = get_via_tor(target)

    soup = BeautifulSoup(html, "html.parser")
    print("[*] Page title:", soup.title.string if soup.title else "No title found")
