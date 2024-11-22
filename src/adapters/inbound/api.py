from fastapi import APIRouter,FastAPI, Query
from datetime import datetime

from src.infrastructure.uow import SqlAlchemyUnitOfWork
from src.domain.models import MarathonInfo
from src.ports.inbound import ControllerPort
from src.application.services import MarathonService


class MarathonController(ControllerPort):
    def __init__(self, marathon_service: MarathonService):
        self.marathon_service = marathon_service
        self.router = APIRouter(prefix="/api/v1")
        self.setup_routes()


    def setup_routes(self):
        self.router.add_api_route(
            "/healthcheck",
            self.health_check,
            methods=["GET"]
        )
        self.router.add_api_route(
            "/marathon",
            self.get_marathon_info,
            methods=["GET"],
            response_model=list[MarathonInfo]
        )
        self.router.add_api_route(
            "/marathon/open-registration",
            self.get_marathon_open_registration,
            methods=["GET"],
            response_model=list[MarathonInfo]
        )
        self.router.add_api_route(
            "/marathon/this-month",
            self.get_marathon_this_month,
            methods=["GET"],
            response_model=list[MarathonInfo]
        )

    async def health_check(self):
        return {"message": "healthy!"}
    
    async def get_marathon_info(
        self,
        registration_status: bool = Query(None, description="접수 기간 체크"),
        region: str = Query(None, description="지역 조회"),
        course: int = Query(None, description="코스 조회"),
        race_search_start_date: datetime = Query(None, description="마라톤 날짜 탐색 범위(시작)"),
        race_search_end_date: datetime = Query(None, description="마라톤 날짜 탐색 범위(끝)"),
    ):
        
        marathon_list = self.marathon_service.get_marathon_info(
            registration_status, 
            region, 
            course, 
            race_search_start_date, 
            race_search_end_date
        )
        return [MarathonInfo.model_validate(marathon) for marathon in marathon_list]

    
    async def get_marathon_open_registration(self):
        marathon_list = self.marathon_service.get_marathon_open_registration()
        return [MarathonInfo.model_validate(marathon) for marathon in marathon_list]

    async def get_marathon_this_month(self):
        marathon_list = self.marathon_service.get_marathon_this_month()
        return [MarathonInfo.model_validate(marathon) for marathon in marathon_list]
