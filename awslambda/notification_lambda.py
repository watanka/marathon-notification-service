import json
from src.application.services import MarathonService, RecipientService
from src.application.notification_service import NotificationService
from src.infrastructure.database import create_database, init_tables
from src.infrastructure.uow import SqlAlchemyUnitOfWork
from src.adapters.outbound.notifications import (
    TwilioNotificationAdapter,
    TelegramNotificationAdapter
)
from src.infrastructure.models import RecipientDB
from src.adapters.inbound.address_manager import GoogleSpreadSheetAddressManager
from src.adapters.inbound.web_crawler import RoadRunWebCrawler, MarathonInfoWeeklyFilter
from config import get_settings
import logging

logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    settings = get_settings()
    
    create_database()
    init_tables()
    # 데이터베이스 세션 생성
    uow = SqlAlchemyUnitOfWork()
    marathon_service = MarathonService(uow)
    recipient_service = RecipientService(uow)
    url = "http://www.roadrun.co.kr/schedule/list.php"
    
    marathon_filter = MarathonInfoWeeklyFilter()
    crawler =  RoadRunWebCrawler(marathon_filter)
    marathon_list = crawler.crawl(url)

    for marathon in marathon_list:
        marathon = crawler.preprocess_data(marathon)
        marathon_service.save_marathon_info(uow, marathon)

    # 알림 서비스 설정
    twilio_adapter = TwilioNotificationAdapter(
        account_sid=settings.TWILIO_ACCOUNT_SID,
        auth_token=settings.TWILIO_AUTH_TOKEN,
        from_number=settings.TWILIO_FROM_NUMBER
    )
    
    # telegram_adapter = TelegramNotificationAdapter(
    #     bot_token=settings.TELEGRAM_BOT_TOKEN
    # )
    
    notification_service = NotificationService([twilio_adapter])

    address_manager = GoogleSpreadSheetAddressManager()
    recipients = address_manager.load_address()
    logger.info(f"Recipients: {recipients}")
    for recipient in recipients:
        recipient_service.save_recipient(RecipientDB.from_dict(recipient))
    
    marathon_list = marathon_service.get_marathon_open_registration()
    notification_service.notify_new_marathon('이번주 마라톤 접수일정입니다', marathon_list, recipients)
    # 웹 크롤링 실행
    
    return {
        'statusCode': 200,
        'body': json.dumps('Marathon data processed successfully')
    }