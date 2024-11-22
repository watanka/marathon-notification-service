from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class Recipient(BaseModel):
    name: str
    phone_number: str
    

class Course(BaseModel):
    distance: float
    name: str
    description: str | None = ''

    class Config:
        from_attributes = True

class Region(str, Enum):
    SEOUL = "서울"
    GYEONGGI = "경기"
    INCHEON = "인천"
    GANGWON = "강원"
    CHUNGBUK = "충북"
    CHUNGNAM = "충남"
    DAEJEON = "대전"
    JEONBUK = "전북"
    JEONNAM = "전남"
    GWANGJU = "광주"
    GYEONGBUK = "경북"
    DAEGU = "대구"
    GYEONGNAM = "경남"
    BUSAN = "부산"
    ULSAN = "울산"
    JEJU = "제주"
    OVERSEAS = "해외"
    OTHER = "기타"
    
class MarathonInfo(BaseModel):
    title: str
    race_date: datetime
    location: str
    courses: list[int] = Field(default_factory=list)
    homepage: str
    organization_name: str
    registration_start_date: datetime
    registration_end_date: datetime
    
    class Config:
        from_attributes = True

    @property
    def in_registration_period(self):
        return self.registration_start_date <= datetime.now() and self.registration_end_date >= datetime.now()