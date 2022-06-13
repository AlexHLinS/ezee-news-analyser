import requests
import htmldate
import date_guesser

from datetime import timedelta
from time import sleep
from urllib.parse import urlparse
from json import dumps
from datetime import datetime


from app.db.crud import *
from app.db.models import *
from app.helpers import default_logger
from core import get_article_text_and_title, start_analyze
from aux_tools import get_relative_urls, get_antiplag_uid, get_plagiary_percentage, get_grammatical_error_count


def get_urls_with_dates(urls: List[str]):
    urls_wd = []
    for url in urls:
        date = get_url_date_created(url)
        if date is not None:
            urls_wd.append({'url': url,
                            'date': date})
    return urls_wd


def get_url_date_created(url):
    try:
        response = requests.get(url, timeout=5)
    except Exception as e:
        return None

    try:
        html_date_result = htmldate.find_date(response.text)
    except Exception as e:
        return None

    try:
        response = requests.get(url, timeout=5)
        date_guesser_result = date_guesser.guess_date(url, response.text).date
    except Exception as e:
        return None

    if html_date_result is not None and date_guesser_result is not None:
        html_date_result = datetime.strptime(html_date_result, '%Y-%m-%d')
        return max(html_date_result.date(), date_guesser_result.date())
    return None


def analyze_document_useless(document: Document, logger=default_logger) -> None:
    """
    Таска на анализ документа. Предполагается, что должна запускаться через N секунд после инициализации проверки
    на антиплагиате

    Args:
        document: документ, который будет анализироваться
        ap_uuid: уникальный идентификатор, по которому можно получить результаты анализа с антиплагиата
        logger (optional): логгер для отслеживания процесса анализа
    """

    logger.info('Starting the analysis', doc_id=document.id, ar_id=document.ar_id)

    # TODO: Пока просто для примера. Вместо этого подставить реальный анализ
    from time import sleep
    from random import randint

    # Block1
    sleep(5)
    update_entry_by_id(document.ar_id, AnalysisResult(primary_source_url=True,
                                                      created_at=datetime.now(),
                                                      text='Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
                                                      source_score=0.5,
                                                      times_published=228,
                                                      percentage_blacklist=10.98,
                                                      source_text='Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?',
                                                      avg_sources_score=3.2,
                                                      reliable_sources_flag=True,
                                                      date_updated=datetime.now()))

    # Block2
    sleep(4)
    update_entry_by_id(document.ar_id, AnalysisResult(
        diagram_data=dumps(
            [{"date": datetime.now().replace(day=randint(1, 29)).strftime('%m/%d/%Y'), "is_valid": bool(randint(0, 1))}
             for i in range(228)]),
        date_updated=datetime.now()))
    # Block3
    sleep(3)
    update_entry_by_id(document.ar_id, AnalysisResult(plagiary_percentage=0.3,
                                                      is_any_sentiment_delta=True,
                                                      facts="Факты, факты, факты",
                                                      date_updated=datetime.now()))
    # Block4
    sleep(2)
    update_entry_by_id(document.ar_id, AnalysisResult(grammatic_errors_count=123,
                                                      spam_index=0.123,
                                                      water_index=0.56,
                                                      sentiment_index=0.98,
                                                      speech_index=0.12,
                                                      intuition_index=0.65,
                                                      clickbait_index=0.87,
                                                      rationality_index=0.54,
                                                      fake_index=0.78,
                                                      date_updated=datetime.now()))

    logger.info('Analysis has been finished', doc_id=document.id, ar_id=document.ar_id)

    return None


