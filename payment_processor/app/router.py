import json

from aiokafka import AIOKafkaConsumer
from fastapi import APIRouter

from .config import loop, KAFKA_BOOTSTRAP_SERVERS, KAFKA_CONSUMER_GROUP, KAFKA_TOPIC, log
from .payment_utils import process_claim

route = APIRouter()


async def consume():
    """
    A function to consume a message from kafka. The value of the message is then passed down to process_claim to
    process a payment from the claim.
    :return: None
    """
    consumer = AIOKafkaConsumer(KAFKA_TOPIC, loop=loop,
                                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, group_id=KAFKA_CONSUMER_GROUP)
    await consumer.start()
    try:
        async for msg in consumer:
            log.info(f'Consumer msg: {msg}')
            process_claim(json.loads(msg.value))

    finally:
        await consumer.stop()
