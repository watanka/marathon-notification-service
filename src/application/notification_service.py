from src.ports.outbound import NotificationPort
from src.domain.models import MarathonInfo

class NotificationService:
    def __init__(self, notification_adapters: list[NotificationPort]):
        self.notification_adapters = notification_adapters

    def notify_new_marathon(self, 
                            message_title: str, 
                            marathon_list: list[MarathonInfo], 
                            recipients: list[dict]):
        
        for adapter in self.notification_adapters:
            for recipient_dict in recipients:                
                message = self._create_marathon_message(message_title, marathon_list)
                adapter.send_notification(message, recipient_dict['phone_number'])

    def _create_marathon_message(self, message_title: str, marathon_list: list[MarathonInfo]) -> str:
        return f"🏃‍♂️{message_title}🏃‍♂️\n"+ "\n".join([
            f"""
제목: {marathon.title}
일시: {marathon.race_date.strftime('%Y-%m-%d %H:%M')}
접수기간: {marathon.registration_start_date.strftime('%Y-%m-%d')} ~ {marathon.registration_end_date.strftime('%Y-%m-%d')}
장소: {marathon.location}
링크: {marathon.homepage}
        """.strip() for marathon in marathon_list
        ])
