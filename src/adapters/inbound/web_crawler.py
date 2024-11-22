from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple

from src.ports.inbound import WebCrawlerPort

class BaseMarathonInfoFilter:
    def filter(self, marathon_list: List[Dict]) -> List[Dict]:
        return marathon_list

class MarathonInfoWeeklyFilter(BaseMarathonInfoFilter):
    def filter(self, marathon: Dict) -> Dict | None:
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
        week_end = week_start + timedelta(days=6)
        week_end = week_end.replace(hour=23, minute=59, second=59, microsecond=999999)

        if week_start <= marathon['race_date'] <= week_end:
            return marathon
        elif marathon['registration_start_date'] <= today and marathon['registration_end_date'] >= today:
            return marathon

        return

class RoadRunWebCrawler(WebCrawlerPort):

    def __init__(self, marathon_filter: BaseMarathonInfoFilter):
        self.marathon_filter = marathon_filter

    def crawl(self, url: str) -> List[Dict]:
        try:
            response = requests.get(url)
            response.encoding = 'euc-kr'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            marathon_list = []
            rows = soup.find_all('tr')
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    date_cell = cols[0].find('font', size="4")
                    title_cell = cols[1].find('a')
                    
                    if date_cell and title_cell and date_cell.text.strip() and title_cell.text.strip():
                        if re.match(r'\d', date_cell.text.strip()):
                            marathon_info = self._parse_marathon_info(cols)
                            filtered_marathon_info = self.marathon_filter.filter(marathon_info)
                            if filtered_marathon_info:
                                marathon_list.append(filtered_marathon_info)
                                
            
            return marathon_list
            
        except Exception as e:
            print(f"Error crawling marathon schedule: {str(e)}")
            return []

    def preprocess_data(self, marathon: Dict) -> Dict:
        marathon_info = {}
        for key, value in marathon.items():
            if key == 'title':
                marathon_info['title'] = value
            elif key == 'location':
                marathon_info['location'] = value
            elif key == 'homepage':
                marathon_info['homepage'] = value
            elif key == 'courses':
                marathon_info['courses'] = value
            elif key == 'organizer':
                marathon_info['organization_name'] = value
            elif key == 'registration_period':
                registration_start_date, registration_end_date = map(
                    lambda x: datetime.strptime(x.strip(), '%Y년%m월%d일'),
                    value.split('~')
                )
                marathon_info['registration_start_date'] = registration_start_date
                marathon_info['registration_end_date'] = registration_end_date
            elif key == 'event_datetime':
                date, start_time = value.split(' 출발시간:')
                date = datetime.strptime(date.strip(), '%Y년%m월%d일')
                start_time = self._parse_race_time(start_time)
                race_time = datetime.combine(date, start_time)
                marathon_info['race_date'] = race_time
        return marathon_info

    def _parse_marathon_info(self, cols: List) -> Optional[Dict]:
        try:
            date_font = cols[0].find('font', size="4")
            date_cell = date_font.text if date_font else ""
            
            day_font = cols[0].find('font', color="#959595")
            day_of_week = day_font.text.strip('()') if day_font else ""
            
            title_link = cols[1].find('a')
            title = title_link.text if title_link else ""
            detail_url = title_link['href'] if title_link else ""
            
            course_font = cols[1].find('font', color="#990000")
            courses = course_font.text.split(',') if course_font else []
            courses = [course.strip() for course in courses]
            
            location = cols[2].text.strip() if cols[2] else ""
            
            organizer_text = cols[3].text.split('☎') if cols[3] else ["", ""]
            organizer = organizer_text[0].strip()
            contact = organizer_text[1].strip().split()[0] if len(organizer_text) > 1 else ""
            
            homepage = None
            homepage_link = cols[3].find('a', href=True)
            if homepage_link and homepage_link.find('img') and 'home.gif' in homepage_link.find('img')['src']:
                homepage = homepage_link['href']
            
            registration_period, event_datetime = self._get_detail_info(detail_url)
            
            return {
                'date': date_cell,
                'day_of_week': day_of_week,
                'title': title,
                'courses': courses,
                'location': location,
                'organizer': organizer,
                'contact': contact,
                'homepage': homepage,
                'detail_url': detail_url,
                'registration_period': registration_period,
                'event_datetime': event_datetime
            }
        except Exception as e:
            print(f"Error parsing marathon info: {str(e)}")
            return None

    def _get_detail_info(self, detail_url: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            real_url = self._convert_js_url_to_real_url(detail_url)
            if not real_url:
                return None, None
            
            response = requests.get(real_url)
            response.encoding = 'euc-kr'
            html_content = response.text.encode('utf-8', errors='ignore').decode('utf-8')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            registration_period = None
            event_datetime = None
            
            table = soup.find('table')
            if table:
                for row in table.find_all('tr'):
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        label = cols[0].text.strip()
                        value = cols[1].text.strip()
                        
                        if '접수기간' in label:
                            registration_period = value
                        elif '대회일시' in label:
                            event_datetime = value
            
            return registration_period, event_datetime
        except Exception as e:
            print(f"Error fetching detail info: {str(e)}")
            return None, None

    def _convert_js_url_to_real_url(self, js_url: str) -> Optional[str]:
        match = re.search(r"'(view\.php\?no=\d+)'", js_url)
        if match:
            return f"http://www.roadrun.co.kr/schedule/{match.group(1)}"
        return None

    def _parse_race_time(self, time_str: str) -> time:
        time_str = time_str.replace("출발시간:", "").replace("출발", "").replace(';', ':').strip()
        try:
            if time_str.isdigit():
                if len(time_str) == 4:
                    hour = int(time_str[:2])
                    minute = int(time_str[2:])
                    return time(hour, minute)
                else:
                    hour = int(time_str)
                    return time(hour, 0)
            if ':' in time_str:
                hour, minute = map(int, re.findall(r'\d+', time_str)[:2])
                if hour == 24:
                    hour = 0
                return time(hour, minute)
            
            hour_match = re.search(r'(\d+)시', time_str)
            hour = int(hour_match.group(1))

            minute_match = re.search(r'(\d+)분', time_str)
            minute = int(minute_match.group(1)) if minute_match else 0

            is_pm = '오후' in time_str
            if is_pm and hour != 12:
                hour += 12

            return time(hour, minute)

        except Exception as e:
            print(f'시간 파싱 에러: {str(e)}, 입력값: {time_str}')
            return time(0, 0) 