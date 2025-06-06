# app/schemas/student.py

from typing import Optional, Any
from uuid import UUID
from datetime import datetime

from pydantic import EmailStr, constr, validator
from sqlmodel import SQLModel, Field


class StudentBase(SQLModel):
    name: constr(min_length=1, max_length=100) = Field(
        ..., description="Student full name"
    )
    email: EmailStr = Field(
        ..., description="Student email, must be valid and unique"
    )
    enrollment_date: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Enrollment date (timestamp). Defaults to current time if not provided."
    )

    @validator("name")
    def name_must_not_be_blank(cls, v: str):
        if not v.strip():
            raise ValueError("Name must not be empty")
        return v.title()


class StudentCreate(StudentBase):
    pass


class StudentUpdate(SQLModel):
    name: Optional[constr(min_length=1, max_length=100)] = Field(
        None, description="Student full name (for update)"
    )
    email: Optional[EmailStr] = Field(
        None, description="Student email (for update)"
    )
    enrollment_date: Optional[datetime] = Field(
        None, description="Enrollment date (for update)"
    )

    @validator("name")
    def name_must_not_be_blank(cls, v: Optional[str]):
        if v is not None and not v.strip():
            raise ValueError("Name must not be empty")
        return v.title() if v else v


class StudentRead(SQLModel):
    id: UUID
    name: str
    email: EmailStr
    enrollment_date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


T = Any


class ResponseModel(SQLModel):
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
