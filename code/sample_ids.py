import random

# correct relative path
with open("dataset\extension_ids.txt") as f:
    ids = f.read().splitlines()

print(f"Total IDs: {len(ids)}")

# shuffle
random.shuffle(ids)

# take 300
sample_ids = ids[:700]

# save ALSO into dataset folder (important)
with open("dataset\sample_ids.txt", "w") as f:
    for i in sample_ids:
        f.write(i + "\n")

print("✅ Created sample_ids.txt with 700 IDs")