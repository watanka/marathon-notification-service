from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 스코프 설정
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1Pjuh7x_QxImluPDoJaa47be10tbq6YDaCtogrsU5_80"
RANGE_NAME = "response_sheet"

def main():
    """Shows basic usage of the Sheets API."""
    try:
        # 서비스 계정 인증 정보 로드
        credentials = service_account.Credentials.from_service_account_file(
            "credentials.json",  # 서비스 계정 키 파일
            scopes=SCOPES
        )

        # Sheets API 클라이언트 생성
        service = build("sheets", "v4", credentials=credentials)
        sheet = service.spreadsheets()
        
        result = (
            sheet.values()
            .get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return

        print("Name, Major:")
        for row in values:
            timestamp_str, name, courses, phone_number = row
            phone_number = preprocess_phone_number(phone_number)
            print(timestamp_str, name, courses, phone_number)
            
    except HttpError as err:
        print(err)

def preprocess_phone_number(phone_number: str) -> str:
    return '+82' + phone_number.replace("-", "")[1:]

if __name__ == "__main__":
    main()