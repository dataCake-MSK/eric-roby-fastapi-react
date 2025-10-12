## database(sqlite)와 fastapi 연결
## 이 코드는 SQLAlchemy(ORM 라이브러리)를 사용해서 SQLite(가벼운 파일 기반 DB) 연결과 ORM 설정을 하는 기본 코드예요.
## (ORM은 Object Relational Mapping, 즉 객체로 DB를 다루는 기술이에요.)
## 이 코드는 "SQLite 데이터베이스 파일(finance.db)을 만들고, SQLAlchemy가 그걸 사용할 수 있게 준비해요."

from sqlalchemy import create_engine  # sqlalchemy 핵심 도구
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

URL_DATABASE = 'sqlite:///./finance.db'  # 현재 폴더(./)에 finance라는 db 저장해요.
# ↓ DB와 연결을 만듭니다. engine은 DB 엔진 객체로, SQLAlchemy가 DB에 접근할 때 항상 이걸 사용해요. connect_args는 SQLite 전용 설정이에요.
engine = create_engine(URL_DATABASE, connect_args={"check_same_thread": False})  
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # 세션(데이터베이스와 대화하는 객체) 생성기
Base = declarative_base()  # 모든 ORM 모델 클래스의 부모(Base) 가 되는 객체이에요.

# **엔진(engine)**이 “DB와의 물리적 연결”이라면,
# **세션(Session)**은 그 위에서 실제 “쿼리(질문)”를 주고받는 논리적 연결이에요.