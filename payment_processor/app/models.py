from sqlalchemy import Column, Integer, String, BigInteger, DECIMAL, Date
from .database import Base


class Claim(Base):
    __tablename__ = 'claims'
    claim_id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer)
    service_date = Column(Date)
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


class Payment(Base):
    __tablename__ = 'payments'
    payment_id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer)
    member_id = Column(Integer)
    service_date = Column(Date)
    payment_amount = Column(DECIMAL)
    nacha_file_name = Column(String)


class Member(Base):
    __tablename__ = 'members'
    member_id = Column(Integer, primary_key=True, index=True)
    bank_institution = Column(String)
    account_number = Column(BigInteger)
    routing_number = Column(BigInteger)
