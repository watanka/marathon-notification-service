from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infrastructure.models import MarathonInfoDB, Course
from src.infrastructure.database import Base
from src.adapters.outbound.repository import MarathonRepository
from datetime import datetime
import pytest



@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)

@pytest.fixture
def sample_marathons(db_session):
    repository = MarathonRepository(db_session)
    full_course = Course(distance=42, name="풀코스")
    half_course = Course(distance=21, name="하프코스")
    ten_k = Course(distance=10, name="10km")
    five_k = Course(distance=5, name="5km ")
    db_session.add_all([full_course, half_course, ten_k, five_k])
    db_session.commit()

    marathons = [
        MarathonInfoDB(
            title="서울 마라톤",
            race_date=datetime(2024, 3, 15, 9, 0, 0),
            location="서울특별시",
            homepage = 'example.com',
            registration_start_date=datetime(2024, 1, 1),
            registration_end_date=datetime(2024, 2, 28),
        ),
        MarathonInfoDB(
            title="부산 마라톤",
            race_date=datetime(2024, 3, 20, 8, 0, 0),
            location="부산광역시",
            homepage = 'example.com',
            registration_start_date=datetime(2024, 2, 1),
            registration_end_date=datetime(2024, 3, 10),
        ),
        MarathonInfoDB(
            title="제주 마라톤",
            race_date=datetime(2024, 3, 29, 9, 30, 0),
            location="제주특별자치도",
            homepage = 'example.com',
            registration_start_date=datetime(2024, 2, 15),
            registration_end_date=datetime(2024, 3, 25),
        ),
    ]

    courses_info = [
        [half_course, full_course],
        [ten_k],
        [half_course, five_k],
    ]
    for marathon, courses in zip(marathons, courses_info):
        marathon.courses.extend(courses)
        db_session.add(marathon)

        
    db_session.commit()

    return marathons



class TestMarathonRepository:
    def test_get_marathon_info_by_race_date(self, db_session, sample_marathons):
        repository = MarathonRepository(db_session)
        
        # 2024년 3월과 4월 마라톤 조회
        march_2024 = datetime(2024, 3, 1)
        april_2024 = datetime(2024, 4, 1)
        results = repository.get_by_race_date(march_2024, april_2024)

        assert len(results) == 3
        assert all(m.race_date.month in [3, 4] for m in results)
        assert all(m.race_date.year == 2024 for m in results)
    
    def test_get_marathons_by_course(self, db_session, sample_marathons):
        repository = MarathonRepository(db_session)
        # 하프 코스가 있는 마라톤 조회
        results = repository.get_by_distance(21)

        assert len(results) == 2
    
    def test_get_marathons_by_registration_period(self, db_session, sample_marathons):
        repository = MarathonRepository(db_session)
        # 특정 날짜에 등록 가능한 마라톤 조회
        check_date = datetime(2024, 2, 20)
        results = repository.get_by_registration_period(check_date)
        assert len(results) == 3
        assert all(
            m.registration_start_date <= check_date <= m.registration_end_date 
            for m in results
        )

    def test_get_marathons_by_region(self, db_session, sample_marathons):
        repository = MarathonRepository(db_session)
        region = '서울특별시'
        results = repository.get_by_region(region)

        assert len(results) == 1
        assert results[0].title == '서울 마라톤'
    
    def test_get_marathons_with_multiple_conditions(self, db_session, sample_marathons):
        repository = MarathonRepository(db_session)

        # 여러 조건을 조합한 조회
        conditions = {
            'registration_status': False,
            'region': '서울특별시',
            'course': 21,
            'race_search_start_date': datetime(2024, 3, 1),
            'race_search_end_date': datetime(2024, 4, 1)
        }
        results = repository.get_marathons(**conditions)
        assert len(results) == 1
        assert results[0].title == "서울 마라톤"
        assert 21 in [c.distance for c in results[0].courses]
        assert results[0].race_date.month == 3

    def test_get_marathons_with_location(self, db_session, sample_marathons):
        repository = MarathonRepository(db_session)
        results = repository.get_by_region("부산광역시")
        assert len(results) == 1
        assert results[0].location == "부산광역시"

    def test_empty_results(self, db_session, sample_marathons):
        repository = MarathonRepository(db_session)
        # 조건에 맞는 데이터가 없는 경우
        results = repository.get_by_registration_period(datetime(2025, 5, 1))
        assert len(results) == 0
    
    def test_invalid_date_handling(self, db_session, sample_marathons):
        repository = MarathonRepository(db_session)
        # 잘못된 날짜 입력 처리
        with pytest.raises(ValueError):
            repository.get_by_registration_period(datetime(2024, 13, 1))

    @pytest.mark.parametrize("course,expected_count", [
        (42, 1),
        (21, 2),
        (10, 1),
        (5, 1),
        (38, 0),
    ])
    def test_course_variations(self, db_session, sample_marathons, course, expected_count):
        repository = MarathonRepository(db_session)
        results = repository.get_by_distance(course)
        assert len(results) == expected_count