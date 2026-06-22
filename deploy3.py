import requests
import hashlib

TOKEN_FILE = "/tmp/.netlify_token"
SITE_ID = "8ba0bfa3-a650-405d-befb-4b819cf5bb73"
BASE = "https://api.netlify.com/api/v1"
FILES_DIR = "/home/ubuntu/wedding-site"
FILE_LIST = ["index.html", "bethsaida.jpg"]

def main():
    with open(TOKEN_FILE) as f:
        token = f.read().strip()
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Build file hashes
    files_dict = {}
    contents = {}
    for fname in FILE_LIST:
        path = f"{FILES_DIR}/{fname}"
        with open(path, "rb") as f:
            content = f.read()
        contents[fname] = content
        files_dict[f"/{fname}"] = hashlib.sha1(content).hexdigest()
    
    # Create deploy
    r = requests.post(f"{BASE}/sites/{SITE_ID}/deploys", headers=headers, json={"files": files_dict})
    print(f"Create deploy: {r.status_code}")
    data = r.json()
    deploy_id = data.get("id")
    required = data.get("required", [])
    print(f"Deploy ID: {deploy_id}")
    print(f"Need to upload: {required}")
    
    if not deploy_id:
        print(f"Error: {data}")
        return
    
    # Upload each file
    for fname in FILE_LIST:
        with open(f"{FILES_DIR}/{fname}", "rb") as f:
            r = requests.put(
                f"{BASE}/deploys/{deploy_id}/files/{fname}",
                headers={**headers, "Content-Type": "application/octet-stream"},
                data=f
            )
            print(f"  {fname}: {r.status_code} - {r.text[:100] if r.status_code != 200 else 'OK'}")
    
    print(f"\nDone! https://carolwedsdaniel.netlify.app")

if __name__ == "__main__":
    main()
