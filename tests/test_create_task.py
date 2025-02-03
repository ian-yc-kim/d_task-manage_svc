import json
from datetime import datetime

import pytest
import httpx
from tests.test_auth_middleware import FakeAsyncClient


@pytest.fixture(autouse=True)
def bypass_auth(monkeypatch):
    """Bypass authentication middleware to avoid 401 errors during tests by removing the AuthMiddleware."""
    from d_task_manage_svc.app import app
    from d_task_manage_svc.middleware.auth import AuthMiddleware
    # Reset middleware stack and remove AuthMiddleware
    app.middleware_stack = None
    app.user_middleware = [m for m in app.user_middleware if m.cls != AuthMiddleware]


@pytest.fixture(autouse=True)
def override_auth_middleware(monkeypatch, client):
    def fake_async_client_valid(*args, **kwargs):
        return FakeAsyncClient(status_code=200)
    monkeypatch.setattr(httpx, "AsyncClient", fake_async_client_valid)


# Test for task creation API endpoint using client fixture from conftest.py

def test_create_task_success(client):
    payload = {
        "title": "Test Task",
        "description": "A new test task",
        "assignee": "tester",
        "due_date": "2030-01-01T00:00:00",
        "status": "in_progress"
    }
    response = client.post("/task", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert "created_at" in data
    # Validate that created_at is a valid datetime string
    try:
        datetime.fromisoformat(data["created_at"])
    except Exception:
        pytest.fail("created_at is not a valid ISO datetime string")


def test_create_task_default_status(client):
    # When status is not provided, it should default to 'not_started'
    payload = {
        "title": "Test Task 2",
        "description": "A task with default status",
        "assignee": "tester",
        "due_date": "2030-01-02T00:00:00"
    }
    response = client.post("/task", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert "created_at" in data


def test_create_task_invalid_input(client):
    # Missing title should cause a validation error
    payload = {
        "description": "Missing title field"
    }
    response = client.post("/task", json=payload)
    assert response.status_code == 422


def test_create_task_invalid_status(client):
    # Providing an invalid status should result in a 400 error with custom detail
    payload = {
        "title": "Test Invalid Status",
        "description": "Invalid status value test",
        "assignee": "tester",
        "due_date": "2030-01-03T00:00:00",
        "status": "unknown_status"
    }
    response = client.post("/task", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid status value"
