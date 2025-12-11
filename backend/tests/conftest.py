import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.db.client import db_client
from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient

# Override settings for testing if needed
# settings.MONGO_URI = "mongodb://admin:password@localhost:27017"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="module")
async def test_db():
    # Setup
    db_client.connect()
    yield db_client
    # Teardown
    db_client.close()
