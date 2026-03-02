import json
import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse

from database import IS_RAILWAY, SessionLocal
from models import WebhookEvent, NedapToken
from auth import verify_token
import nedap_client

router = APIRouter()

NEDAP_API_KEY = os.environ.get("NEDAP_API_KEY", "")
BACKEND_URL = os.environ.get(
    "BACKEND_URL",
    "https://sowvox-production.up.railway.app"
    if IS_RAILWAY
    else "http://localhost:8000",
)


# ── General ──────────────────────────────────────────────


@router.get("/")
def read_root():
    return {
        "message": "SowVox Backend is Active",
        "storage": "Railway Volume" if IS_RAILWAY else "Local",
    }


# ── Nedap OAuth2 ────────────────────────────────────────


@router.get("/auth/connect")
def auth_connect():
    """Redirect the farmer to Nedap's authorization page."""
    if not NEDAP_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Nedap API key not configured",
        )
    redirect_uri = f"{BACKEND_URL}/auth/callback"
    nedap_auth_url = (
        f"https://nedap-bi.com/oauth/authorize"
        f"?client_id={NEDAP_API_KEY}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
    )
    return RedirectResponse(url=nedap_auth_url)


@router.get("/auth/callback")
def auth_callback(code: str = Query(None)):
    """Handle Nedap's redirect with an authorization code."""
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    redirect_uri = f"{BACKEND_URL}/auth/callback"

    try:
        token_data = nedap_client.exchange_code(code, redirect_uri)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to exchange code with Nedap: {e}",
        )

    db = SessionLocal()
    try:
        token = NedapToken(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            expires_at=nedap_client.calculate_expires_at(
                token_data.get("expires_in", 86400)
            ),
        )
        db.add(token)
        db.commit()
    finally:
        db.close()

    return {"status": "connected", "message": "Nedap account linked successfully"}


@router.get("/nedap/status")
def nedap_status():
    """Check if we have a valid Nedap connection."""
    db = SessionLocal()
    try:
        token = db.query(NedapToken).order_by(NedapToken.id.desc()).first()
        if not token:
            return {"connected": False}
        return {
            "connected": True,
            "expires_at": str(token.expires_at),
            "expired": token.expires_at < datetime.utcnow(),
        }
    finally:
        db.close()


@router.get("/nedap/data")
def get_nedap_data(endpoint: str = Query("/v1/animals")):
    """Fetch data from Nedap API. Auto-refreshes token if expired."""
    db = SessionLocal()
    try:
        token = db.query(NedapToken).order_by(NedapToken.id.desc()).first()
        if not token:
            raise HTTPException(
                status_code=400,
                detail="No Nedap connection. Visit /auth/connect first.",
            )

        # Auto-refresh if expired
        if token.expires_at < datetime.utcnow():
            try:
                new_tokens = nedap_client.refresh_access_token(token.refresh_token)
            except Exception as e:
                raise HTTPException(
                    status_code=502,
                    detail=f"Failed to refresh Nedap token: {e}",
                )
            token.access_token = new_tokens["access_token"]
            token.refresh_token = new_tokens["refresh_token"]
            token.expires_at = nedap_client.calculate_expires_at(
                new_tokens.get("expires_in", 86400)
            )
            db.commit()

        # Fetch data from Nedap
        try:
            data = nedap_client.fetch_nedap_data(token.access_token, endpoint)
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"Nedap API request failed: {e}",
            )

        return data
    finally:
        db.close()


# ── Webhook (existing) ──────────────────────────────────


@router.post("/webhook")
def receive_webhook_data(data: dict, _token=Depends(verify_token)):
    db = SessionLocal()
    try:
        event = WebhookEvent(payload=json.dumps(data))
        db.add(event)
        db.commit()
    finally:
        db.close()
    return {"status": "success"}


@router.get("/webhook/events")
def get_events():
    db = SessionLocal()
    try:
        events = db.query(WebhookEvent).order_by(WebhookEvent.id.desc()).all()
        return [
            {
                "id": e.id,
                "payload": json.loads(e.payload),
                "received_at": str(e.received_at),
            }
            for e in events
        ]
    finally:
        db.close()
