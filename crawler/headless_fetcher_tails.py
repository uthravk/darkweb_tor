# crawler/headless_fetcher_tails.py
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time, logging

logging.basicConfig(level=logging.INFO)

def get_tor_firefox_driver(socks_host='127.0.0.1', socks_port=9050):
    opts = Options()
    opts.headless = True
    profile = webdriver.FirefoxProfile()
    profile.set_preference("network.proxy.type", 1)
    profile.set_preference("network.proxy.socks", socks_host)
    profile.set_preference("network.proxy.socks_port", socks_port)
    profile.set_preference("network.proxy.socks_remote_dns", True)
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.dir", "/tmp")
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream,application/zip,application/pdf")
    profile.set_preference("pdfjs.disabled", True)
    profile.set_preference("privacy.firstparty.isolate", True)
    profile.update_preferences()
    caps = webdriver.DesiredCapabilities().FIREFOX
    return webdriver.Firefox(firefox_profile=profile, options=opts, desired_capabilities=caps)

def render_via_tor(url, wait=3):
    driver = get_tor_firefox_driver()
    try:
        logging.info(f"Rendering {url} via Tor headless Firefox.")
        driver.set_page_load_timeout(60)
        driver.get(url)
        time.sleep(wait)
        return driver.page_source
    finally:
        driver.quit()
