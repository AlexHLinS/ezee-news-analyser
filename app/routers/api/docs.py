from uuid import uuid4

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session

from app import ROOT_LOGGER
from app.logging import CustomLoggerAdapter
from app.db.crud import *
from app.db.models import *
from app.routers.api.models import *
from app.tasks.analysis import analyze_document
from core import get_article_text_and_title

router = APIRouter(
    prefix="/docs"
)


@router.get("/{doc_id}", name='Получить документ', response_model=PyDocument)
async def get_document(doc_id: int, db: Session = Depends(get_db)) -> Document:
    """
    Делает запрос в БД на получение документа по id
    """

    document = get_entry_by_id(doc_id, Document, db)

    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return document


@router.post("/", name='Отправить документ на анализ', response_model=PyDocument)
async def add_document(new_doc: NewPyDocument,
                       background_tasks: BackgroundTasks,
                       db: Session = Depends(get_db)) -> Document:
    """
    Создаёт новый документ в БД и отправляет его на анализ

    - **new_doc**: Новый документ для анализа
    """
    logger = CustomLoggerAdapter(ROOT_LOGGER, extra={'req_uuid': uuid4(), 'method': 'POST api/docs'})

    if new_doc.url is None:
        url, title, text = None, new_doc.title, new_doc.text
    else:
        document = db.query(Document
                            ).filter(Document.url == new_doc.url
                                     ).first()
        if document is not None:
            logger.info('Document already exists')
            return document
        sth = get_article_text_and_title(new_doc.url)
        url, title, text = new_doc.url, sth.title, sth.text

    logger.info('Inserting an entry into "analysis_results"')
    analysis_result = AnalysisResult()
    add_entries(analysis_result, db=db)

    logger.info('Inserting an entry into "docs"')
    document = Document(url=url,
                        title=title,
                        text=text,
                        ar_id=analysis_result.id,
                        entity_uuid=str(uuid4()))
    add_entries(document, db=db)

    background_tasks.add_task(analyze_document,
                              document=document,
                              logger=logger)

    return document


@router.get("/{doc_id}/analyze-sources",
            name='Провести анализ источников документа',
            response_model=PySourcesAnalysisResult)
async def analyze_sources(doc_id: int, db: Session = Depends(get_db)) -> PySourcesAnalysisResult:
    """
    Проводит анализ источников, которые публиковали документ и ему подобные
    """
    logger = CustomLoggerAdapter(ROOT_LOGGER, extra={'req_uuid': uuid4(),
                                                     'method': f'GET api/docs/{doc_id}/analyze-sources'})

    document = get_entry_by_id(doc_id, Document, db)

    if document is None:
        logger.info('Document not found', doc_id=doc_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if document.entity_uuid is None:
        logger.info('entity_uuid is not provided for the document', doc_id=doc_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    related_documents = db.query(Document, Source
                                 ).filter(Document.entity_uuid == document.entity_uuid
                                          ).order_by(Document.date_updated.desc()).all()

    sources = db.query(Source
                       ).filter(Source.id in [rd.s_id for rd in related_documents]
                                ).all()

    if len(sources) > 0:
        good_media_percentage = len([s for s in sources if s.score is not None and s.score > 8]) / len(sources)
        media_avg_score = sum([s for s in sources if s.score is not None]) / len(sources)
    else:
        good_media_percentage, media_avg_score = None, None
    return PySourcesAnalysisResult(sources=sources,
                                   good_media_percentage=good_media_percentage,
                                   media_avg_score=media_avg_score)
