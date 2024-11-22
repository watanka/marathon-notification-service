from abc import ABC, abstractmethod
from src.domain.repository import AbstractRepository

class AbstractUnitOfWork(ABC):
    marathon_repository: AbstractRepository
    
    def __enter__(self):
        """컨텍스트 시작"""
        return self

    def __exit__(self, *args):
       self.rollback()

    @abstractmethod
    def commit(self):
        """변경사항 커밋"""
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        """변경사항 롤백"""
        raise NotImplementedError