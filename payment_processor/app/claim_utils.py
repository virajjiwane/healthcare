import datetime
from fastapi import Depends
from sqlalchemy.orm import Session
import string
import random
from .config import log
from .database import engine
from .models import Claim, Payment, Member
from dateutil.parser import parse
from re import sub
from decimal import Decimal

from .shared_utils import clean


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


def generate_payment_record_line(payment: Payment) -> str:
    with Session(engine) as db:
        member = db.query(Member).filter_by(member_id=payment.member_id).first()
        if member is None:
            raise Exception(f"member with member_id {payment.member_id} not found")
        return f"{payment.payment_id}\t{member.bank_institution}\t{member.routing_number}\t{member.account_number}\t{int(payment.payment_amount * 100)}"


def write_payment_record_line_to_nacha_file(payment_record_line: str, payment: Payment):
    filename = payment.nacha_file_name
    with open(filename, 'a+') as f:
        f.write(payment_record_line+"\n")


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
    payment_record_line = generate_payment_record_line(payment)
    log.info(f"PAYMENT RECORD LINE | payment_record_line={payment_record_line}")
    write_payment_record_line_to_nacha_file(payment_record_line, payment)
    log.info(f"PAYMENT RECORD LINE WRITTEN | payment_record_line={payment_record_line} TO FILE {payment.nacha_file_name}")
    log.info(f"{'*'*20}  PROCESSED CLAIM | raw_claim={raw_claim} {'*'*20} ")



