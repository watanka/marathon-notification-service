from abc import ABC, abstractmethod


class NotificationPort(ABC):
    @abstractmethod
    def send_notification(self, message: str, recipient: str) -> bool:
        pass