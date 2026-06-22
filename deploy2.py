import requests
import sys

with open("/tmp/.netlify_token") as f:
    TOKEN = f.read().strip()

SITE = "8ba0bfa3-a650-405d-befb-4b819cf5bb73"
headers = {"Authorization": f"Bearer {TOKEN}"}
base = "https://api.netlify.com/api/v1"

# Create deploy
r = requests.post(f"{base}/sites/{SITE}/deploys", headers=headers, json={})
print(f"Deploy status: {r.status_code}")
data = r.json()
deploy_id = data.get("id")
print(f"Deploy ID: {deploy_id}")

if not deploy_id:
    print("Error:", data)
    sys.exit(1)

# Upload files
files_dir = "/home/ubuntu/wedding-site"
for fname in ["index.html", "bethsaida.jpg"]:
    path = f"{files_dir}/{fname}"
    with open(path, "rb") as f:
        r = requests.put(
            f"{base}/deploys/{deploy_id}/files/{fname}",
            headers={**headers, "Content-Type": "application/octet-stream"},
            data=f
        )
        print(f"{fname}: {r.status_code} {r.text[:200]}")

print("\nDone! https://carolwedsdaniel.netlify.app")
