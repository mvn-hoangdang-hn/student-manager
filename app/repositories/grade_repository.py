from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from app.models.grade import Grade
from app.schemas.grade import GradeCreate, GradeUpdate
from .grade_repository_interface import GradeRepositoryInterface


class GradeRepository(GradeRepositoryInterface):
    """Implementation của Grade Repository"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, grade_data: GradeCreate) -> Grade:
        """Tạo điểm mới"""
        db_grade = Grade(**grade_data.dict())
        self.db.add(db_grade)
        self.db.commit()
        self.db.refresh(db_grade)
        return db_grade

    def get_by_id(self, grade_id: int) -> Optional[Grade]:
        """Lấy điểm theo ID"""
        return self.db.query(Grade).filter(Grade.id == grade_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Grade]:
        """Lấy tất cả điểm với phân trang"""
        return self.db.query(Grade).offset(skip).limit(limit).all()

    def get_by_student_id(self, student_id: int) -> List[Grade]:
        """Lấy tất cả điểm của một học sinh"""
        return self.db.query(Grade).filter(Grade.student_id == student_id).all()

    def get_by_subject(self, subject: str) -> List[Grade]:
        """Lấy tất cả điểm theo môn học"""
        return self.db.query(Grade).filter(Grade.subject == subject).all()

    def get_by_semester(self, semester: str, academic_year: str) -> List[Grade]:
        """Lấy tất cả điểm theo học kỳ và năm học"""
        return self.db.query(Grade).filter(
            and_(
                Grade.semester == semester,
                Grade.academic_year == academic_year
            )
        ).all()

    def get_by_student_and_subject(self, student_id: int, subject: str) -> List[Grade]:
        """Lấy điểm của học sinh theo môn học"""
        return self.db.query(Grade).filter(
            and_(
                Grade.student_id == student_id,
                Grade.subject == subject
            )
        ).all()

    def update(self, grade_id: int, grade_data: GradeUpdate) -> Optional[Grade]:
        """Cập nhật điểm"""
        db_grade = self.db.query(Grade).filter(Grade.id == grade_id).first()
        if db_grade:
            update_data = grade_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_grade, field, value)
            self.db.commit()
            self.db.refresh(db_grade)
        return db_grade

    def delete(self, grade_id: int) -> bool:
        """Xóa điểm"""
        db_grade = self.db.query(Grade).filter(Grade.id == grade_id).first()
        if db_grade:
            self.db.delete(db_grade)
            self.db.commit()
            return True
        return False

    def exists(self, grade_id: int) -> bool:
        """Kiểm tra điểm có tồn tại không"""
        return self.db.query(Grade).filter(Grade.id == grade_id).first() is not None

    def count_by_student(self, student_id: int) -> int:
        """Đếm số điểm của một học sinh"""
        return self.db.query(Grade).filter(Grade.student_id == student_id).count()

    def get_average_by_student(self, student_id: int, subject: Optional[str] = None) -> float:
        """Tính điểm trung bình của học sinh (có thể theo môn)"""
        query = self.db.query(func.avg(Grade.score)).filter(Grade.student_id == student_id)

        if subject:
            query = query.filter(Grade.subject == subject)

        result = query.scalar()
        return float(result) if result else 0.0

    # Thêm một số method bổ sung hữu ích

    def get_by_student_and_semester(self, student_id: int, semester: str, academic_year: str) -> List[Grade]:
        """Lấy điểm của học sinh theo học kỳ"""
        return self.db.query(Grade).filter(
            and_(
                Grade.student_id == student_id,
                Grade.semester == semester,
                Grade.academic_year == academic_year
            )
        ).all()

    def get_highest_score_by_subject(self, subject: str) -> Optional[Grade]:
        """Lấy điểm cao nhất của một môn học"""
        return self.db.query(Grade).filter(Grade.subject == subject).order_by(Grade.score.desc()).first()

    def get_lowest_score_by_subject(self, subject: str) -> Optional[Grade]:
        """Lấy điểm thấp nhất của một môn học"""
        return self.db.query(Grade).filter(Grade.subject == subject).order_by(Grade.score.asc()).first()

    def get_grades_above_score(self, min_score: float) -> List[Grade]:
        """Lấy tất cả điểm trên một ngưỡng"""
        return self.db.query(Grade).filter(Grade.score >= min_score).all()

    def get_grades_below_score(self, max_score: float) -> List[Grade]:
        """Lấy tất cả điểm dưới một ngưỡng"""
        return self.db.query(Grade).filter(Grade.score <= max_score).all()

    def get_subject_statistics(self, subject: str) -> dict:
        """Thống kê điểm của một môn học"""
        grades = self.db.query(Grade.score).filter(Grade.subject == subject).all()

        if not grades:
            return {
                "count": 0,
                "average": 0.0,
                "max": 0.0,
                "min": 0.0
            }

        scores = [grade.score for grade in grades]

        return {
            "count": len(scores),
            "average": sum(scores) / len(scores),
            "max": max(scores),
            "min": min(scores)
        }
