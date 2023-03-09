import datetime

from dateutil.parser import parse
from fastapi import FastAPI, Depends, HTTPException
from starlette import status

from . import models, schemas
from .config import log
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
import portalocker
from .router import consume, route
import asyncio
import pandas as pd

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


@app.get('/claims')
def fetch_all_claims(db: Session = Depends(get_db)):
    claims = db.query(models.Claim).all()
    return claims


@app.get('/members')
def fetch_all_members(db: Session = Depends(get_db)):
    members = db.query(models.Member).all()
    return members


@app.get('/payment', status_code=status.HTTP_200_OK)
def fetch_payment_by_service_date(service_date: str, db: Session = Depends(get_db)):
    try:
        service_date = parse(service_date).date()
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Bad service_date format")
    payments = db.query(models.Payment).filter_by(service_date=service_date).all()
    if not payments:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Payments not found")
    return payments


@app.delete('/payment', status_code=status.HTTP_204_NO_CONTENT)
def reverse_payment(request: schemas.ReversePayment, db: Session = Depends(get_db)):
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
    log.info(f"{'#'*5} POPULATING MEMBERS {'#'*5}")
    members = pd.read_csv('members_1234.csv').to_dict('index')
    with Session(engine) as db:
        for index, member_dict in members.items():
            member_dict = clean(member_dict)
            log.info(f"MEMBER: {member_dict}")
            member = models.Member(**member_dict)
            db.add(member)
            db.commit()
            db.refresh(member)

    log.info(f"{'#'*5} POPULATING MEMBERS DONE {'#'*5}")
