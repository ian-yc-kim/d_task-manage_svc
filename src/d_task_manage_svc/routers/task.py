import logging
import asyncio
from datetime import datetime
from enum import Enum
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from d_task_manage_svc.models.task import Task
from d_task_manage_svc.models.base import get_db, SessionLocal
from d_task_manage_svc.instruction_generator import generate_instructions

"""
Module for Task-related API endpoints.
This module defines the endpoints for creating tasks, retrieving tasks assigned to a user with pagination, getting task details, updating tasks, and deleting tasks.
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
        updated_at (Optional[datetime]): The timestamp when the task was last updated.
    """
    task_id: int
    title: str
    description: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

class TaskUpdate(BaseModel):
    """Schema for updating an existing task. All fields are optional but at least one is required."""
    title: Optional[str] = Field(None, description="Updated title of the task")
    description: Optional[str] = Field(None, description="Updated description of the task")
    assignee: Optional[str] = Field(None, description="Updated assignee of the task")
    due_date: Optional[datetime] = Field(None, description="Updated due date of the task")
    status: Optional[TaskStatus] = Field(None, description="Updated task status")


def _format_instructions(instructions: List[str]) -> str:
    """Formats the list of instructions into a single string."""
    return "; ".join(instructions)


async def process_instruction_generation(task_id: int, title: str, description: str) -> None:
    """Background task to generate instructions and update the task record with suggested instructions."""
    try:
        instructions = await generate_instructions(title, description)
        if instructions:
            instructions_text = _format_instructions(instructions)
            session = SessionLocal()
            try:
                task_obj = session.query(Task).filter(Task.task_id == task_id).first()
                if task_obj:
                    task_obj.suggested_instructions = instructions_text
                    session.commit()
            except Exception as e:
                logging.error(e, exc_info=True)
                session.rollback()
            finally:
                session.close()
    except Exception as e:
        logging.error(e, exc_info=True)


def trigger_instruction_generation(task_id: int, title: str, description: str) -> None:
    """Synchronous wrapper to schedule the asynchronous instruction generation task."""
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(process_instruction_generation(task_id, title, description))
    except RuntimeError:
        # No running event loop, so start one temporarily
        try:
            asyncio.run(process_instruction_generation(task_id, title, description))
        except Exception as e:
            logging.error(e, exc_info=True)


@router.post("/task", response_model=TaskCreateResponse, summary="Create a new task")
async def create_task(task: TaskCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
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

        # Schedule background task for instruction generation if title and description are provided
        if new_task.title and new_task.description:
            background_tasks.add_task(trigger_instruction_generation, new_task.task_id, new_task.title, new_task.description)

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


@router.get("/task/{task_id}", response_model=TaskRead, summary="Retrieve task details")
async def get_task(task_id: int, db: Session = Depends(get_db)):
    if task_id <= 0:
        raise HTTPException(status_code=400, detail="task_id must be positive")
    try:
        stmt = select(Task).where(Task.task_id == task_id)
        result = db.execute(stmt)
        task = result.scalars().first()
    except Exception as e:
        logging.error(e, exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRead.from_orm(task)


@router.put("/task/{task_id}", response_model=TaskRead, summary="Update an existing task")
async def update_task(task_id: int, task_update: TaskUpdate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if task_id <= 0:
        raise HTTPException(status_code=400, detail="task_id must be positive")

    try:
        stmt = select(Task).where(Task.task_id == task_id)
        result = db.execute(stmt)
        task = result.scalars().first()
    except Exception as e:
        logging.error(e, exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="At least one field must be provided for update")

    for key, value in update_data.items():
        if key == "status":
            setattr(task, key, value.value if hasattr(value, "value") else value)
        else:
            setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    try:
        db.commit()
        db.refresh(task)
    except Exception as e:
        logging.error(e, exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    # Determine effective title and description for instruction generation
    effective_title = task.title
    effective_description = task.description
    if effective_title and effective_description:
        background_tasks.add_task(trigger_instruction_generation, task.task_id, effective_title, effective_description)

    return TaskRead.from_orm(task)


@router.delete("/task/{task_id}", status_code=204, summary="Delete a task")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    if task_id <= 0:
        raise HTTPException(status_code=400, detail="task_id must be positive")
    try:
        stmt = select(Task).where(Task.task_id == task_id)
        result = db.execute(stmt)
        task = result.scalars().first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        db.delete(task)
        db.commit()
        return
    except HTTPException:
        # Re-raise HTTP exceptions such as 400 or 404
        raise
    except Exception as e:
        logging.error(e, exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
