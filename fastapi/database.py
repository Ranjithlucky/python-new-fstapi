from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor
import time

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://<username>:<password>@<ipaddress/hostname>/<database>"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgress@localhost/fastapi"

# sql database
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:db.close()

while True:
    try:
        conn=psycopg2.connect(host='localhost',database='fastapi',user='postgres',password='postgress',cursor_factory=RealDictCursor)
        cursor=conn.cursor()
        print("Database connected successfully")
        break
    except Exception as error:
        print("Connection has been failed")
        print("error:",error)
        time.sleep(2)
