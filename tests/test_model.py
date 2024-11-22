import pytest
from datetime import datetime
from src.infrastructure.models import MarathonInfoDB, Course
from src.domain.models import MarathonInfo

@pytest.fixture
def sample_course():
    return Course(
        distance=42.195,
        name="FULL",
        description="풀 마라톤 코스"
    )

@pytest.fixture
def sample_marathon_db(sample_course):
    return MarathonInfoDB(
        title="서울마라톤 2024",
        race_date=datetime(2024, 3, 1, 9, 0),  # 2024년 3월 1일 09:00
        location="서울광장",
        courses=[sample_course],
        homepage="http://example.com",
        organization_name="서울시체육회",
        registration_start_date=datetime(2024, 1, 1),
        registration_end_date=datetime(2024, 2, 1)
    )

def test_marathon_db_to_pydantic(sample_marathon_db):
    # When: DB 모델을 Pydantic 모델로 변환
    marathon_info = MarathonInfo.model_validate(sample_marathon_db)
    
    # Then: 변환된 데이터 검증
    assert marathon_info.title == "서울마라톤 2024"
    assert marathon_info.race_date == datetime(2024, 3, 1, 9, 0)
    assert marathon_info.location == "서울광장"
    assert marathon_info.homepage == "http://example.com"
    assert marathon_info.organization_name == "서울시체육회"
    assert marathon_info.registration_start_date == datetime(2024, 1, 1)
    assert marathon_info.registration_end_date == datetime(2024, 2, 1)
    
    # 코스 정보 검증
    assert len(marathon_info.courses) == 1
    assert marathon_info.courses[0].distance == 42.195
    assert marathon_info.courses[0].name == "FULL"
    assert marathon_info.courses[0].description == "풀 마라톤 코스"

def test_marathon_db_list_to_pydantic(sample_marathon_db):
    # Given: DB 모델 리스트
    marathons_db = [sample_marathon_db, sample_marathon_db]
    
    # When: DB 모델 리스트를 Pydantic 모델 리스트로 변환
    marathons_info = [MarathonInfo.model_validate(m) for m in marathons_db]
    
    # Then: 변환된 리스트 검증
    assert len(marathons_info) == 2
    for marathon_info in marathons_info:
        assert isinstance(marathon_info, MarathonInfo)
        assert marathon_info.title == "서울마라톤 2024"
        assert len(marathon_info.courses) == 1

def test_registration_period_property(sample_marathon_db):
    # Given: 현재 시점이 접수 기간 내인 마라톤
    current_marathon = MarathonInfo.model_validate(sample_marathon_db)
    
    # 접수 기간이 지난 마라톤
    past_marathon = MarathonInfo.model_validate(MarathonInfoDB(
        title="지난 마라톤",
        race_date=datetime(2023, 12, 1),
        location="서울",
        homepage="http://example.com",
        courses=[],
        organization_name="주최사",
        registration_start_date=datetime(2023, 10, 1),
        registration_end_date=datetime(2023, 11, 1)
    ))
    
    # When & Then: 접수 기간 프로퍼티 검증
    if datetime.now() < datetime(2024, 2, 1):
        assert current_marathon.in_registration_period
    assert not past_marathon.in_registration_period

@pytest.mark.parametrize("invalid_data", [
    {"title": None},  # 필수 필드 누락
    {"race_date": "invalid-date"},  # 잘못된 날짜 형식
])
def test_invalid_marathon_data(invalid_data, sample_marathon_db):
    # Given: 유효하지 않은 데이터로 DB 모델 생성
    invalid_marathon = sample_marathon_db
    for key, value in invalid_data.items():
        setattr(invalid_marathon, key, value)
    
    # When & Then: Pydantic 모델 변환 시 예외 발생 확인
    with pytest.raises(Exception):
        MarathonInfo.model_validate(invalid_marathon)