import logging
from datetime import datetime
from enum import Enum
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from d_task_manage_svc.models.task import Task
from d_task_manage_svc.models.base import get_db

"""
Module for Task-related API endpoints.
This module defines the endpoints for creating tasks.
"""

# Router instance for task endpoints
router = APIRouter()

class TaskStatus(str, Enum):
    """Enum for task status values."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class TaskCreate(BaseModel):
    """Schema for creating a new task. Contains task details required for task creation.

    Attributes:
        title (str): Title of the task.
        description (str, optional): Detailed description of the task.
        assignee (str, optional): Person assigned to the task.
        due_date (datetime, optional): Due date for the task.
        status (TaskStatus): Status of the task. Must be one of not_started, in_progress, completed. Defaults to not_started.
    """
    title: str = Field(..., description="Title of the task")
    description: Optional[str] = Field(None, description="Detailed description of the task")
    assignee: Optional[str] = Field(None, description="Person assigned to the task")
    due_date: Optional[datetime] = Field(None, description="Due date for the task")
    status: TaskStatus = Field(TaskStatus.NOT_STARTED, description="Status of the task")

class TaskCreateResponse(BaseModel):
    """Response model for task creation.

    Attributes:
        task_id (int): The unique identifier of the created task.
        created_at (datetime): The timestamp when the task was created.
    """
    task_id: int = Field(..., description="The unique identifier of the created task")
    created_at: datetime = Field(..., description="The timestamp when the task was created")

@router.post("/task", response_model=TaskCreateResponse, summary="Create a new task")
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Endpoint to create a new task.

    Parameters:
        task (TaskCreate): The task creation request data containing title, description, assignee, due_date, and status.
        db (Session): Database session provided by dependency injection.

    Returns:
        TaskCreateResponse: Contains the auto-generated task_id and created_at timestamp.

    Raises:
        HTTPException: If an internal error occurs during task creation.
    """
    try:
        new_task = Task(
            title=task.title,
            description=task.description,
            assignee=task.assignee,
            due_date=task.due_date,
            status=task.status.value
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return TaskCreateResponse(task_id=new_task.task_id, created_at=new_task.created_at)
    except Exception as e:
        logging.error(e, exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
