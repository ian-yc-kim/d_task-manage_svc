import pytest
from datetime import datetime

from d_task_manage_svc.models.task import Task
from d_task_manage_svc.app import app
from d_task_manage_svc.middleware.auth import AuthMiddleware

# Bypass authentication middleware for update task tests
@pytest.fixture(autouse=True)
def bypass_auth(monkeypatch):
    app.middleware_stack = None
    app.user_middleware = [m for m in app.user_middleware if m.cls.__name__ != "AuthMiddleware"]


def create_sample_task(db, title: str, assignee: str):
    task = Task(title=title, description='Sample description', assignee=assignee)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def test_update_task_success(client, db_session):
    # Arrange: Create a sample task
    session = db_session
    task = create_sample_task(session, 'Original Title', 'Alice')
    
    # Act: Update the task's title
    response = client.put(f"/task/{task.task_id}", json={"title": "Updated Title"})
    
    # Assert: Check for success and updated fields
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data.get("updated_at") is not None
    updated_at = datetime.fromisoformat(data["updated_at"])
    assert updated_at > task.created_at


def test_update_task_no_field(client, db_session):
    # Arrange: Create a sample task
    session = db_session
    task = create_sample_task(session, 'Test Task', 'Bob')
    
    # Act: Attempt to update with no fields
    response = client.put(f"/task/{task.task_id}", json={})
    
    # Assert: Expect a 400 error for missing update fields
    assert response.status_code == 400, response.text
    data = response.json()
    assert "At least one field must be provided" in data["detail"]


def test_update_task_nonexistent(client):
    # Act: Attempt to update a non-existent task
    response = client.put("/task/9999", json={"title": "Updated"})
    
    # Assert: Expect a 404 response
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Task not found"


def test_update_task_invalid_id(client):
    # Act: Attempt to update with an invalid (negative) task_id
    response = client.put("/task/-1", json={"title": "New Title"})
    
    # Assert: Expect a 400 response
    assert response.status_code == 400, response.text
    data = response.json()
    assert "task_id must be positive" in data["detail"]
