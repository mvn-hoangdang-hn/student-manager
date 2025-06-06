# app/routers/student.py

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.schemas.student import StudentCreate, StudentRead, StudentUpdate, ResponseModel
from app.repositories.student_repository import StudentRepository
from app.core.database import get_session

router = APIRouter(prefix="/students", tags=["students"])


def get_student_repo(session: Session = Depends(get_session())) -> StudentRepository:
    return StudentRepository(session)


@router.post(
    "/",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Student",
)
def create_student(
    student_in: StudentCreate,
    repo: StudentRepository = Depends(get_student_repo),
):
    student = repo.create(student_in)
    return ResponseModel(success=True, data=student, message="Student created successfully")


@router.get(
    "/",
    response_model=ResponseModel,
    summary="Retrieve list of Students (with pagination)",
)
def read_students(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, gt=0, le=100, description="Number of records to return"),
    repo: StudentRepository = Depends(get_student_repo),
):
    students = repo.get_all(skip=skip, limit=limit)
    return ResponseModel(success=True, data=students, message=None)


@router.get(
    "/{student_id}",
    response_model=ResponseModel,
    summary="Retrieve a Student by ID (UUID)",
)
def read_student(
    student_id: UUID,
    repo: StudentRepository = Depends(get_student_repo),
):
    student = repo.get(student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return ResponseModel(success=True, data=student, message=None)


@router.put(
    "/{student_id}",
    response_model=ResponseModel,
    summary="Update a Student by ID (UUID)",
)
def update_student(
    student_id: UUID,
    student_in: StudentUpdate,
    repo: StudentRepository = Depends(get_student_repo),
):
    updated = repo.update(student_id, student_in)
    return ResponseModel(success=True, data=updated, message="Update successful")


@router.delete(
    "/{student_id}",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    summary="Delete a Student by ID (UUID)",
)
def delete_student(
    student_id: UUID,
    repo: StudentRepository = Depends(get_student_repo),
):
    repo.delete(student_id)
    return ResponseModel(success=True, data=None, message="Deletion successful")
