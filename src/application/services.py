from src.domain.models import MarathonInfo
from src.infrastructure.models import MarathonInfoDB, RecipientDB
from src.application.uow import AbstractUnitOfWork
from sqlalchemy.orm import Session
from datetime import datetime
import calendar

class MarathonService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
    
    def save_marathon_info(self, marathon: MarathonInfoDB):
        with self.uow as uow:
            existing_marathon = uow.marathon_repository.get_by_title_race_date(marathon.title, 
                                                                               marathon.race_date, 
                                                                               )
            if not existing_marathon:
                uow.marathon_repository.save(marathon)
                uow.commit()

    def get_marathon_info(self, 
                          registration_status: bool = None,
                          region: str = None, 
                          course: int = None, 
                          race_search_start_date: datetime = None, 
                          race_search_end_date: datetime = None):

        with self.uow as uow:
            
            marathon_list: list[MarathonInfoDB] = uow.marathon_repository.get_marathons(
                registration_status=registration_status,
            region = region,
            course = course,
            race_search_start_date = race_search_start_date,
            race_search_end_date = race_search_end_date,
            )
            marathon_list = [marathon.to_pydantic() for marathon in marathon_list]

        return marathon_list
    
    def get_marathon_open_registration(self):
        with self.uow as uow:
            marathon_list: list[MarathonInfoDB] = uow.marathon_repository.get_by_registration_period(datetime.now())
            marathon_list = [marathon.to_pydantic() for marathon in marathon_list]
        return marathon_list

    def get_marathon_this_month(self, 
                        registration_status: bool = None,
                        region: str = None, 
                        course: int = None):
        # 이번 달에 열리는 마라톤 대회 정보 조회
        with self.uow as uow:
            now = datetime.now()
            current_year = now.year
            current_month = now.month
            _, last_day = calendar.monthrange(current_year, current_month)
            month_end = datetime(current_year, current_month, last_day, 23, 59, 59)

            marathon_list: list[MarathonInfoDB] = uow.marathon_repository.get_marathons(
                registration_status=registration_status,
                region = region,
                course = course,
                race_search_start_date = datetime(current_year, current_month, 1, 0, 0, 0),
                race_search_end_date = month_end,
                )
            marathon_list = [marathon.to_pydantic() for marathon in marathon_list]

        return marathon_list
    

class RecipientService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    def save_recipient(self, recipient: RecipientDB):
        with self.uow as uow:
            uow.recipient_repository.save(recipient)
            uow.commit()

    def get_recipients(self):
        with self.uow as uow:
            recipients = uow.recipient_repository.get_all()
            recipients = [recipient.to_pydantic() for recipient in recipients]
        return recipients
