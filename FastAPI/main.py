from fastapi import FastAPI, HTTPException, Depends  # Depends: 의존성 주입(Dependency Injection) 기능.
from typing import Annotated  # 타입 힌트에 부가 정보를 첨부할 때 쓰는 문법입니다. FastAPI에서는 Depends와 함께 주로 사용돼요.
from sqlalchemy.orm import Session  # DB 작업 시 타입 힌트로 사용됩니다.
from pydantic import BaseModel  # 자동으로 JSON을 Python 객체로 변환하고 검증해줘요.
from database import SessionLocal, engine  # database.py에서 만든 DB 연결 도구들을 불러옵니다. SessionLocal: DB 세션을 생성하는 함수 | engine: 실제 DB 연결 객체
import models  # ORM 모델 정의 파일(models.py)을 불러옵니다. 
from fastapi.middleware.cors import CORSMiddleware  # CORS(Cross-Origin Resource Sharing) 관련 미들웨어를 추가하여
                                                    # React (http://localhost:3000) → FastAPI (http://localhost:8000)
                                                    # 서로 다른 도메인 간 요청을 브라우저가 막지 않도록 서버에서 허용 신호 줘야
                                                    # origin: 프로토콜 + 도메인 + 포트 번호 3개 모두 동일

app = FastAPI()
origins = [  # 화이트리스트 등록
	'http://localhost:3000'
]

app.add_middleware(  # 미들웨어(요청/응답 사이클에 공통 로직)를 fastapi 앱에 적용합니다.
	CORSMiddleware,
	allow_origins=origins
)

# 실제로는 다음 parameter를 위에 추가해야 
# 일부 요청(POST, OPTIONS 등)이 막히지 않고 정상 동작
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],


# Pydantic 모델 통한 JSON ↔ Python 객체 간 변환 및 데이터 검증 
# 결국 FastAPI가 JSON 잘 다룰 수 있게 해줌
class TransactionBase(BaseModel):  # 요청 검증용 Pydantic 스키마 모델  # 잘못된 타입 들어오면 442 응답으로 막음
	amount: float  # 초기값 없이 변수 선언 후 타입힌트까지 한 것
	category: str
	description: str
	is_income: bool
	date: str

class TransactionModel(TransactionBase):  # 응답 직렬화 용도 Pydantic 스키마 모델
	id: int
	class Config:
		orm_mode = True  # ORM 객체 Transaction의 필드 자동 추출할 수 있게 해줌
    # ↑ class Config는 데이터 필드가 아니라 “모델 동작 방식을 제어하는 설정 블록”이에요. JSON 구조의 키로 들어가지 않습니다.

def get_db():
	db = SessionLocal()  # DB 연결 세션을 하나 엽니다
	try:
		yield db  # 세션을 밖으로 전달(의존성 주입)
	finally:
		db.close()  # 함수 끝나면 세션 자동으로 닫아서 자원 낭비 방지
		
db_dependency = Annotated[Session, Depends(get_db)]  # endpoint가 실행될 떄 get_db()로 DB 세션 주입해줘
models.Base.metadata.create_all(bind=engine)  # DB에 테이블 없으면 자동 생성해주는 초기화 코드

@app.post("/transactions/", response_model=TransactionModel)  # ← 응답 직렬화 모델 지정 (DB에서 ORM 모델 반환할 때 해당 스키마 모델로 변환)
async def create_transaction(transaction: TransactionBase, db: db_dependency):  # transaction: TransactionBase → 요청 검증용 모델 지정 | db: db_dependency → 의존성 주입을 통해 얻은 DB 세션
					      # ↗ 클라이언트의 JSON body를 TransactionBase 타입으로 파싱 및 검증 후 transaction 변수에 담음 
						  # ↗ FastAPI는 인자 순서가 아닌 타입과 의존성 정보 보고 주입해줌
	db_transaction = models.Transaction(**transaction.model_dump())  # Transaction() 인스턴스는 DB 1개 레코드  # `dict` method is deprecated
	db.add(db_transaction)  
	db.commit()
	db.refresh(db_transaction)
	return db_transaction  # db_transaction은 SQLAlchemy ORM 객체예요. Transaction 클래스의 인스턴스.
	# ↑ @app.post(xxx, response_model=TransactionModel) 덕분에
	# 1️⃣ ORM 객체 → TransactionModel 변환 (orm_mode=True 덕분에 가능)
	# 2️⃣ TransactionModel → JSON 직렬화
	# 3️⃣ 최종적으로 클라이언트에게 ★ JSON으로 응답 전송 ★  

# 첨부. 
# Transaction() 인스턴스는 “1개의 실제 레코드
# row = Transaction(amount=1200.0, category="Food")
# db.add(row)

# 첨부.
# 다음과 같이 공통 필드 정의 / 요청 / 응답 모델 따로 정의 주로 함
# class UserBase(BaseModel):
#     email: str

# class UserCreate(UserBase):  # 요청(request)용
#     password: str

# class UserResponse(UserBase):  # 응답(response)용
#     id: int
#     class Config:
#         orm_mode = True
