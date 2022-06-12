from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import ROOT_LOGGER
from app.logging import CustomLoggerAdapter
from app.db.crud import *
from app.db.models import *
from app.routers.api.models import *

router = APIRouter(
    prefix="/analysis-results"
)


@router.get("/{ar_id}", name='Получить результат анализа', response_model=PyAnalysisResult)
async def get_analysis_result(ar_id: int, db: Session = Depends(get_db)) -> AnalysisResult:
    """
    Делает запрос в БД на получение результата анализа по id
    """

    analysis_result = get_entry_by_id(ar_id, AnalysisResult, db)

    if analysis_result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return analysis_result
