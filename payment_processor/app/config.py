import asyncio
import os
import logging
log = logging.getLogger("uvicorn")

# env Variable
KAFKA_HOST: str = os.getenv("KAFKA_HOST")
KAFKA_PORT: str = os.getenv("KAFKA_PORT")
KAFKA_BOOTSTRAP_SERVERS=f"{KAFKA_HOST}:{KAFKA_PORT}"
KAFKA_TOPIC: str = os.getenv("KAFKA_TOPIC")
KAFKA_CONSUMER_GROUP="group-id"
loop = asyncio.get_event_loop()
