import json
import aio_pika
from app.core.rabbitmq import get_channel

async def publish_user_created(user: dict):
    channel = await get_channel()

    message = aio_pika.Message(
        body=json.dumps(user).encode()
    )

    await channel.default_exchange.publish(
        message,
        routing_key="user.created"
    )