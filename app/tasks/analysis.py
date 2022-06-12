from app.db.crud import *
from app.db.models import AnalysisResult
from app.helpers import default_logger


def analyze_document(document: Document, logger=default_logger) -> None:
    """
    Таска на анализ документа

    Проводит анализ документа и
    """

    logger.info('Starting the analysis', doc_id=document.id, ar_id=document.ar_id)

    # TODO: Пока просто для примера. Вместо этого подставить реальный анализ
    from time import sleep
    sleep(5)
    update_entry_by_id(document.ar_id, AnalysisResult(is_organisation_real=True))
    sleep(5)
    update_entry_by_id(document.ar_id, AnalysisResult(author_rate=0.5))
    sleep(5)
    update_entry_by_id(document.ar_id, AnalysisResult(mistakes_count=4))

    logger.info('Analysis has been finished', doc_id=document.id, ar_id=document.ar_id)

    return None


