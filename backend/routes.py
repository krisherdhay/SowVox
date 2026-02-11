import json
from fastapi import APIRouter
from database import IS_RAILWAY, SessionLocal
from models import WebhookEvent

router = APIRouter()


@router.get("/")
def read_root():
    return {
        "message": "SowVox Backend is Active",
        "storage": "Railway Volume" if IS_RAILWAY else "Local",
    }


@router.post("/webhook")
def receive_nedap_data(data: dict):
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
