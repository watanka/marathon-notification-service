from src.infrastructure.models import MarathonInfoDB, Course, RecipientDB
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from src.domain.repository import AbstractRepository

class RecipientRepository(AbstractRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, recipients: RecipientDB):
        self.db.add(recipients)

    def get_all(self):
        return self.db.query(RecipientDB).all()

class MarathonRepository(AbstractRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, 
            title: str,
            race_date: datetime,
            location: str,
            homepage: str,
            courses: list[Course],
            organization_name: str,
            registration_start_date: datetime,
            registration_end_date: datetime):
        register_courses = []
        for course_name in courses:
            if course := self.create_or_get_course(course_name):
                register_courses.append(course)
        
        marathon_info = MarathonInfoDB(
            title=title,
            race_date=race_date,
            location=location,
            homepage=homepage,
            courses=register_courses,
            organization_name=organization_name,
            registration_start_date=registration_start_date,
            registration_end_date=registration_end_date
        )

        self.db.add(marathon_info)

    def get_by_title_race_date(self, title: str, race_date: datetime):
        return self.db.query(MarathonInfoDB).filter(and_(MarathonInfoDB.title == title,
                                                        MarathonInfoDB.race_date == race_date)).first()

    def create_or_get_course(self, course: str) -> Course:
        if result := Course.normalize_course_name(course):
            distance, name = result
        else:
            return

        course = self.db.query(Course).filter(
            Course.distance == distance
        ).first()

        if not course:
            course = Course(
                distance = distance,
                name = name
            )
            self.db.add(course)
            self.db.flush()

        return course

    def get(self):
        return self.db.query(MarathonInfoDB).all()
    
    def get_by_region(self, region: str):
        return self.db.query(MarathonInfoDB).filter(MarathonInfoDB.location == region).all()
    
    def get_by_distance(self, distance: int):
        return self.db.query(MarathonInfoDB)\
                .join(MarathonInfoDB.courses)\
                .filter(Course.distance == distance)\
                .distinct()\
                .all()

    def get_by_registration_period(self, check_date: datetime):
        return self.db.query(MarathonInfoDB).filter(and_(MarathonInfoDB.registration_start_date <= check_date,
                                                    MarathonInfoDB.registration_end_date >= check_date)).all()

    def get_by_race_date(self, search_start_date: datetime, search_end_date: datetime):
        return self.db.query(MarathonInfoDB).filter(
            and_(search_start_date <= MarathonInfoDB.race_date,
            MarathonInfoDB.race_date <= search_end_date)
        ).all()


    def get_marathons(self, 
                      registration_status: bool = True, 
                      region: str = None,
                      course: int = None,
                      race_search_start_date: datetime = None,
                      race_search_end_date: datetime = None
                      ):
        query = self.db.query(MarathonInfoDB)
        if registration_status:
            query = query.filter(and_(MarathonInfoDB.registration_start_date <= datetime.now(),
                                       MarathonInfoDB.registration_end_date >= datetime.now()))
        if course is not None:
            query = query.join(MarathonInfoDB.courses)\
                    .filter(Course.distance == course)\
                    .distinct()
        if region is not None:
            query = query.filter(MarathonInfoDB.location == region)
        if race_search_start_date is not None and race_search_end_date is not None:
            query = query.filter(and_(MarathonInfoDB.race_date >= race_search_start_date,
                                  MarathonInfoDB.race_date <= race_search_end_date)
                                  )
        return query.all()
