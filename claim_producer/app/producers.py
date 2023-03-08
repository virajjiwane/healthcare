
from .config import loop, KAFKA_BOOTSTRAP_SERVERS, KAFKA_CONSUMER_GROUP, KAFKA_TOPIC, log
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import json

from .schemas import Message


async def produce_message(message):
    producer = AIOKafkaProducer(
        loop=loop, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    try:
        log.info(f'Sending message with value: {message}')
        value_json = json.dumps(message).encode('utf-8')
        await producer.send_and_wait(topic=KAFKA_TOPIC, value=value_json)
    finally:
        await producer.stop()