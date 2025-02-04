import sqlalchemy as sa
import pytest

from d_task_manage_svc.models.task import Task

def test_suggested_instructions_column(db_session):
    # Create a new task with suggested_instructions as None
    new_task = Task(title='Test Task', suggested_instructions=None)
    db_session.add(new_task)
    db_session.commit()
    
    # Retrieve the task and check that suggested_instructions is None
    retrieved_task = db_session.execute(sa.select(Task).where(Task.task_id == new_task.task_id)).scalar_one()
    assert retrieved_task.suggested_instructions is None
    
    # Update the suggested_instructions column
    new_value = 'This is an auto-generated instruction.'
    retrieved_task.suggested_instructions = new_value
    db_session.commit()

    # Retrieve again and check
    updated_task = db_session.execute(sa.select(Task).where(Task.task_id == new_task.task_id)).scalar_one()
    assert updated_task.suggested_instructions == new_value
