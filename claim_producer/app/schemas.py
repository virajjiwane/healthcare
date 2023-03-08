from pydantic import BaseModel

class Claim(BaseModel):
    claim_id: int
    member_id: int


class Message(BaseModel):
    message : str