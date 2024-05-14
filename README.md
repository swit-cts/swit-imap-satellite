# Swit 설치형 IMAP API 서버
## 1. 개요
Swit의 기본 IMAP 앱을 사용하는 고객들을 위해서 작성된 예제 입니다.
본 예제는 Naver IMAP을 기준으로 작성되었습니다.

## 2. 주요 Denpendency
* FastAPI
* SqlAlchemy
* Alembic
* imap-tools

## 3. 인증
* 기본적인 인증은 OAuth 2.0을 사용 합니다.
* 사용자의 실제 IMAP 이메일 인증정보를 사용 합니다.
* 이메일 인증정보는 암호화 되어 본 서버에 저장이 되며, 스윗으로는 인증 토큰만이 전송 됩니다.

## 설치
* .env 파일을 작성 합니다.
```dotenv
# 데이터베이스 접속 정보
DB_HOST={DBMS Host address} # DBMS의 호스트 주소
DB_NAME={DB Name}   # 데이터베이스 명
DB_USER={DBMS User ID} # DBMS 접속 사용자 아이디
DB_PASSWORD={DBMS Password} # DBMS 접속 사용자 비밀번호
DB_PORT={DBMS Port} # DBMS 사용 포트 (MySQL: 3306)

# Swagger-UI 접근 권한
SWAGGER_USERNAME={Swagger username} # Swagger-UI에 접근할 수 있는 사용자 명
SWAGGER_PASSWORD={Swagger password} # Swagger-UI에 접근할 수 있는 사용자 비밀번호

EMAIL_HOST=imap.naver.com # 본 예제는 네이버를 기준으로 만들어 졌습니다.
STORAGE_PATH={Upload path} # 첨부파일이 저장될 경로

# Token  발행을 위한 Secret key
JWT_SECRET_KEY={Access Token Secret Key} # Access Token을 발행하기 위한 Secret Key
JWT_REFRESH_SECRET_KEY={Refresh Token Secret Key} # Refresh Token을 발행하기 위한 Secret Key
```



## Alembic
* 데이터베이스 관리는 Alembic을 사용
```shell
alembic revision --autogenerate -m "message"
```