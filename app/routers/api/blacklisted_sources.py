from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import ROOT_LOGGER
from app.logging import CustomLoggerAdapter
from app.db.crud import *
from app.db.models import *
from app.routers.api.models import *


router = APIRouter(
    prefix="/blacklisted-sources"
)


@router.get("/{bsource_id}", name='Получить заблокированный источник', response_model=PyBlacklistedSource)
async def get_source(bsource_id: int, db: Session = Depends(get_db)) -> PyBlacklistedSource:
    """
    Делает запрос в БД на получение заблокированного источника по id
    """

    bsource = get_entry_by_id(bsource_id, BlacklistedSource, db)

    if bsource_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return bsource


@router.post("/", name='Создать заблокированный источник', response_model=PyBlacklistedSource)
async def add_blacklisted_source(new_bsource: NewPyBlacklistedSource,
                                 db: Session = Depends(get_db)) -> PyBlacklistedSource:
    """
    Создает запись заблокированного источника в БД
    """

    logger = CustomLoggerAdapter(ROOT_LOGGER, extra={'req_uuid': uuid4(), 'method': 'POST api/sources'})

    if new_bsource.url is not None:
        maybe_existing_source = db.query(BlacklistedSource
                                         ).filter(BlacklistedSource.url == new_bsource.url
                                                  ).first()
        if maybe_existing_source is not None:
            logger.info('Source already exists')
            return maybe_existing_source

    if new_bsource.ipv4 is not None:
        maybe_existing_source = db.query(BlacklistedSource
                                         ).filter(BlacklistedSource.ipv4 == new_bsource.ipv4
                                                  ).first()
        if maybe_existing_source is not None:
            logger.info('Source already exists')
            return maybe_existing_source

    if new_bsource.ipv6 is not None:
        maybe_existing_source = db.query(BlacklistedSource
                                         ).filter(BlacklistedSource.ipv6 == new_bsource.ipv6
                                                  ).first()
        if maybe_existing_source is not None:
            logger.info('Source already exists')
            return maybe_existing_source

    bsource = add_entries(BlacklistedSource(url=new_bsource.url, ipv4=new_bsource.ipv4, ipv6=new_bsource.ipv6), db=db)

    return bsource