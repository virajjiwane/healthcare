from fastapi import APIRouter

from .claim_utils import process_claim
from .config import loop, KAFKA_BOOTSTRAP_SERVERS, KAFKA_CONSUMER_GROUP, KAFKA_TOPIC, log
from aiokafka import AIOKafkaConsumer
import json

route = APIRouter()


async def consume():
    consumer = AIOKafkaConsumer(KAFKA_TOPIC, loop=loop,
                                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, group_id=KAFKA_CONSUMER_GROUP)
    await consumer.start()
    try:
        async for msg in consumer:
            log.info(f'Consumer msg: {msg}')
            process_claim(json.loads(msg.value))

    finally:
        await consumer.stop()
