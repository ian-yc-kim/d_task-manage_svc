"""Tests for asynchronous instruction generation triggering in create_task and update_task endpoints.

This module contains tests to verify that the asynchronous background task for instruction generation is scheduled only when complete data is provided, and that errors during scheduling are logged appropriately.
"""

import pytest
import logging
from datetime import datetime

# Tests for ensuring asynchronous instruction generation is triggered correctly


def test_create_task_with_complete_data(client, caplog):
    caplog.clear()
    payload = {
        "title": "Complete Task",
        "description": "This task has full details.",
        "assignee": "tester",
        "due_date": "2030-01-01T00:00:00",
        "status": "in_progress"
    }
    response = client.post("/task", json=payload)
    assert response.status_code == 200, response.text
    # When task is created with complete data, no warning should be logged
    for record in caplog.records:
        assert "not scheduled" not in record.message


def test_create_task_with_missing_description(client, caplog):
    caplog.clear()
    payload = {
        "title": "Incomplete Task",
        "description": "",
        "assignee": "tester",
        "due_date": "2030-01-01T00:00:00",
        "status": "in_progress"
    }
    response = client.post("/task", json=payload)
    # Even with missing description, task creation should succeed
    assert response.status_code == 200, response.text
    found_warning = any("not scheduled" in record.message for record in caplog.records)
    assert found_warning, "Expected warning log for missing description in create_task."


def test_update_task_with_complete_data(client, db_session, caplog):
    caplog.clear()
    # First, create a task
    payload_create = {
        "title": "Original Title",
        "description": "Original description",
        "assignee": "tester",
        "due_date": "2030-01-01T00:00:00",
        "status": "in_progress"
    }
    response_create = client.post("/task", json=payload_create)
    assert response_create.status_code == 200, response_create.text
    task_id = response_create.json()["task_id"]
    
    # Now update with complete data
    payload_update = {
        "title": "Updated Title",
        "description": "Updated description"
    }
    response = client.put(f"/task/{task_id}", json=payload_update)
    assert response.status_code == 200, response.text
    for record in caplog.records:
        assert "not scheduled" not in record.message


def test_update_task_with_missing_title(client, db_session, caplog):
    caplog.clear()
    # Create a task with complete details
    payload_create = {
        "title": "Task to Update",
        "description": "Initial description",
        "assignee": "tester",
        "due_date": "2030-01-01T00:00:00",
        "status": "in_progress"
    }
    response_create = client.post("/task", json=payload_create)
    assert response_create.status_code == 200, response_create.text
    task_id = response_create.json()["task_id"]
    
    # Update the task with an empty title
    payload_update = {
        "title": "",
        "description": "Updated description"
    }
    response = client.put(f"/task/{task_id}", json=payload_update)
    # Update should succeed, but warning should be logged
    assert response.status_code == 200, response.text
    found_warning = any("not scheduled" in record.message for record in caplog.records)
    assert found_warning, "Expected warning log for missing title in update_task."


def test_create_task_background_task_failure(client, caplog, monkeypatch):
    caplog.clear()
    # Simulate failure in scheduling by monkeypatching trigger_instruction_generation to raise an exception
    from d_task_manage_svc.routers import task as task_module
    def fake_trigger(*args, **kwargs):
        raise Exception("Simulated scheduling failure")
    monkeypatch.setattr(task_module, "trigger_instruction_generation", fake_trigger)

    payload = {
        "title": "Task with scheduling failure",
        "description": "This task will simulate a scheduling failure.",
        "assignee": "tester",
        "due_date": "2030-01-01T00:00:00",
        "status": "in_progress"
    }
    response = client.post("/task", json=payload)
    assert response.status_code == 200, response.text
    found_error = any("Simulated scheduling failure" in record.message for record in caplog.records)
    assert found_error, "Expected error log for simulated scheduling failure in create_task."


def test_update_task_background_task_failure(client, db_session, caplog, monkeypatch):
    caplog.clear()
    from d_task_manage_svc.routers import task as task_module
    def fake_trigger(*args, **kwargs):
        raise Exception("Simulated scheduling failure")
    monkeypatch.setattr(task_module, "trigger_instruction_generation", fake_trigger)

    # Create a task normally
    payload_create = {
        "title": "Task for update scheduling failure",
        "description": "Initial description",
        "assignee": "tester",
        "due_date": "2030-01-01T00:00:00",
        "status": "in_progress"
    }
    response_create = client.post("/task", json=payload_create)
    assert response_create.status_code == 200, response_create.text
    task_id = response_create.json()["task_id"]

    # Update with complete data, which will trigger the fake scheduling failure
    payload_update = {
        "title": "Updated Title",
        "description": "Updated description"
    }
    response = client.put(f"/task/{task_id}", json=payload_update)
    assert response.status_code == 200, response.text
    found_error = any("Simulated scheduling failure" in record.message for record in caplog.records)
    assert found_error, "Expected error log for simulated scheduling failure in update_task."
