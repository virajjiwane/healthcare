from fastapi import Depends
from sqlalchemy.orm import Session

from .config import log
from .database import engine
from .models import Claim
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
        claim_dict['service_date'] = parse(claim_dict['service_date'])
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
    # pass

def generate_payment_record_id() -> str:
    pass

def calculate_total_payment(claim: Claim) -> float:
    pass


def insert_payment_record(payment):
    pass

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
    total_payment = calculate_total_payment(claim)
    insert_payment_record(None)
    generate_payment_record_line(Claim())
    write_payment_record_line_to_nacha_file('',Claim())
    log.info(f"{'*'*20}  PROCESSED CLAIM | raw_claim={raw_claim} {'*'*20} ")



