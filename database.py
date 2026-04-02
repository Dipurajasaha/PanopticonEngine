from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


SQLALCHEMY_DATABASE_URL = "sqlite:///./panopticon.db"

# -- connection to the database --
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# -- session maker for database interactions --
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -- base class for ORM models --
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        