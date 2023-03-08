from fastapi import FastAPI
from .router import route


app = FastAPI()

app.include_router(route)
