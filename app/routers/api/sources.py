from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import ROOT_LOGGER
from app.logging import CustomLoggerAdapter
from app.db.crud import *
from app.db.models import *
from app.routers.api.models import *


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
