import asyncio

import pandas as pd
from fastapi import FastAPI

from .config import log
from .producers import produce_message

app = FastAPI()


claims = pd.read_csv('claim_fees_1234.csv').to_dict('index')


@app.on_event("startup")
async def produce_claims():
    """
    This function will read claim_fees_1234.csv and publish the claims on kafka on app startup.
    Adding an async wait of 15sec to wait till the consumer i.e. payment-processor is ready with members populated
    in its DB
    :return: None
    """
    await asyncio.sleep(15)
    for index, claim in claims.items():
        log.info(f"{'#' * 5} PRODUCING A CLAIM {'#' * 5}")
        log.info(f"CLAIM: {claim}")
        await produce_message(claim)

        log.info(f"{'#' * 5} PRODUCED A CLAIM {'#' * 5}")


@app.post('/trigger-claims', tags=["For Testing Purpose"])
async def trigger_claims():
    """
    This API can be used to manually publish claims. It is not necessary to call this API explicitly as claims will be
    published on startup of the app but created this API for testing purpose.
    :return: HTTPStatusCode 200
    """
    await produce_claims()
