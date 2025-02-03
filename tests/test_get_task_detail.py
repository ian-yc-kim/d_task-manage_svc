import importlib
import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from d_task_manage_svc.models.task import Task
from d_task_manage_svc.app import app


@pytest.fixture(autouse=True)
def bypass_auth(monkeypatch):
    """Bypass authentication middleware to avoid 401 errors during tests.
    This fixture removes the AuthMiddleware from the app's middleware stack, allowing tests to focus on endpoint logic without authentication interference."""
    app.middleware_stack = None
    app.user_middleware = [m for m in app.user_middleware if m.cls.__name__ != 'AuthMiddleware']


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


def test_get_task_detail_missing_auth_token(db_session):
    """Test that missing session token returns 401 Unauthorized."""
    from fastapi.testclient import TestClient
    from d_task_manage_svc.models.base import get_db
    
    # Reload the app module to get the original middleware configuration
    import importlib
    from d_task_manage_svc import app as app_module
    importlib.reload(app_module)
    app_instance = app_module.app
    
    # Set up dependency override for the database using the session_local fixture from conftest
    from tests.conftest import session_local

    def override_session():
        session = session_local()()
        try:
            yield session
        finally:
            session.close()
    
    app_instance.dependency_overrides[get_db] = override_session
    client_with_auth = TestClient(app_instance)
    
    # Act: Call the endpoint without providing a session token
    response = client_with_auth.get("/task/1")
    
    # Assert: The AuthMiddleware should return 401 Unauthorized due to missing session token
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Session token is missing"
