from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from src.domain.models import MarathonInfo, Recipient
from sqlalchemy import Table, ForeignKey
from .database import Base
import re

class RecipientDB(Base):
    __tablename__ = 'recipient'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone_number = Column(String)

    def to_pydantic(self):
        return Recipient(
            name=self.name,
            phone_number=self.phone_number,
        )
    
    @classmethod
    def from_dict(cls, data: dict):
        instance = cls()  
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance

marathon_course_association = Table(
    'marathon_course_association',
    Base.metadata,
    Column('marathon_id', Integer, ForeignKey('marathon_info.id')),
    Column('course_id', Integer, ForeignKey('course.id'))
)


class Course(Base):
    __tablename__ = 'course'
    
    id = Column(Integer, primary_key = True)
    distance = Column(Float)
    name = Column(String)
    description = Column(String, nullable = True)

    @staticmethod
    def normalize_course_name(course: str) ->tuple[float, str]:
        """코스 이름을 정규화하여 거리, 이름, 타입을 반환"""
        course_name = course.upper().strip()
        
        if course_name == '하프' or course_name == 'HALF':
            return 21.0975, 'HALF'
        elif course_name == '풀' or course_name == 'FULL':
            return 42.195, 'FULL'
        elif course_name.endswith('KM'):
            # "10km", "5km" 등의 형식 처리
           if numbers := re.findall(r'\d+', course_name):
                distance = float(numbers[0])
                return distance, course_name
        else:
            print(f'{course_name}은 코스 DB에 반영되지 않았습니다.')
            return None

class MarathonInfoDB(Base):
    __tablename__ = "marathon_info"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    race_date = Column(DateTime)
    location = Column(String)
    homepage = Column(String)
    courses = relationship(
        Course,
        secondary = marathon_course_association,
    )
    organization_name = Column(String)
    registration_start_date = Column(DateTime)
    registration_end_date = Column(DateTime)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_pydantic(self):
        return MarathonInfo(
            title=self.title,
            race_date=self.race_date,
            location=self.location,
            course=[course.distance for course in self.courses],
            homepage=self.homepage,
            organization_name=self.organization_name,
            registration_start_date=self.registration_start_date,
            registration_end_date=self.registration_end_date,
        )
    
    @classmethod
    def from_dict(cls, data: dict):
        instance = cls()  
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance

