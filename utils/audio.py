import requests
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import base64

keys_loc = "../keys"

# Load credentials from your service account file
creds = service_account.Credentials.from_service_account_file(
    f"{keys_loc}/service.json",
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

# Fetch an access token (this is what gcloud auth print-access-token returns)
creds.refresh(Request())
token = creds.token

def get_mp3(cost="so much"):

    url = "https://aiplatform.googleapis.com/v1beta1/projects/wpp-cto-smartprod-sandbox/locations/global/interactions"

    payload = {
      "model": "lyria-3-clip-preview",
      "input": [
        {
          "type": "text",
          "text": f"I build a computer that costs ${cost}"
        }
      ]
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    my_song = data["outputs"][2]["data"]
    
    mp3_bytes = base64.b64decode(my_song)
    return mp3_bytes
