import xml.etree.ElementTree as ET

# === FILE PATH ===
xml_file = r"C:\Users\Nikitha\Documents\Projects\malicious browser extension\dataset\cws_sitemap_shard_0.xml"

# === PARSE XML ===
tree = ET.parse(xml_file)
root = tree.getroot()

ids = []

# Loop through all <loc> tags
for elem in root.iter():
    if "loc" in elem.tag:
        url = elem.text
        
        if url and "/detail/" in url:
            ext_id = url.split("/")[-1]
            
            # Ensure it's valid (32 characters)
            if len(ext_id) == 32:
                ids.append(ext_id)

# Remove duplicates (important)
ids = list(set(ids))

# Save to file
with open("extension_ids.txt", "w") as f:
    for i in ids:
        f.write(i + "\n")

print(f"✅ Extracted {len(ids)} extension IDs")