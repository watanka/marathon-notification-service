from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime
from src.domain.models import MarathonInfo

class WebCrawlerPort(ABC):
    @abstractmethod
    def crawl(self, url: str) -> List[Dict]:
        """웹 크롤링을 수행하고 마라톤 정보 목록을 반환"""
        pass

    @abstractmethod
    def preprocess_data(self, marathon_data: Dict) -> Dict:
        """크롤링된 데이터를 도메인 모델에 맞게 전처리"""
        pass


class AddressManagerPort(ABC):
    @abstractmethod
    def load_address(self) -> List[Dict]:
        pass

class ControllerPort(ABC):
    @abstractmethod
    def get_marathon_info(self, marathon_data: Dict) -> List[MarathonInfo]:
        pass
