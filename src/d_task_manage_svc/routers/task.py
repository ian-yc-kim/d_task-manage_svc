import logging
from datetime import datetime
from enum import Enum
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from d_task_manage_svc.models.task import Task
from d_task_manage_svc.models.base import get_db

"""
Module for Task-related API endpoints.
This module defines the endpoints for creating tasks and retrieving tasks assigned to a user with pagination.
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
        description (Optional[str]): Detailed description of the task.
        assignee (Optional[str]): Person assigned to the task.
        due_date (Optional[datetime]): Due date for the task.
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

class TaskRead(BaseModel):
    """Pydantic model for reading task information.

    Attributes:
        task_id (int): The unique identifier of the task.
        title (str): The title of the task.
        description (Optional[str]): The detailed description of the task.
        assignee (Optional[str]): The user assigned to the task.
        due_date (Optional[datetime]): The due date of the task.
        status (str): The status of the task.
        created_at (datetime): The creation timestamp of the task.
    """
    task_id: int
    title: str
    description: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

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

@router.get("/task", response_model=List[TaskRead], summary="Retrieve tasks for a user with pagination")
async def get_tasks(
    username: str = Query(..., description="Username of the assignee", min_length=1),
    limit: int = Query(20, description="Limit number of tasks"),
    offset: int = Query(0, description="Offset for tasks"),
    db: Session = Depends(get_db)
):
    """Endpoint to retrieve tasks assigned to a given user with pagination.

    Query Parameters:
        username (str): The username of the assignee. Must be a non-empty string.
        limit (int): Maximum number of tasks to return. Defaults to 20. Capped at 100.
        offset (int): The offset for pagination. Defaults to 0.

    Returns:
        List[TaskRead]: A list of tasks assigned to the specified user. Returns an empty list if no tasks are found.

    Raises:
        HTTPException: With status 400 for invalid inputs and 500 for unexpected errors.
    """
    # Manual validation to enforce our own limits
    if username.strip() == "":
        raise HTTPException(status_code=400, detail="Username must be a non-empty string")
    if limit < 0 or limit > 100 or offset < 0:
        raise HTTPException(status_code=400, detail="Invalid pagination parameters: limit must be between 0 and 100 and offset must be non-negative")
    
    try:
        stmt = select(Task).where(Task.assignee == username).offset(offset).limit(limit)
        result = db.execute(stmt)
        tasks = result.scalars().all()
        return [TaskRead.from_orm(task) for task in tasks]
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
