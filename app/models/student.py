# app/models/student.py

import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.sqlite import TEXT


from sqlmodel import SQLModel, Field


class Student(SQLModel, table=True):
    __tablename__ = "students"

    id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            TEXT,
            primary_key=True,
            default=lambda: str(uuid.uuid4()),
            unique=True,
            nullable=False
        ),
    )

    name: str = Field(nullable=False, max_length=100)
    email: str = Field(nullable=False, index=True, unique=True, max_length=100)
    enrollment_date: datetime = Field(default_factory=datetime.utcnow)

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    )
