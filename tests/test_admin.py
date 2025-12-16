import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.database import get_session
from src.main import app

API_KEY = "change-me-in-production"


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_admin_status_without_auth(client: TestClient):
    response = client.get("/admin/status")
    assert response.status_code == 422


def test_admin_status_with_auth(client: TestClient):
    response = client.get("/admin/status", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert "system_status" in data
    assert "scheduler_running" in data


def test_list_channels(client: TestClient):
    response = client.get("/admin/channels", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_channel(client: TestClient):
    channel_data = {
        "channel_name": "Test Channel",
        "channel_id": "UC_TEST_123",
        "description": "Test description",
        "content_type": "educational",
        "video_length": "short",
        "video_style": "informative",
        "ai_provider": "openai"
    }
    response = client.post(
        "/admin/channels",
        json=channel_data,
        headers={"X-API-Key": API_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["channel_name"] == "Test Channel"
    assert data["channel_id"] == "UC_TEST_123"


def test_list_schedules(client: TestClient):
    response = client.get("/admin/schedules", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_job_history(client: TestClient):
    response = client.get("/admin/jobs/history", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_upcoming_jobs(client: TestClient):
    response = client.get("/admin/jobs/upcoming", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_upload_history(client: TestClient):
    response = client.get("/admin/uploads/history", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_test_ai_generation(client: TestClient):
    response = client.post(
        "/admin/actions/test-ai-generation",
        json={"job_name": "test", "details": "Test AI generation"},
        headers={"X-API-Key": API_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "job_id" in data


def test_admin_dashboard_route(client: TestClient):
    response = client.get("/admin/dashboard")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
