import json

from fastapi import FastAPI

from .producers import produce_message
from .router import route
from fastapi_utils.tasks import repeat_every
import pandas as pd
from .config import log
import time
import asyncio

from .schemas import Message

app = FastAPI()

app.include_router(route)

claims = pd.read_csv('claim_fees_1234.csv').to_dict('index')

@app.on_event("startup")
async def produce_claims():
    for index, claim in claims.items():
        log.info(f"{'#'*5} PRODUCING A CLAIM {'#'*5}")
        claim_str = json.dumps(claim)
        log.info(f"CLAIM: {claim_str}")
        await produce_message(claim)

        log.info(f"{'#'*5} PRODUCED A CLAIM {'#'*5}")

        # await asyncio.sleep(1)

