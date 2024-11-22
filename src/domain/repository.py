from abc import ABC, abstractmethod


class AbstractRepository(ABC):
    @abstractmethod
    def save(self):
        pass
