import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db import Base, get_db
from app.main import app
from app.models.user import User

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSession = async_sessionmaker(engine, expire_on_commit=False)


async def override_get_db():
    async with TestSession() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestSession() as session:
        session.add(User(id=1, username="demo", email="demo@example.com"))
        await session.commit()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_create_event_type(client):
    response = await client.post(
        "/api/v1/event-types",
        json={
            "title": "Consultation",
            "slug": "consult",
            "length": 30,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Consultation"
    assert data["slug"] == "consult"
    assert data["length"] == 30
    assert data["owner_username"] == "demo"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_event_types(client):
    response = await client.get("/api/v1/event-types")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
