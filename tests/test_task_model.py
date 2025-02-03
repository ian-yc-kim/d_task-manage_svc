import pytest

from d_task_manage_svc.models.task import Task


def test_create_and_query_task(db_session):
    # Use db_session fixture directly
    session = db_session
    new_task = Task(title='Test Task', description='A test description', assignee='Alice')
    session.add(new_task)
    session.commit()

    # Query the task back and verify its attributes
    queried_task = session.query(Task).filter_by(task_id=new_task.task_id).first()
    assert queried_task is not None
    assert queried_task.title == 'Test Task'
    assert queried_task.description == 'A test description'
    assert queried_task.assignee == 'Alice'
    assert queried_task.status == 'not_started'
    assert queried_task.created_at is not None


def test_task_default_status(db_session):
    # Use db_session fixture directly
    session = db_session
    task = Task(title='Another Task')
    session.add(task)
    session.commit()
    retrieved_task = session.query(Task).filter_by(task_id=task.task_id).first()
    assert retrieved_task.status == 'not_started'
