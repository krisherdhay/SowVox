from sqlalchemy import Column, Integer, String, Float
from database import Base, engine


class SowData(Base):
    __tablename__ = "sow_records"
    id = Column(Integer, primary_key=True, index=True)
    sow_id = Column(String)
    weight_kg = Column(Float)
    feed_intake_g = Column(Float)


Base.metadata.create_all(bind=engine)
