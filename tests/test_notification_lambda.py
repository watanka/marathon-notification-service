import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from awslambda.notification_lambda import lambda_handler
from src.infrastructure.models import MarathonInfoDB

@pytest.mark.skip
@patch('awslambda.notification_lambda.get_db')
@patch('awslambda.notification_lambda.MarathonService')
def test_notification_lambda_with_mocks(mock_marathon_service, mock_get_db):
    # 모의 데이터베이스 세션 설정
    mock_db = MagicMock()
    mock_get_db.return_value = iter([mock_db])
    
    # 모의 마라톤 서비스 설정
    mock_marathon_service.return_value.get_marathon_info.return_value = [
        MarathonInfoDB.from_dict(data={
            'title': '테스트 마라톤',
            'race_date': datetime.now(),
            'location': '서울',
        })
    ]
    
    # 테스트 실행
    result = lambda_handler({}, None)
    
    # 결과 확인
    assert result['statusCode'] == 200