import requests
from bs4 import BeautifulSoup
import pandas as pd
import zipfile
import json
import os
import re
import time
import struct

# ----------------------------
# SETTINGS
# ----------------------------

TARGET_EXTENSIONS = 300
CATEGORY_URL = "https://chrome.google.com/webstore/category/extensions"

headers = {
    "User-Agent": "Mozilla/5.0"
}

# ----------------------------
# CRX EXTRACTION FUNCTION
# ----------------------------

def extract_crx(crx_path, extract_to):

    with open(crx_path, 'rb') as f:

        magic = f.read(4)

        if magic != b'Cr24':
            print("Invalid CRX:", crx_path)
            return False

        version = struct.unpack('<I', f.read(4))[0]

        if version == 2:
            pubkey_len = struct.unpack('<I', f.read(4))[0]
            sig_len = struct.unpack('<I', f.read(4))[0]
            f.seek(pubkey_len + sig_len, 1)

        elif version == 3:
            header_len = struct.unpack('<I', f.read(4))[0]
            f.seek(header_len, 1)

        zip_data = f.read()

    zip_path = crx_path.replace(".crx", ".zip")

    with open(zip_path, "wb") as z:
        z.write(zip_data)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        return True

    except:
        return False


# ----------------------------
# STEP 1 — GET EXTENSION IDS
# ----------------------------

print("Collecting extension IDs...")

response = requests.get(CATEGORY_URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

links = soup.find_all("a", href=True)

extension_ids = set()

for link in links:

    href = link["href"]

    if "/detail/" in href:

        match = re.search(r'/detail/.*/([a-z]{32})', href)

        if match:
            extension_ids.add(match.group(1))

extension_ids = list(extension_ids)

print("Found:", len(extension_ids), "extensions")

extension_ids = extension_ids[:TARGET_EXTENSIONS]

# ----------------------------
# CREATE FOLDERS
# ----------------------------

os.makedirs("crx", exist_ok=True)
os.makedirs("extracted", exist_ok=True)

dataset = []

# ----------------------------
# STEP 2 — DOWNLOAD + PROCESS
# ----------------------------

for ext_id in extension_ids:

    print("Processing:", ext_id)

    try:

        url = f"https://clients2.google.com/service/update2/crx?response=redirect&prodversion=49.0&acceptformat=crx2,crx3&x=id%3D{ext_id}%26installsource%3Dondemand%26uc"

        r = requests.get(url)

        crx_path = f"crx/{ext_id}.crx"

        with open(crx_path, "wb") as f:
            f.write(r.content)

        extract_path = f"extracted/{ext_id}"
        os.makedirs(extract_path, exist_ok=True)

        success = extract_crx(crx_path, extract_path)

        if not success:
            continue

        manifest_path = f"{extract_path}/manifest.json"

        if not os.path.exists(manifest_path):
            continue

        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        name = manifest.get("name")
        description = manifest.get("description")
        version = manifest.get("version")

        permissions = manifest.get("permissions", [])
        host_permissions = manifest.get("host_permissions", [])

        dataset.append({

            "extension_id": ext_id,
            "name": name,
            "description": description,
            "version": version,
            "permissions": ", ".join(permissions),
            "host_permissions": ", ".join(host_permissions)

        })

        time.sleep(1)

    except Exception as e:

        print("Error:", e)


# ----------------------------
# SAVE DATASET
# ----------------------------

df = pd.DataFrame(dataset)

df.to_csv("extension_dataset.csv", index=False)

print("Dataset created:", len(df), "extensions")