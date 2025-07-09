# app/repositories/student_repository.py

from typing import Sequence, Optional
from uuid import UUID

from sqlmodel import Session, select
from fastapi import HTTPException, status

from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate
from app.repositories.student_repository_interface import IStudentRepository


class StudentRepository(IStudentRepository):
    """
    Implementation của IStudentRepository, dùng SQLModel để thao tác CRUD trên bảng students.
    """

    def __init__(self, session: Session):
        self.session = session

    def create(self, student_in: StudentCreate) -> Student:
        # Kiểm tra email đã tồn tại chưa
        existing = self.session.exec(
            select(Student).where(Student.email == student_in.email)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã tồn tại"
            )

        # Tạo object Student từ dữ liệu đã validate
        student_data = student_in.model_dump()
        obj = Student(**student_data)

        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[Student]:
        return self.session.exec(
            select(Student).offset(skip).limit(limit)
        ).all()

    def get(self, student_id: UUID) -> Optional[Student]:
        return self.session.get(Student, str(student_id))

    def update(self, student_id: UUID, student_in: StudentUpdate) -> Student:
        db_obj = self.session.get(Student, str(student_id))
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student không tồn tại"
            )

        data = student_in.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(db_obj, key, value)

        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, student_id: UUID) -> None:
        db_obj = self.session.get(Student, str(student_id))
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student không tồn tại"
            )

        self.session.delete(db_obj)
        self.session.commit()