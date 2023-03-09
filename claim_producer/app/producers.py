import json

from aiokafka import AIOKafkaProducer

from .config import loop, KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, log


async def produce_message(message: dict):
    """
    A function to publish message on kafka
    :param message: Message dictionary
    :return: None
    """
    producer = AIOKafkaProducer(
        loop=loop, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    try:
        log.info(f'Sending message with value: {message}')
        value_json = json.dumps(message).encode('utf-8')
        await producer.send_and_wait(topic=KAFKA_TOPIC, value=value_json)
    finally:
        await producer.stop()
