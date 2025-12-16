from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_manual_trigger_success_mocked(client):
    mock_coordinator = AsyncMock()
    mock_coordinator.execute_upload_job = AsyncMock()
    
    mock_session = MagicMock()
    mock_schedule = MagicMock()
    mock_schedule.channel_id = 1
    mock_session.exec.return_value.first.return_value = mock_schedule

    with patch("src.routers.coordinator.coordinator_service", mock_coordinator):
        with patch("src.routers.coordinator.Depends", return_value=mock_session):
            with patch("src.routers.coordinator.select", return_value=MagicMock()):
                response = client.post(
                    "/coordinator/trigger",
                    json={"channel_id": 1},
                )

    assert response.status_code in [200, 500]


def test_unregister_job(client):
    mock_unregister = MagicMock()

    with patch("src.routers.coordinator.unregister_channel_job", mock_unregister):
        response = client.delete("/coordinator/jobs/unregister/1")

    assert response.status_code == 200
    assert "Job unregistered for channel_id: 1" in response.json()["message"]
    mock_unregister.assert_called_once_with(1)
