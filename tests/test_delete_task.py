import pytest
from fastapi import status


def test_delete_task_success(client):
    headers = {"X-Session-Token": "testtoken"}
    # Create a new task using the POST endpoint
    task_payload = {
        "title": "Task to be deleted",
        "description": "This task will be deleted",
        "assignee": "tester",
        "due_date": "2024-12-31T00:00:00",
        "status": "not_started"
    }
    response = client.post("/task", json=task_payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    task_id = data.get("task_id")
    
    # Delete the created task
    response = client.delete(f"/task/{task_id}", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.text
    
    # Verify that the task is indeed deleted by attempting to retrieve it
    response = client.get(f"/task/{task_id}", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text


def test_delete_nonexistent_task(client):
    headers = {"X-Session-Token": "testtoken"}
    # Attempt to delete a task with an id that doesn't exist
    nonexistent_id = 9999
    response = client.delete(f"/task/{nonexistent_id}", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    data = response.json()
    assert data.get("detail") == "Task not found"


def test_delete_invalid_task_id(client):
    headers = {"X-Session-Token": "testtoken"}
    # Attempt to delete a task with an invalid (non-positive) task_id
    invalid_id = 0
    response = client.delete(f"/task/{invalid_id}", headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.text
    data = response.json()
    assert "task_id must be positive" in data.get("detail")
