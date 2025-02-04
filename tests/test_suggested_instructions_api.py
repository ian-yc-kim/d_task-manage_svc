import pytest
from datetime import datetime

from d_task_manage_svc.models.task import Task


def test_task_detail_includes_null_suggested_instructions(client, db_session):
    """Test that when a task is created without suggested_instructions, the GET detail endpoint returns null for that field."""
    # Create a task without setting suggested_instructions
    task = Task(title='Task with no suggestion', description='No suggestions provided', assignee='tester')
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    # Fetch the task detail
    response = client.get(f"/task/{task.task_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert 'suggested_instructions' in data
    assert data['suggested_instructions'] is None


def test_task_detail_includes_populated_suggested_instructions(client, db_session):
    """Test that when a task has suggested_instructions set, the GET detail endpoint returns the correct value."""
    suggestion = 'This is an auto-generated suggestion.'
    task = Task(title='Task with suggestion', description='Has suggestion', assignee='tester', suggested_instructions=suggestion)
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    response = client.get(f"/task/{task.task_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert 'suggested_instructions' in data
    assert data['suggested_instructions'] == suggestion
