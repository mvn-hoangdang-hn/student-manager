
# app/schemas/grade.py

from typing import Optional, Any
from uuid import UUID
from datetime import datetime

from pydantic import constr, validator, Field
from sqlmodel import SQLModel


class GradeBase(SQLModel):
    student_id: str = Field(
        ..., description="Student ID reference"
    )
    subject: constr(min_length=1, max_length=50) = Field(
        ..., description="Subject name"
    )
    score: float = Field(
        ..., ge=0, description="Score achieved"
    )
    max_score: float = Field(
        default=10.0, gt=0, description="Maximum possible score"
    )
    grade_type: str = Field(
        default="regular", max_length=20, description="Type of grade"
    )
    semester: constr(min_length=1, max_length=10) = Field(
        ..., description="Semester"
    )
    academic_year: constr(min_length=1, max_length=10) = Field(
        ..., description="Academic year"
    )

    @validator("subject")
    def subject_must_not_be_blank(cls, v: str):
        if not v.strip():
            raise ValueError("Subject must not be empty")
        return v.strip().title()

    @validator("semester")
    def semester_must_not_be_blank(cls, v: str):
        if not v.strip():
            raise ValueError("Semester must not be empty")
        return v.strip()

    @validator("academic_year")
    def academic_year_must_not_be_blank(cls, v: str):
        if not v.strip():
            raise ValueError("Academic year must not be empty")
        return v.strip()


class GradeCreate(GradeBase):
    pass


class GradeUpdate(SQLModel):
    subject: Optional[constr(min_length=1, max_length=50)] = Field(
        None, description="Subject name (for update)"
    )
    score: Optional[float] = Field(
        None, ge=0, description="Score achieved (for update)"
    )
    max_score: Optional[float] = Field(
        None, gt=0, description="Maximum possible score (for update)"
    )
    grade_type: Optional[str] = Field(
        None, max_length=20, description="Type of grade (for update)"
    )
    semester: Optional[constr(min_length=1, max_length=10)] = Field(
        None, description="Semester (for update)"
    )
    academic_year: Optional[constr(min_length=1, max_length=10)] = Field(
        None, description="Academic year (for update)"
    )

    @validator("subject")
    def subject_must_not_be_blank(cls, v: Optional[str]):
        if v is not None and not v.strip():
            raise ValueError("Subject must not be empty")
        return v.strip().title() if v else v

    @validator("semester")
    def semester_must_not_be_blank(cls, v: Optional[str]):
        if v is not None and not v.strip():
            raise ValueError("Semester must not be empty")
        return v.strip() if v else v

    @validator("academic_year")
    def academic_year_must_not_be_blank(cls, v: Optional[str]):
        if v is not None and not v.strip():
            raise ValueError("Academic year must not be empty")
        return v.strip() if v else v


class GradeRead(SQLModel):
    id: UUID
    student_id: str
    subject: str
    score: float
    max_score: float
    grade_type: str
    semester: str
    academic_year: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class GradeWithStudent(GradeRead):
    student_name: str
    student_email: str

    model_config = {
        "from_attributes": True
    }


T = Any


class GradeResponseModel(SQLModel):
    success: bool = Field(
        ..., description="Indicates whether the operation was successful"
    )
    data: Optional[T] = Field(
        None, description="Returned payload (object or list)"
    )
    message: Optional[str] = Field(
        None, description="Additional message (if any)"
    )

    model_config = {
        "from_attributes": True
    }