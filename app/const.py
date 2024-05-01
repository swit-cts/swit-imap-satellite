import os
from dotenv import load_dotenv


class Const:
    """
    상수 관리
    """

    env = os.getenv('ENV', 'dev')

    load_dotenv(f".env.{env}")

    DB_URL = f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"

    # Swagger-UI Auth
    SWAGGER_USERNAME = os.getenv("SWAGGER_USERNAME")
    SWAGGER_PASSWORD = os.getenv("SWAGGER_PASSWORD")

    #Environment
    ENV = os.getenv("ENV")
    EMAIL_HOST = os.getenv("EMAIL_HOST")
    STORAGE_PATH = os.getenv("STORAGE_PATH")

    # Security!!!
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")


const = Const()
