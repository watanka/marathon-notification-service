from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

from src.application.uow import AbstractUnitOfWork
from src.adapters.outbound.repository import MarathonRepository, RecipientRepository
from config import get_settings

settings = get_settings()

DEFAULT_SESSION_FACTORY = sessionmaker(bind=create_engine(
        settings.SQLALCHEMY_DATABASE_URL,
        connect_args={'client_encoding': 'utf8'}
))

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory
        self._session = None

    def __enter__(self) -> Session:
        self._session = self.session_factory()
        self.marathon_repository = MarathonRepository(self._session)
        self.recipient_repository = RecipientRepository(self._session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self._session.close()

    def commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()