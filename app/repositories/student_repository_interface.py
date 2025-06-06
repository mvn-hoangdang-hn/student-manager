# app/repositories/student_repository_interface.py

from abc import ABC, abstractmethod
from typing import Sequence, Optional
from uuid import UUID

from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate


class IStudentRepository(ABC):


    @abstractmethod
    def create(self, student_in: StudentCreate) -> Student:

        raise NotImplementedError

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[Student]:

        raise NotImplementedError

    @abstractmethod
    def get(self, student_id: UUID) -> Optional[Student]:

        raise NotImplementedError

    @abstractmethod
    def update(self, student_id: UUID, student_in: StudentUpdate) -> Student:

        raise NotImplementedError

    @abstractmethod
    def delete(self, student_id: UUID) -> None:

        raise NotImplementedError
