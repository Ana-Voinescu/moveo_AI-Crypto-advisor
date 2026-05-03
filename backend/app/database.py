import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

# SQLite requires check_same_thread=False when used in a multi-threaded server
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Each request to the API will open one session and close it when done
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All model classes inherit from Base so SQLAlchemy can map them to tables
Base = declarative_base()
