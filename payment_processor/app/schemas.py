import datetime

from pydantic import BaseModel


class ReversePayment(BaseModel):
    claim_id: int
    member_id: int
    service_date: datetime.date
