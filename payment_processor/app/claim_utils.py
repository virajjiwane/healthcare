import datetime

from fastapi import Depends
from sqlalchemy.orm import Session
import string
import random
from .config import log
from .database import engine
from .models import Claim, Payment
from dateutil.parser import parse
from re import sub
from decimal import Decimal


def clean(uncleaned_dict) -> dict:
    cleaned_dict = {}
    for key, value in uncleaned_dict.items():
        key = key.strip().replace('"', '').replace(' ','_').replace('/','_').replace('#','no').lower()
        if type(value) is str:
            value = value.strip()
        cleaned_dict[key] = value
    return cleaned_dict


def build_claim(claim_dict: dict) -> Claim:
    if claim_dict['service_date']:
        claim_dict['service_date'] = parse(claim_dict['service_date']).date()
    for fees in ['provider_fees', 'allowed_fees', 'member_coinsurance', 'member_copay', 'net_fee', 'processing_fees']:
        if claim_dict[fees]:
            claim_dict[fees] = Decimal(sub(r'[^\d.]', '', claim_dict[fees]))

    return Claim(**claim_dict)


def insert_claim_in_db(claim: Claim) -> Claim:
    with Session(engine) as db:
        db.add(claim)
        db.commit()
        db.refresh(claim)
    return claim

def generate_payment_record_id() -> int:
    with Session(engine) as db:
        while True:
            payment_record_id = int(''.join(random.choices(string.digits, k=16)))
            log.info(f"trying payment_record_id = {payment_record_id}")
            if not db.query(Payment).filter_by(payment_id=payment_record_id).first():
                log.info(f"success payment_record_id = {payment_record_id}")
                return payment_record_id


def calculate_total_payment(claim: Claim) -> Decimal:
    return claim.net_fee + claim.processing_fees


def generate_nacha_file_name(service_date):
    return f"payments_{service_date.strftime('%m_%d_%Y')}.nacha"


def build_payment(claim: Claim, payment_record_id: int, total_payment: Decimal) -> Payment:
    return Payment(
        payment_id=payment_record_id,
        claim_id=claim.claim_id,
        member_id=claim.member_id,
        service_date=claim.service_date,
        payment_amount=total_payment,
        nacha_file_name=generate_nacha_file_name(claim.service_date)
    )


def insert_payment_record(payment) -> Payment:
    with Session(engine) as db:
        db.add(payment)
        db.commit()
        db.refresh(payment)
    return payment

def generate_payment_record_line(claim: Claim) -> str:
    pass

def write_payment_record_line_to_nacha_file(payment_record_line: str, claim: Claim):
    pass


def process_claim(raw_claim: dict):
    log.info(f"{'*'*20}  PROCESSING CLAIM | raw_claim={raw_claim} {'*'*20} ")
    cleaned_claim = clean(raw_claim)
    log.info(f"CLEANED CLAIM | cleaned_claim={cleaned_claim}")
    claim = build_claim(cleaned_claim)
    log.info(f"CLAIM OBJECT | claim={claim}")
    claim = insert_claim_in_db(claim)
    log.info(f"INSERTED OBJECT | claim={claim}")
    payment_record_id = generate_payment_record_id()
    log.info(f"PAYMENT RECORD ID | payment_record_id={payment_record_id}")
    total_payment = calculate_total_payment(claim)
    log.info(f"TOTAL PAYMENT | total_payment={total_payment}")
    payment = build_payment(claim, payment_record_id, total_payment)
    log.info(f"PAYMENT OBJECT | payment={payment}")
    payment = insert_payment_record(payment)
    log.info(f"INSERTED OBJECT | payment={payment}")
    generate_payment_record_line(Claim())
    write_payment_record_line_to_nacha_file('',Claim())
    log.info(f"{'*'*20}  PROCESSED CLAIM | raw_claim={raw_claim} {'*'*20} ")



