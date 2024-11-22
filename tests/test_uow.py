from src.infrastructure.uow import SqlAlchemyUnitOfWork, DEFAULT_SESSION_FACTORY
from src.adapters.outbound.repository import MarathonRepository
from datetime import datetime
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infrastructure.models import Base

@pytest.fixture
def db_session_maker():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    try:
        yield TestingSessionLocal
    finally:
        Base.metadata.drop_all(engine)

def test_uow_can_read_marathon_info(db_session_maker):
    session = db_session_maker()
    marathon_repository = MarathonRepository(session)
    marathon_repository.save(**{
        'title': 'test',
        'race_date': datetime.now(),
        'location': 'test',
        'homepage': 'test',
        'courses': ['HALF'],
        'organization_name': 'test',
        'registration_start_date': datetime.now(),
        'registration_end_date': datetime.now()
    })
    session.commit()

    uow = SqlAlchemyUnitOfWork(db_session_maker)

    with uow:
        marathon_list = uow.marathon_repository.get()
        assert marathon_list is not None
        assert len(marathon_list) > 0

def test_uow_can_save_marathon_info(db_session_maker):
    uow = SqlAlchemyUnitOfWork(db_session_maker)

    with uow:
        uow.marathon_repository.save(**{
            'title': 'test',
            'race_date': datetime.now(),
            'location': 'test',
            'homepage': 'test',
            'courses': ['HALF'],
            'organization_name': 'test',
            'registration_start_date': datetime.now(),
            'registration_end_date': datetime.now()
        })
        uow.commit()
    
    session = db_session_maker()
    marathon_repository = MarathonRepository(session)

    marathon_list = marathon_repository.get()
    assert len(marathon_list) == 1
