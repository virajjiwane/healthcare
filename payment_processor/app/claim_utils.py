from payment_processor.app.models import Claim


def clean(uncleaned_dict) -> dict:
    pass

def build_claim(claim_dict: dict) -> Claim:
    pass


def insert_claim_in_db(claim: Claim) -> Claim:
    pass

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
    cleaned_claim = clean(raw_claim)
    claim = build_claim(cleaned_claim)
    insert_claim_in_db(claim)
    payment_record_id = generate_payment_record_id()
    total_payment = calculate_total_payment(claim)
    insert_payment_record()
    generate_payment_record_line()
    write_payment_record_line_to_nacha_file()



