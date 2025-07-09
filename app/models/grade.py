# app/models/grade.py

import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, String, Float
from sqlalchemy.dialects.sqlite import TEXT

from sqlmodel import SQLModel, Field


class Grade(SQLModel, table=True):
    __tablename__ = "grades"

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

    student_id: str = Field(
        nullable=False, 
        foreign_key="students.id",
        description="Student ID reference"
    )
    subject: str = Field(nullable=False, max_length=50, description="Subject name")
    score: float = Field(nullable=False, ge=0, description="Score achieved")
    max_score: float = Field(default=10.0, gt=0, description="Maximum possible score")
    grade_type: str = Field(default="regular", max_length=20, description="Type of grade")
    semester: str = Field(nullable=False, max_length=10, description="Semester")
    academic_year: str = Field(nullable=False, max_length=10, description="Academic year")

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    )

    def __repr__(self):
        return f"<Grade(student_id={self.student_id}, subject='{self.subject}', score={self.score})>"