def analyze_document(document: Document, logger=default_logger):
    """
    Считаем times_published
    Заносим все остальные документы в базу (тот, что отправлен на анализ - должен иметь ar_id)
    По возможности вытягиваем для них текст и заголовок
    Считаем percentage_blacklist
    Считаем reliable_sources_flag
    Считаем diagram_data
    Считаем plagiary_percentage
    """

    logger.info('Starting the analysis')
    ap_uuid = get_antiplag_uid(document.text)
    logger.info('Successfully requested AP for text processing', ap_uuid=ap_uuid)

    db = next(get_db())

    timeout, delay = 90, 5
    start_time = datetime.now()
    while datetime.now() <= start_time + timedelta(seconds=timeout):
        try:
            relative_urls = get_relative_urls(ap_uuid, 0)
        except KeyError:
            logger.info(f"AP in progress. Delaying for {delay} seconds..")
            sleep(3)
            continue
        break
    else:
        logger.error('Timeout expired for waiting AP results, Source analysis is cancelled',
                     doc_id=document.id, ar_id=document.ar_id)
        return None

    # Если нет URL, то определяем его по наибольшему совпадению на АП
    if document.url is None:
        document.url = max(relative_urls, key=lambda x: x['plagiat']).get('url')
    update_entry_by_id(document.id, document)

    # определяем grammatic_errors_count
    try:
        count = get_grammatical_error_count(ap_uuid)
    except Exception as e:
        logger.warning('Exception raised during "grammatical_error_count"', exc=repr(e))
        count = None
    update_entry_by_id(document.ar_id, AnalysisResult(grammatical_error_count=count))

    # определяем plagiat_percentage
    try:
        plagiary_percentage = get_plagiary_percentage(ap_uuid, True)
    except Exception as e:
        plagiary_percentage = None
        logger.warning('plagiat_percentage could not be processed', exc=repr(e))
    update_entry_by_id(document.ar_id, AnalysisResult(plagiary_percentage=plagiary_percentage))

    urls = [ru.get('url') for ru in relative_urls]

    # считаем diagram_data
    url_with_dates = get_urls_with_dates(urls)
    diagram_data = dumps([{'date': datetime.strftime(uwd.get('date'), '%Y-%m-%d'),
                           'is_valid': None} for uwd in url_with_dates])
    update_entry_by_id(document.ar_id, AnalysisResult(diagram_data=diagram_data))

    # определяем primary_source_url, created_at, text
    primary_source = sorted(url_with_dates, key=lambda x: x['date'])[0] if len(url_with_dates) > 0 else None
    primary_source_url = primary_source.get('url') if primary_source is not None else None
    created_at = primary_source.get('date') if primary_source is not None else None
    update_entry_by_id(document.ar_id, AnalysisResult(primary_source_url=primary_source_url,
                                                      created_at=created_at))

    # Считаем times_published
    update_entry_by_id(document.ar_id, AnalysisResult(times_published=len(urls)))

    new_sources, new_documents = [], []
    primary_source_text, primary_source_title = None, None
    for url in urls:
        try:
            netloc = urlparse(url).netloc
        except Exception as e:
            netloc = None
            logger.warning('Exception raised during extraction of netloc', url=url, exc=repr(e))

        if netloc is not None:
            new_sources.append(Source(url=netloc))

        try:
            sth = get_article_text_and_title(url)
        except Exception as e:
            sth = None
            logger.warning('Exception raised during extraction of text and title', url=url, exc=repr(e))

        # определяем text для primary_source
        if sth is not None and url == primary_source_url:
            update_entry_by_id(document.ar_id, AnalysisResult(text=sth.text))
            primary_source_text = sth.text
            primary_source_title = sth.title

        new_documents.append(Document(url=url,
                                      text=sth.text if sth is not None else None,
                                      title=sth.title if sth is not None else None,
                                      s_id=new_sources[-1].id if netloc is not None else None,
                                      entity_uuid=document.entity_uuid))

    new_documents = add_entries(*new_documents)
    new_sources = add_entries(*new_sources)

    # определяем sentiment_index, facts
    analysis_result = get_entry_by_id(document.ar_id, AnalysisResult)
    some_metrics = {}
    if primary_source_text and primary_source_title and document.text:
        try:
            some_metrics = start_analyze(document.id, primary_source_text, primary_source_title)
        except Exception as e:
            logger.warning("Exception raised during 'start_analyze'", exc=repr(e))

    update_entry_by_id(document.ar_id, AnalysisResult(sentiment_index=some_metrics.get('sentiment_index'),
                                                      facts=some_metrics.get('facts')))

    # Считаем percentage_blacklist
    if len(new_sources) > 0:
        blacklisted = db.query(BlacklistedSource
                               ).filter(BlacklistedSource.url in [ns.url for ns in new_sources]
                                        ).all()
        percentage_blacklist = len(blacklisted) / len(new_sources)
    else:
        percentage_blacklist = None

    update_entry_by_id(document.ar_id, AnalysisResult(percentage_blacklist=percentage_blacklist))
    logger.info('Analysis has been finished')
    return

