from fastapi import FastAPI, Depends
from . import models, schemas
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
from .router import consume, route
import asyncio

models.Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.post('/create-claim')
def create_claim(request: schemas.Claim, db: Session = Depends(get_db)):
    new_claim = models.Claim(claim_id=request.claim_id,
                             member_id=request.member_id)
    db.add(new_claim)
    db.commit()
    db.refresh(new_claim)
    return new_claim


@app.get('/claims')
def fetch_all_claims(db: Session = Depends(get_db)):
    claims = db.query(models.Claim).all()
    return claims


@app.get('/payment')
def fetch_payment_by_service_date(service_date: str, db: Session = Depends(get_db)):
    pass


@app.delete('/payment')
def reverse_payment(claim_id: int, member_id: int, service_date: str, db: Session = Depends(get_db)):
    pass


app.include_router(route)
asyncio.create_task(consume())
