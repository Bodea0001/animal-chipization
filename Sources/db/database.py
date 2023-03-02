from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.config import POSTGRESQL_CONFIG


engine = create_engine(POSTGRESQL_CONFIG, echo=True, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)