import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient, ASGITransport

from src.database import Base

from src.main import app
from src.database import get_session

TEST_DB_URL = "postgresql+asyncpg://postgres:1234@localhost/wallets_test"

engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)
TestSession = async_sessionmaker(engine, expire_on_commit=False)

@pytest.fixture
async def prepare_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(prepare_db):
    async def override_get_session():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()