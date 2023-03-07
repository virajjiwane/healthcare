from sqlalchemy import Column, Integer
from .database import Base

class Claim(Base):
    __tablename__ = 'claims'
    claim_id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer)