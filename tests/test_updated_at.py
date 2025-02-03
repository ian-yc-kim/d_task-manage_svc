import time
from d_task_manage_svc.models.task import Task

def test_updated_at_column(db_session):
    session = db_session
    # Create a new task
    task = Task(title='Initial Task', description='Initial description')
    session.add(task)
    session.commit()
    
    # Initially, updated_at should be None
    assert task.updated_at is None
    
    # Update the task
    task.title = 'Updated Task'
    session.commit()
    session.refresh(task)
    
    # After update, updated_at should be set
    assert task.updated_at is not None
