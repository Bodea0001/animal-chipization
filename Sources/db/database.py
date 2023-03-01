import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


POSTGRESQL_CONFIG = os.environ["POSTGRESQL_CONFIG"]

engine = create_engine(POSTGRESQL_CONFIG, echo=True, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)