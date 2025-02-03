import pytest
from datetime import datetime

from fastapi.testclient import TestClient

from d_task_manage_svc.models.task import Task
from d_task_manage_svc.app import app
from d_task_manage_svc.middleware.auth import AuthMiddleware


@pytest.fixture(autouse=True)
def bypass_auth(monkeypatch):
    """Bypass authentication middleware to avoid 401 errors during tests."""
    app.middleware_stack = None
    app.user_middleware = [m for m in app.user_middleware if m.cls != AuthMiddleware]


def create_sample_task(db, title: str, assignee: str):
    task = Task(title=title, description='Sample description', assignee=assignee)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def test_get_tasks_valid_request_with_tasks(client, db_session):
    # Arrange: Create sample tasks assigned to 'john'
    session = db_session
    create_sample_task(session, 'Task 1', 'john')
    create_sample_task(session, 'Task 2', 'john')
    create_sample_task(session, 'Task 3', 'doe')  # different user

    # Act: Retrieve tasks for user 'john'
    response = client.get("/task", params={"username": "john", "limit": 10, "offset": 0})

    # Assert
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    for task in data:
        assert task["assignee"] == "john"
        # Check that created_at is valid ISO datetime
        datetime.fromisoformat(task["created_at"])


def test_get_tasks_valid_request_empty_list(client):
    # Act: Query for a username with no tasks
    response = client.get("/task", params={"username": "nonexistent", "limit": 10, "offset": 0})

    # Assert
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_tasks_invalid_username(client):
    # Act: Provide empty username
    response = client.get("/task", params={"username": "   ", "limit": 10, "offset": 0})

    # Assert
    assert response.status_code == 400, response.text
    data = response.json()
    assert "Username must be a non-empty string" in data["detail"]


def test_get_tasks_invalid_limit(client):
    # Act: Provide negative limit
    response = client.get("/task", params={"username": "john", "limit": -1, "offset": 0})

    # Assert
    assert response.status_code == 400, response.text
    data = response.json()
    assert "Invalid pagination parameters" in data["detail"]


def test_get_tasks_invalid_offset(client):
    # Act: Provide negative offset
    response = client.get("/task", params={"username": "john", "limit": 10, "offset": -5})

    # Assert
    assert response.status_code == 400, response.text
    data = response.json()
    assert "Invalid pagination parameters" in data["detail"]


def test_get_tasks_limit_exceeds_cap(client):
    # Act: Provide limit greater than allowed cap
    response = client.get("/task", params={"username": "john", "limit": 101, "offset": 0})

    # Assert
    assert response.status_code == 400, response.text
    data = response.json()
    assert "Invalid pagination parameters" in data["detail"]
