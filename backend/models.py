import json
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base, engine


class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    id = Column(Integer, primary_key=True, index=True)
    payload = Column(String)
    received_at = Column(DateTime, server_default=func.now())

    def payload_json(self):
        return json.loads(self.payload)


Base.metadata.create_all(bind=engine)
