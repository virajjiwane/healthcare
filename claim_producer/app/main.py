import asyncio

import pandas as pd
import simplejson
from fastapi import FastAPI

from .config import log
from .producers import produce_message
from .router import route

app = FastAPI()

app.include_router(route)

claims = pd.read_csv('claim_fees_1234.csv').to_dict('index')


@app.on_event("startup")
async def produce_claims():
    await asyncio.sleep(15)
    for index, claim in claims.items():
        log.info(f"{'#' * 5} PRODUCING A CLAIM {'#' * 5}")
        claim_str = simplejson.dumps(claim, ignore_nan=True)
        log.info(f"CLAIM: {claim_str}")
        await produce_message(claim)

        log.info(f"{'#' * 5} PRODUCED A CLAIM {'#' * 5}")


@app.post('/trigger-claims')
async def trigger_claims():
    await produce_claims()
