import undetected_chromedriver as uc
import random

USER_AGENTS = [
    # Add several real desktop user agents here
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Add more as needed
]

PROXIES = [
    # Example: 'http://username:password@proxy_ip:proxy_port',
    # 'http://proxy_ip:proxy_port',
    # Add your proxies here
]

def get_random_proxy():
    if PROXIES:
        return random.choice(PROXIES)
    return None

def setup_mobile_driver():
    options = uc.ChromeOptions()
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f"--user-agent={user_agent}")
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    # Set a typical desktop window size
    width = random.randint(1200, 1600)
    height = random.randint(800, 1000)
    options.add_argument(f"--window-size={width},{height}")
    # Proxy support
    proxy = get_random_proxy()
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')
    driver = uc.Chrome(options=options)
    return driver

# Helper for random delays
def random_delay(min_sec=1.2, max_sec=2.7):
    import time
    time.sleep(random.uniform(min_sec, max_sec)) 