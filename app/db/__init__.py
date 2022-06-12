import configparser


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Чтение конфига
config = configparser.RawConfigParser()
config.read('config.ini')

engine = create_engine(config['DB']['SQLALCHEMY_DATABASE_URL'], connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

