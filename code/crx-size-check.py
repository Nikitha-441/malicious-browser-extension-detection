import os

crx_dir = r"C:\Users\Nikitha\Documents\Projects\malicious browser extension\dataset\crx_files"

have = set(f.replace(".crx","") for f in os.listdir(crx_dir) if f.endswith(".crx"))
print(f"Have: {len(have)}")