from sqlalchemy import Column, Integer, DateTime, String, BigInteger, DECIMAL
from .database import Base


class Claim(Base):
    __tablename__ = 'claims'
    claim_id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer)
    service_date = Column(DateTime)
    submitted_procedure = Column(String)
    quadrant = Column(String)
    plan_group_no = Column(String)
    subscriberno = Column(BigInteger)
    provider_npi = Column(BigInteger)
    provider_fees = Column(DECIMAL)
    allowed_fees = Column(DECIMAL)
    member_coinsurance = Column(DECIMAL)
    member_copay = Column(DECIMAL)
    net_fee = Column(DECIMAL)
    processing_fees = Column(DECIMAL)
