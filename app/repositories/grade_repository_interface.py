from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.grade import Grade
from app.schemas.grade import GradeCreate, GradeUpdate


class GradeRepositoryInterface(ABC):
    """Interface cho Grade Repository"""

    @abstractmethod
    def create(self, grade_data: GradeCreate) -> Grade:
        """Tạo điểm mới"""
        pass

    @abstractmethod
    def get_by_id(self, grade_id: int) -> Optional[Grade]:
        """Lấy điểm theo ID"""
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Grade]:
        """Lấy tất cả điểm với phân trang"""
        pass

    @abstractmethod
    def get_by_student_id(self, student_id: int) -> List[Grade]:
        """Lấy tất cả điểm của một học sinh"""
        pass

    @abstractmethod
    def get_by_subject(self, subject: str) -> List[Grade]:
        """Lấy tất cả điểm theo môn học"""
        pass

    @abstractmethod
    def get_by_semester(self, semester: str, academic_year: str) -> List[Grade]:
        """Lấy tất cả điểm theo học kỳ và năm học"""
        pass

    @abstractmethod
    def get_by_student_and_subject(self, student_id: int, subject: str) -> List[Grade]:
        """Lấy điểm của học sinh theo môn học"""
        pass

    @abstractmethod
    def update(self, grade_id: int, grade_data: GradeUpdate) -> Optional[Grade]:
        """Cập nhật điểm"""
        pass

    @abstractmethod
    def delete(self, grade_id: int) -> bool:
        """Xóa điểm"""
        pass

    @abstractmethod
    def exists(self, grade_id: int) -> bool:
        """Kiểm tra điểm có tồn tại không"""
        pass

    @abstractmethod
    def count_by_student(self, student_id: int) -> int:
        """Đếm số điểm của một học sinh"""
        pass

    @abstractmethod
    def get_average_by_student(self, student_id: int, subject: Optional[str] = None) -> float:
        """Tính điểm trung bình của học sinh (có thể theo môn)"""
        pass