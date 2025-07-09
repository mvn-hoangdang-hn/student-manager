# app/routers/grade.py

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.grade import Grade
from app.models.student import Student
from app.schemas.grade import (
    GradeCreate,
    GradeUpdate,
    GradeRead,
    GradeWithStudent,
    GradeResponseModel
)
from app.schemas.student import ResponseModel

router = APIRouter(prefix="/grades", tags=["grades"])


@router.post("/", response_model=ResponseModel)
def create_grade(
        grade_data: GradeCreate,
        session: Session = Depends(get_session())
):
    """Create a new grade"""
    try:
        # Kiểm tra student tồn tại
        student = session.get(Student, grade_data.student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )

        # Tạo grade mới
        grade = Grade(**grade_data.model_dump())
        session.add(grade)
        session.commit()
        session.refresh(grade)

        return ResponseModel(
            success=True,
            data=GradeRead.model_validate(grade),
            message="Grade created successfully"
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/", response_model=ResponseModel)
def get_all_grades(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session())
):
    """Get all grades"""
    try:
        statement = select(Grade).offset(skip).limit(limit)
        grades = session.exec(statement).all()

        grades_data = [GradeRead.model_validate(grade) for grade in grades]

        return ResponseModel(
            success=True,
            data=grades_data,
            message=f"Retrieved {len(grades_data)} grades"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{grade_id}", response_model=ResponseModel)
def get_grade(
        grade_id: UUID,
        session: Session = Depends(get_session())
):
    """Get a specific grade by ID"""
    try:
        grade = session.get(Grade, str(grade_id))
        if not grade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grade not found"
            )

        return ResponseModel(
            success=True,
            data=GradeRead.model_validate(grade),
            message="Grade retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/student/{student_id}", response_model=ResponseModel)
def get_grades_by_student(
        student_id: str,
        session: Session = Depends(get_session())
):
    """Get all grades for a specific student"""
    try:
        # Kiểm tra student tồn tại
        student = session.get(Student, student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )

        statement = select(Grade).where(Grade.student_id == student_id)
        grades = session.exec(statement).all()

        grades_data = [GradeRead.model_validate(grade) for grade in grades]

        return ResponseModel(
            success=True,
            data=grades_data,
            message=f"Retrieved {len(grades_data)} grades for student"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/with-student/", response_model=ResponseModel)
def get_grades_with_student_info(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session())
):
    """Get all grades with student information"""
    try:
        statement = (
            select(Grade, Student)
            .join(Student, Grade.student_id == Student.id)
            .offset(skip)
            .limit(limit)
        )
        results = session.exec(statement).all()

        grades_with_student = []
        for grade, student in results:
            grade_data = GradeRead.model_validate(grade).model_dump()
            grade_data["student_name"] = student.name
            grade_data["student_email"] = student.email
            grades_with_student.append(GradeWithStudent(**grade_data))

        return ResponseModel(
            success=True,
            data=grades_with_student,
            message=f"Retrieved {len(grades_with_student)} grades with student info"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{grade_id}", response_model=ResponseModel)
def update_grade(
        grade_id: UUID,
        grade_update: GradeUpdate,
        session: Session = Depends(get_session())
):
    """Update a specific grade"""
    try:
        grade = session.get(Grade, str(grade_id))
        if not grade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grade not found"
            )

        # Cập nhật chỉ các field được cung cấp
        update_data = grade_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(grade, field, value)

        session.add(grade)
        session.commit()
        session.refresh(grade)

        return ResponseModel(
            success=True,
            data=GradeRead.model_validate(grade),
            message="Grade updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{grade_id}", response_model=ResponseModel)
def delete_grade(
        grade_id: UUID,
        session: Session = Depends(get_session())
):
    """Delete a specific grade"""
    try:
        grade = session.get(Grade, str(grade_id))
        if not grade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grade not found"
            )

        session.delete(grade)
        session.commit()

        return ResponseModel(
            success=True,
            data=None,
            message="Grade deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/statistics/by-subject", response_model=ResponseModel)
def get_statistics_by_subject(
        session: Session = Depends(get_session())
):
    """Get grade statistics by subject"""
    try:
        from sqlalchemy import func

        statement = (
            select(
                Grade.subject,
                func.count(Grade.id).label("total_grades"),
                func.avg(Grade.score).label("average_score"),
                func.min(Grade.score).label("min_score"),
                func.max(Grade.score).label("max_score")
            )
            .group_by(Grade.subject)
        )

        results = session.exec(statement).all()

        statistics = []
        for row in results:
            statistics.append({
                "subject": row.subject,
                "total_grades": row.total_grades,
                "average_score": round(row.average_score, 2) if row.average_score else 0,
                "min_score": row.min_score,
                "max_score": row.max_score
            })

        return ResponseModel(
            success=True,
            data=statistics,
            message="Statistics retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )