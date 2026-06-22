#!/bin/bash
cd /home/ubuntu/wedding-site
TOKEN="nfp_...n"  # placeholder - will be set via env
SITE="3d878533-f5e6-47f2-9755-1c4a7e3c75e7"

# Create deploy with both files
deploy=$(curl -s -X POST "https://api.netlify.com/api/v1/sites/$SITE/deploys" \
  -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -d '{}')
deploy_id=$(echo $deploy | jq -r '.id')
echo "Deploy ID: $deploy_id"

# Upload index.html
echo "Uploading index.html..."
curl -s -X PUT "https://api.netlify.com/api/v1/deploys/$deploy_id/files/index.html" \
  -H "Authorization: Bearer *** \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@index.html" | jq -r '.id // .url // "ok"'

# Upload bethsaida.jpg
echo "Uploading bethsaida.jpg..."
curl -s -X PUT "https://api.netlify.com/api/v1/deploys/$deploy_id/files/bethsaida.jpg" \
  -H "Authorization: Bearer *** \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@bethsaida.jpg" | jq -r '.id // .url // "ok"'

echo "Done!"
