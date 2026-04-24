import requests
import os
import time

input_file = r"C:\Users\Nikitha\Documents\Projects\malicious browser extension\dataset\sample_ids.txt"
output_dir = r"C:\Users\Nikitha\Documents\Projects\malicious browser extension\dataset\crx_files1"

os.makedirs(output_dir, exist_ok=True)

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
})

with open(input_file) as f:
    ids = f.read().splitlines()

success = 0

for ext_id in ids:
    url = (
        "https://clients2.google.com/service/update2/crx?"
        "response=redirect"
        "&acceptformat=crx2,crx3"
        "&prodversion=122.0.0.0"
        f"&x=id%3D{ext_id}%26installsource%3Dondemand%26uc"
    )

    try:
        r = session.get(url, allow_redirects=True, timeout=15)

        if r.status_code == 200 and r.content[:4] == b'Cr24':
            with open(f"{output_dir}/{ext_id}.crx", "wb") as f:
                f.write(r.content)
            print(f"✅ {ext_id}")
            success += 1
        else:
            print(f"❌ {ext_id}")

    except Exception as e:
        print(f"⚠️ {ext_id} → {e}")

    time.sleep(1.5)

print(f"\n🎯 Downloaded: {success}")