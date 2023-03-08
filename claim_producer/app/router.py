from fastapi import APIRouter

from .producers import produce_message
from .schemas import Message

route = APIRouter()


@route.post('/create_message')
async def send(message: Message):
    await produce_message(message)
