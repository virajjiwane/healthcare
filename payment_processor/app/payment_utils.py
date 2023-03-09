"""
This module contains the business logic and necessary utils to process payment from claim.
"""

import random
import string
from decimal import Decimal
from re import sub

import portalocker
from dateutil.parser import parse
from sqlalchemy.orm import Session

from .config import log
from .database import engine
from .models import Claim, Payment, Member
from .shared_utils import clean


def build_claim(claim_dict: dict) -> Claim:
    """
    This function constructs a Claim object from the provided dictionary.
    We provide 'service_date' as a datetime string which is them parsed into date object.
    All the fees fields, if a string, is stripped of any special characters and extract just the number part.
    :param claim_dict: claim dict
    :return: Claim
    """
    if claim_dict['service_date']:
        claim_dict['service_date'] = parse(claim_dict['service_date']).date()
    for fees in ['provider_fees', 'allowed_fees', 'member_coinsurance', 'member_copay', 'net_fee', 'processing_fees']:
        if type(claim_dict[fees]) is str:
            claim_dict[fees] = Decimal(sub(r'[^\d.]', '', claim_dict[fees]))

    return Claim(**claim_dict)


def insert_claim_in_db(claim: Claim, db) -> Claim:
    """
    This function simply inserts a claim into claims table
    :param claim: Claim object
    :param db: DB Session
    :return: Claim
    """
    db.add(claim)
    db.flush()
    return claim


def generate_payment_record_id() -> int:
    """
    This function generates a 16 digit unique payment record id
    :return: Payment Record ID as integer
    """
    with Session(engine) as db:
        while True:
            payment_record_id = int(''.join(random.choices(string.digits, k=16)))
            log.info(f"trying payment_record_id = {payment_record_id}")
            if not db.query(Payment).filter_by(payment_id=payment_record_id).first():
                log.info(f"success payment_record_id = {payment_record_id}")
                return payment_record_id


def calculate_total_payment(claim: Claim) -> Decimal:
    """
    This function calculates total payment for a claim.\n
    Formula: net_fee + processing_fee
    :param claim: Claim object
    :return: Total Payment as Decimal
    """
    return claim.net_fee + claim.processing_fees


def generate_nacha_file_name(service_date) -> str:
    """
    This function generates a nacha file name using claim service date.
    :param service_date:
    :return: Nacha File Name
    """
    return f"payments_{service_date.strftime('%m_%d_%Y')}.nacha"


def build_payment(claim: Claim, payment_record_id: int, total_payment: Decimal) -> Payment:
    """
    This function constructs a Payment object
    :param claim:
    :param payment_record_id:
    :param total_payment:
    :return: Payment
    """
    return Payment(
        payment_id=payment_record_id,
        claim_id=claim.claim_id,
        member_id=claim.member_id,
        service_date=claim.service_date,
        payment_amount=total_payment,
        nacha_file_name=generate_nacha_file_name(claim.service_date)
    )


def insert_payment_record(payment: Payment, db: Session) -> Payment:
    """
    This function simply inserts a payment into payments table
    :param payment:
    :param db:
    :return: Payment
    """
    db.add(payment)
    db.flush()
    return payment


def generate_payment_record_line(payment: Payment) -> str:
    """
    This function generates a payment record line using the provided payment and associated member.
    If the member is not found from payment.member_id we are raising an exception.
    :param payment:
    :return: Payment Record Line (str)
    """
    with Session(engine) as db:
        member = db.query(Member).filter_by(member_id=payment.member_id).first()
        if member is None:
            raise Exception(f"member with member_id {payment.member_id} not found")
        return f"{payment.payment_id}\t{member.bank_institution}\t{member.routing_number}\t" \
               f"{member.account_number}\t{int(payment.payment_amount * 100)}"


def write_payment_record_line_to_nacha_file(payment_record_line: str, payment: Payment):
    """
    This function will open or create a nacha file if a file with the filename as payment.nacha_file_name does not
    exist and append the payment record line to the file.\n
    To handle concurrency of I/O on the same file I have used portalocker to get an exclusive lock on the file.
    :param payment_record_line: str
    :param payment: Payment object
    :return: None
    """
    filename = payment.nacha_file_name
    with open(filename, 'a+') as f:
        portalocker.lock(f, portalocker.LockFlags.EXCLUSIVE)
        f.write(payment_record_line + "\n")


def process_claim(raw_claim: dict):
    """
    This is the core business logic to process a payment from claim. The function cleans and inserts a claim into DB.
    Then generates a unique payment record id and calculates total payment from claim. Then creating and inserting
    payment in payments table. At the end the function is writing a payment record line into a nacha file.\n
    To handle exception at any stage I have utilised a try...except block and if an exception is raised I am
    rolling back in the except block.
    :param raw_claim:
    :return: None
    """
    with Session(engine) as db:
        try:
            log.info(f"{'*' * 20}  PROCESSING CLAIM | raw_claim={raw_claim} {'*' * 20} ")
            cleaned_claim = clean(raw_claim)
            log.info(f"CLEANED CLAIM | cleaned_claim={cleaned_claim}")
            claim = build_claim(cleaned_claim)
            log.info(f"CLAIM OBJECT | claim={claim}")
            claim = insert_claim_in_db(claim, db)
            log.info(f"INSERTED OBJECT | claim={claim}")
            payment_record_id = generate_payment_record_id()
            log.info(f"PAYMENT RECORD ID | payment_record_id={payment_record_id}")
            total_payment = calculate_total_payment(claim)
            log.info(f"TOTAL PAYMENT | total_payment={total_payment}")
            payment = build_payment(claim, payment_record_id, total_payment)
            log.info(f"PAYMENT OBJECT | payment={payment}")
            payment = insert_payment_record(payment, db)
            log.info(f"INSERTED OBJECT | payment={payment}")
            payment_record_line = generate_payment_record_line(payment)
            log.info(f"PAYMENT RECORD LINE | payment_record_line={payment_record_line}")
            write_payment_record_line_to_nacha_file(payment_record_line, payment)
            log.info(f"PAYMENT RECORD LINE WRITTEN | payment_record_line={payment_record_line} "
                     f"TO FILE {payment.nacha_file_name}")
            db.commit()
            log.info(f"{'*' * 20}  PROCESSED CLAIM | raw_claim={raw_claim} {'*' * 20} ")
        except Exception as e:
            db.rollback()
            log.exception(f"{'*' * 20}  EXCEPTION PROCESSING CLAIM | raw_claim={raw_claim} {'*' * 20} ")
            log.exception(e)
