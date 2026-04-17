from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import requests
import zipfile
import io
import json
import time

options = Options()
options.add_argument("--headless")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get("https://chromewebstore.google.com/category/extensions")

time.sleep(5)

extension_urls = set()

print("Collecting extension URLs...")

while len(extension_urls) < 50:

    links = driver.find_elements(By.CSS_SELECTOR,"a[href*='/detail/']")

    for link in links:

        url = link.get_attribute("href")

        if url:
            extension_urls.add(url)

        if len(extension_urls) >= 300:
            break

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(3)

print("Collected URLs:", len(extension_urls))

dataset = []

print("Scraping metadata...")

for url in list(extension_urls)[:300]:

    driver.get(url)
    time.sleep(3)

    data = {}

    data["url"] = url

    # extension id
    ext_id = url.split("/")[-1]
    data["extension_id"] = ext_id

    try:
        data["extension_name"] = driver.find_element(By.TAG_NAME,"h1").text
    except:
        data["extension_name"] = None

    try:
        data["description"] = driver.find_element(By.CSS_SELECTOR,"meta[name='description']").get_attribute("content")
    except:
        data["description"] = None

    try:
        data["developer"] = driver.find_element(By.XPATH,"//a[contains(@href,'publisher')]").text
    except:
        data["developer"] = None

    try:
        data["rating"] = driver.find_element(By.CSS_SELECTOR,"div[role='img']").get_attribute("aria-label")
    except:
        data["rating"] = None

    try:
        data["install_count"] = driver.find_element(By.XPATH,"//*[contains(text(),'users')]").text
    except:
        data["install_count"] = None

    try:
        data["reviews"] = driver.find_element(By.XPATH,"//*[contains(text(),'rating')]").text
    except:
        data["reviews"] = None

    # -------- download extension to get permissions --------

    try:

        crx_url = (
            "https://clients2.google.com/service/update2/crx?"
            f"response=redirect&prodversion=114.0&acceptformat=crx2,crx3&x=id%3D{ext_id}%26installsource%3Dondemand%26uc"
        )

        r = requests.get(crx_url)

        zip_start = r.content.find(b"PK")

        zip_data = r.content[zip_start:]

        z = zipfile.ZipFile(io.BytesIO(zip_data))

        manifest = json.loads(z.read("manifest.json"))

        permissions = manifest.get("permissions", [])

        data["permissions"] = ",".join(permissions)

    except:

        data["permissions"] = None

    dataset.append(data)

    print("Scraped:", data["extension_name"])

df = pd.DataFrame(dataset)

df.to_csv("chrome_extensions_dataset.csv", index=False)

print("Dataset saved as chrome_extensions_dataset.csv")

driver.quit()