from twilio.rest import Client
import telegram
from src.ports.outbound import NotificationPort

class TwilioNotificationAdapter(NotificationPort):
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number

    def send_notification(self, message: str, recipient: str) -> bool:
        try:
            self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=recipient
            )
            return True
        except Exception as e:
            print(f"Twilio notification failed: {e}")
            return False

class TelegramNotificationAdapter(NotificationPort):
    def __init__(self, bot_token: str):
        self.bot = telegram.Bot(token=bot_token)

    def send_notification(self, message: str, chat_id: str) -> bool:
        try:
            self.bot.send_message(chat_id=chat_id, text=message)
            return True
        except Exception as e:
            print(f"Telegram notification failed: {e}")
            return False