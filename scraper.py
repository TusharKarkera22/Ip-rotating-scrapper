from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient
from selenium.webdriver.common.proxy import Proxy, ProxyType
from datetime import datetime
import time
import uuid
import requests
from config import PROXYMESH_USERNAME, PROXYMESH_PASSWORD, PROXYMESH_HOST, PROXYMESH_PORT, MONGODB_URI, DATABASE_NAME, COLLECTION_NAME, TWITTER_USERNAME, TWITTER_PASSWORD
from urllib.parse import quote

def setup_driver_with_proxy():
    try:
        # Set up the proxy
        PROXY = f"{PROXYMESH_HOST}:{PROXYMESH_PORT}"  # Replace with your ProxyMesh host and port
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f'--proxy-server={PROXY}')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)

        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        # Initialize the Chrome driver with the proxy settings
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.implicitly_wait(10)
        
        # Open a page to verify the IP address
        driver.get("http://whatismyipaddress.com")
        time.sleep(5)  # Wait for the page to load completely
        
        return driver
    except Exception as e:
        print(f"Error setting up driver with proxy: {e}")
        raise

def get_ip_address():
    try:
        proxy = {
            'http': f'http://{PROXYMESH_USERNAME}:{PROXYMESH_PASSWORD}@{PROXYMESH_HOST}:{PROXYMESH_PORT}',
            'https': f'http://{PROXYMESH_USERNAME}:{PROXYMESH_PASSWORD}@{PROXYMESH_HOST}:{PROXYMESH_PORT}'
        }
        response = requests.get('http://ipinfo.io/json', proxies=proxy, timeout=10)
        response.raise_for_status()
        return response.json().get('ip', 'Unknown')
    except requests.RequestException as e:
        print(f"Proxy error: {e}")
        return "Unknown"

def login_to_twitter(driver):
    try:
        driver.get("https://x.com/login")
        time.sleep(3)

        # Enter username
        username_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        username_input.send_keys(TWITTER_USERNAME)
        driver.find_element(By.XPATH, "//span[text()='Next']").click()

        # Enter password
        password_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.send_keys(TWITTER_PASSWORD)
        driver.find_element(By.XPATH, "//span[text()='Log in']").click()

        time.sleep(5)  # Allow the page to load

        if "home" not in driver.current_url.lower():
            raise Exception("Login failed - Please check credentials or 2FA settings")
        else:
            return
    except Exception as e:
        print(f"Login error: {e}")
        driver.save_screenshot("login_error.png")
        raise

def get_trending_topics(driver):
    try:
        # Navigate to Explore page
        driver.get("https://x.com/explore")
        
        # Wait for the trends to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='trend']//span"))
        )
        
        # Fetch trends
        trends_xpath = "//div[@data-testid='trend']//span"
        trends = driver.find_elements(By.XPATH, trends_xpath)
        
        if not trends:
            raise Exception("No trends found on the page.")
        
        return [trend.text for trend in trends[:5]]
    except Exception as e:
        print(f"Error fetching trends: {e}")
        driver.save_screenshot("trends_error.png")
        return ["Error fetching trends"] * 5

def save_to_mongodb(trends, ip_address):
    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    record = {
        "_id": str(uuid.uuid4()),
        "nameoftrend1": trends[0],
        "nameoftrend2": trends[1],
        "nameoftrend3": trends[2],
        "nameoftrend4": trends[3],
        "nameoftrend5": trends[4],
        "timestamp": datetime.now(),
        "ip_address": ip_address
    }
    collection.insert_one(record)
    return record

def scrape_trends():
    driver = None
    try:
        ip_address = get_ip_address()
        driver = setup_driver_with_proxy()
        login_to_twitter(driver)
        trends = get_trending_topics(driver)
        return save_to_mongodb(trends, ip_address)
    except Exception as e:
        print(f"Scraping error: {e}")
        return {
            "_id": str(uuid.uuid4()),
            "nameoftrend1": "Error",
            "nameoftrend2": "Error",
            "nameoftrend3": "Error",
            "nameoftrend4": "Error",
            "nameoftrend5": "Error",
            "timestamp": datetime.now(),
            "ip_address": "Error"
        }
    finally:
        if driver:
            driver.quit()
