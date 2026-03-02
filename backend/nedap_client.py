import os
from datetime import datetime, timedelta

import httpx

NEDAP_API_KEY = os.environ.get("NEDAP_API_KEY", "")
NEDAP_API_SECRET = os.environ.get("NEDAP_API_SECRET", "")
NEDAP_BASE_URL = "https://nedap-bi.com"
NEDAP_API_URL = "https://api.nedap-bi.com"


def exchange_code(code: str, redirect_uri: str) -> dict:
    """Exchange authorization code for access + refresh tokens."""
    response = httpx.post(
        f"{NEDAP_BASE_URL}/oauth/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": NEDAP_API_KEY,
            "client_secret": NEDAP_API_SECRET,
        },
    )
    response.raise_for_status()
    return response.json()


def refresh_access_token(refresh_token: str) -> dict:
    """Use a single-use refresh token to get new access + refresh tokens."""
    response = httpx.post(
        f"{NEDAP_BASE_URL}/oauth/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": NEDAP_API_KEY,
            "client_secret": NEDAP_API_SECRET,
        },
    )
    response.raise_for_status()
    return response.json()


def calculate_expires_at(expires_in: int) -> datetime:
    """Convert expires_in seconds to an absolute datetime."""
    return datetime.utcnow() + timedelta(seconds=expires_in)


def fetch_nedap_data(access_token: str, endpoint: str) -> dict:
    """Make an authenticated GET request to a Nedap API endpoint."""
    response = httpx.get(
        f"{NEDAP_API_URL}{endpoint}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response.raise_for_status()
    return response.json()
