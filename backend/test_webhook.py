import os
import httpx
from dotenv import load_dotenv

load_dotenv()

AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]
CLIENT_ID = os.environ["AUTH0_CLIENT_ID"]
CLIENT_SECRET = os.environ["AUTH0_CLIENT_SECRET"]
AUDIENCE = os.environ.get("AUTH0_AUDIENCE", "")

WEBHOOK_URL = "http://localhost:8000/webhook"

# Step 1: Get a token from Auth0
print("Requesting token from Auth0...")
token_resp = httpx.post(
    f"https://{AUTH0_DOMAIN}/oauth/token",
    json={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "audience": AUDIENCE,
        "grant_type": "client_credentials",
    },
)

if token_resp.status_code != 200:
    print(f"Failed to get token: {token_resp.status_code}")
    print(token_resp.json())
    exit(1)

access_token = token_resp.json()["access_token"]
print(f"Got token: {access_token[:20]}...")

# Step 2: Send webhook data with the token
payload = {
    "event_type": "sow_activity",
    "sow_id": "SOW-001",
    "timestamp": "2026-02-12T10:30:00Z",
    "data": {
        "temperature": 38.5,
        "activity_level": "high",
        "location": "pen-12",
    },
}

print("\nSending test webhook with Auth0 token...")
resp = httpx.post(
    WEBHOOK_URL,
    json=payload,
    headers={"Authorization": f"Bearer {access_token}"},
)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.json()}")
