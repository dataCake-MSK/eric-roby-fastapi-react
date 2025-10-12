## SQLAlchemy ORM 모델 정의 코드
from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Float

## table 1개의 1개 record에 대한 ORM 모델을 정의합니다.
class Transaction(Base):  # Base(declarative_base() 생성)를 상속하면 SQLAlchemy가 ORM 모델 클래스로 인식합니다.
	__tablename__ = 'transactions'  # 클래스가 대응할 테이블 이름입니다.

	id = Column(Integer, primary_key=True, index=True)  # DB 테이블의 id 열 정의 | index=True: 검색 속도 향상을 위해 인덱스 생성
	amount = Column(Float)  # 거래 금액을 저장하는 amount 열은 Float 자료형 사용합니다.
	category = Column(String)
	description = Column(String(255))
	is_income = Column(Boolean)
	date = Column(String)


# 이 모델을 DB에 반영하려면 다음 코드를 실행합니다 👇
# from database import engine
# Base.metadata.create_all(bind=engine)

# 그러면 SQLite 파일(finance.db) 안에
# transactions 테이블이 자동으로 생성됩니다.