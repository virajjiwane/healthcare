import asyncio
import os

# env Variable
# KAFKA_HOST: str = os.getenv("KAFKA_HOST")
# KAFKA_PORT: str = os.getenv("KAFKA_PORT")
# KAFKA_BOOTSTRAP_SERVERS= os.getenv("KAFKA_BOOTSTRAP_SERVERS")
KAFKA_BOOTSTRAP_SERVERS="localhost:9093"
print(f"FAST API KAFKA SETTINGS: {KAFKA_BOOTSTRAP_SERVERS}")
KAFKA_TOPIC="claim"
KAFKA_CONSUMER_GROUP="group-id"
loop = asyncio.get_event_loop()
