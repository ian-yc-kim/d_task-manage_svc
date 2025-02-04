from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from .base import Base


class Task(Base):
    """Task model for persisting task information."""
    __tablename__ = 'tasks'

    task_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    assignee = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default='not_started')
    suggested_instructions = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())
