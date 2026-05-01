import aio_pika
from app.core.config import settings

connection = None
channel = None

async def connect_rabbitmq():
    global connection, channel

    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()

async def get_channel():
    return channel