import asyncio

import pandas as pd
import portalocker
from dateutil.parser import parse
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from . import models, schemas
from .config import log
from .database import engine, SessionLocal
from .router import consume, route
from .shared_utils import clean

models.Base.metadata.create_all(engine)

app = FastAPI()

app.include_router(route)
asyncio.create_task(consume())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/claims', status_code=status.HTTP_200_OK, tags=["For Testing Purpose"])
def fetch_all_claims(db: Session = Depends(get_db)):
    """
    This API returns all claims from the DB. It is for testing purpose only
    :param db:
    :return: List<Claim>
    """
    claims = db.query(models.Claim).all()
    return claims


@app.get('/members', status_code=status.HTTP_200_OK, tags=["For Testing Purpose"])
def fetch_all_members(db: Session = Depends(get_db)):
    """
    This API returns all members from the DB. It is for testing purpose only
    :param db:
    :return: List<Member>
    """
    members = db.query(models.Member).all()
    return members


@app.get('/payment', status_code=status.HTTP_200_OK, tags=["Required Functionality"])
def fetch_payment_by_service_date(service_date: str, db: Session = Depends(get_db)):
    """
    An endpoint that allows the user to give a particular service date and then get all the payments that were created
    for that date.
    :param service_date:
    :param db:
    :return: List<Payment>
    """
    try:
        service_date = parse(service_date).date()
    except Exception:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Bad service_date format")
    payments = db.query(models.Payment).filter_by(service_date=service_date).all()
    if not payments:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Payments not found")
    return payments


@app.delete('/payment', status_code=status.HTTP_204_NO_CONTENT, tags=["Required Functionality"])
def reverse_payment(request: schemas.ReversePayment, db: Session = Depends(get_db)):
    """
    An endpoint that allows to reverse a payment using the values claim_id, member_id and service_date,
    the processor will remove the payment record line from the nacha file.\n
    To handle concurrency of I/O on the same file I have used portalocker to get an exclusive lock on the file.
    :param request: ReversePayment
    :param db:
    :return: dictionary
    """
    payments = db.query(models.Payment).filter_by(service_date=request.service_date,
                                                  claim_id=request.claim_id,
                                                  member_id=request.member_id).all()
    if not payments:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Payments not found")

    log.info(f"PAYMENTS TO REVERSE: {payments}")
    for payment in payments:
        log.info(f'REVERSING {payment.payment_id}')
        with open(payment.nacha_file_name, "r") as f:
            lines = f.readlines()
        with open(payment.nacha_file_name, "w") as f:
            log.info(f'LOOKING INTO FILE {payment.nacha_file_name}')
            portalocker.lock(f, portalocker.LockFlags.EXCLUSIVE)
            for line in lines:
                log.info(f'CURRENT LINE {line}')
                payment_record_id = int(line.strip("\n").split("\t")[0])
                log.info(f'payment_record_id={payment_record_id}')
                if payment_record_id != payment.payment_id:
                    log.info(f"THIS LINE IS OK")
                    f.write(line)
                else:
                    log.info(f"FOUND THE LINE TO BE DELETED")

    return {
        "message": "Payment reversed"
    }


@app.on_event("startup")
async def populate_members():
    log.info(f"{'#' * 5} POPULATING MEMBERS {'#' * 5}")
    members = pd.read_csv('members_1234.csv').to_dict('index')
    with Session(engine) as db:
        for index, member_dict in members.items():
            member_dict = clean(member_dict)
            log.info(f"MEMBER: {member_dict}")
            member = models.Member(**member_dict)
            db.add(member)
            db.commit()
            db.refresh(member)

    log.info(f"{'#' * 5} POPULATING MEMBERS DONE {'#' * 5}")
