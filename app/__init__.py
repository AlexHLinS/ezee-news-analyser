import configparser

from app import db

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .logging import get_root_logger, CustomLoggerAdapter

# Чтение конфига
config = configparser.RawConfigParser()
config.read('./config.ini')

# Создание инстанса приложения
app = FastAPI(openapi_url="/api/openapi.json")
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:8080'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

db.Base.metadata.create_all(bind=db.engine)

# Создание логгера
ROOT_LOGGER = get_root_logger(config['LOGGING']['FORMAT'],
                              config['LOGGING']['LEVEL'],
                              config['LOGGING']['LOG_FILE'])

# Routers
from .routers import api
app.include_router(api.api_router)