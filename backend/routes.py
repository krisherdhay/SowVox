from fastapi import APIRouter
from database import IS_RAILWAY

router = APIRouter()


@router.get("/")
def read_root():
    return {
        "message": "SowVox Backend is Active",
        "storage": "Railway Volume" if IS_RAILWAY else "Local",
    }


@router.post("/webhook")
def receive_nedap_data(data: dict):
    print(f"Received data: {data}")
    return {"status": "success"}
