from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from config import get_settings

import boto3
import json

settings = get_settings()
Base = declarative_base()
engine = create_engine(settings.SQLALCHEMY_DATABASE_URL,
                           connect_args={'client_encoding': 'utf8'})
Base.metadata.create_all(bind=engine)

def get_secret():
    """AWS Secrets Manager에서 데이터베이스 자격 증명 가져오기"""
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name='ap-northeast-2'  # 리전 설정
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId='marathon/db-credentials'  # Secrets Manager의 시크릿 이름
        )
    except Exception as e:
        raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret = json.loads(get_secret_value_response['SecretString'])
            return secret


def create_database():
    # 기본 postgres DB에 연결
    DEFAULT_DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/postgres"
    try:
        # 먼저 postgres DB에 연결
        engine = create_engine(DEFAULT_DATABASE_URL)
        with engine.connect() as conn:
            # 현재 트랜잭션 종료
            conn.execute(text("commit"))
            
            # DB 존재 여부 확인
            result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = 'marathon_db'"))
            if not result.fetchone():
                # DB 생성
                conn.execute(text("CREATE DATABASE marathon_db"))
                print("Database 'marathon_db' created successfully")
            else:
                print("Database 'marathon_db' already exists")
    except Exception as e:
        print(f"Error creating database: {e}")
        raise e
    finally:
        engine.dispose()


def init_tables():
    # marathon_db에 연결하는 엔진 생성
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
    try:
        # 테이블 생성
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise e
    finally:
        engine.dispose()


# Dependency
def get_db():
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL,
                           connect_args={'client_encoding': 'utf8'})
    
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()




