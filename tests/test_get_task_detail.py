import pytest
from datetime import datetime

from fastapi.testclient import TestClient

from d_task_manage_svc.models.task import Task
from d_task_manage_svc.app import app


@pytest.fixture(autouse=True)
def bypass_auth(monkeypatch):
    """Bypass authentication middleware to avoid 401 errors during tests."""
    from d_task_manage_svc.middleware.auth import AuthMiddleware
    app.middleware_stack = None
    app.user_middleware = [m for m in app.user_middleware if m.cls != AuthMiddleware]


def create_sample_task(db, title: str, assignee: str):
    task = Task(title=title, description='Sample description', assignee=assignee)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def test_get_task_detail_valid(client, db_session):
    # Arrange: Create a sample task
    session = db_session
    task = create_sample_task(session, 'Detailed Task', 'alice')

    # Act: Retrieve task detail using the newly implemented endpoint
    response = client.get(f"/task/{task.task_id}")

    # Assert: Verify that the response contains valid task details
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["task_id"] == task.task_id
    assert data["title"] == 'Detailed Task'
    assert data["assignee"] == 'alice'
    # Validate datetime format
    datetime.fromisoformat(data["created_at"])


def test_get_task_detail_not_found(client):
    # Act: Attempt to retrieve a task with a non-existent task_id
    response = client.get("/task/9999")

    # Assert: Should return 404 with appropriate message
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Task not found"


def test_get_task_detail_invalid_task_id(client):
    # Act: Provide an invalid task_id (zero)
    response = client.get("/task/0")

    # Assert: Should return 400 with validation error
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "task_id must be positive"


def test_get_task_detail_negative_task_id(client):
    # Act: Provide an invalid task_id (negative number)
    response = client.get("/task/-5")

    # Assert: Should return 400 with validation error
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "task_id must be positive"
