import pytest
from httpx import AsyncClient


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    from ..app.main import app
    async with AsyncClient(app=app, base_url="http://0.0.0.0:8000") as client:
        print("Client is ready")
        yield client
