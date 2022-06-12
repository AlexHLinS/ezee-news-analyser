from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import ROOT_LOGGER
from app.logging import CustomLoggerAdapter
from app.db.crud import *
from app.db.models import *
from app.routers.api.models import *
from app.library.sources_analysis.library import *


router = APIRouter(
    prefix="/sources"
)


@router.get("/{source_id}", name='Получить источник', response_model=PySource)
async def get_source(source_id: int, db: Session = Depends(get_db)) -> PySource:
    """
    Делает запрос в БД на получение источника по id
    """

    source = get_entry_by_id(source_id, Source, db)

    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return source


@router.post("/", name='Разместить новый источник', response_model=PySource)
async def add_source(new_source: NewPySource, db: Session = Depends(get_db)) -> PySource:
    """
    Создает запись нового источника в БД
    """

    logger = CustomLoggerAdapter(ROOT_LOGGER, extra={'req_uuid': uuid4(), 'method': 'POST api/sources'})

    if new_source.url is not None:
        maybe_existing_source = db.query(Source
                                         ).filter(Source.url == new_source.url
                                                  ).first()
        if maybe_existing_source is not None:
            logger.info('Source already exists')
            return maybe_existing_source

    source = Source(url=new_source.url)

    # Получаем IP адрес
    source.ipv4 = get_ip_by_url(new_source.url)

    # Проверяем, есть ли в списке заблокированных
    logger.info('Checking blacklists')
    source.blacklisted = False
    for entry in db.query(BlacklistedSource).all():
        try:
            match = urls_are_same(new_source.url, entry.url)
        except Exception as e:
            logger.error(f'Exception raised', exc=repr(e))
            match = False

        if match or source.ipv4 == entry.ipv4:
            source.blacklisted = True
            break

    # Получаем дату истечения срока действия сертификата
    logger.info('Checking cert expiration date')
    try:
        source.cert_expires_at = get_url_certificate_expiration_date(new_source.url)
    except Exception as e:
        logger.error(f'Exception raised', exc=repr(e))
        pass

    # Получаем инфо об организации и дате создания источника
    logger.info('Checking info about organization')
    try:
        source.org = get_url_information(new_source.url).get('org')
        source.created_at = get_url_information(new_source.url).get('creation_date')
    except Exception as e:
        logger.error(f'Exception raised', exc=repr(e))
        pass

    # TODO: Рассчитываем скор источника
    logger.info('Checking score')
    try:
        source.score = None
    except Exception as e:
        logger.error(f'Exception raised', exc=repr(e))
        pass

    # TODO: Определяем принадлежность государству
    logger.info('Checking if government\'s source')
    try:
        source.government = None
    except Exception as e:
        logger.error(f'Exception raised', exc=repr(e))
        pass

    # TODO: Определяем посещаемость
    logger.info('Checking traffic')
    try:
        source.traffic = None
    except Exception as e:
        logger.error(f'Exception raised', exc=repr(e))
        pass

    source = add_entries(source, db=db)

    return source
