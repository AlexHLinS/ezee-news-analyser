import requests
import htmldate
import date_guesser

from datetime import timedelta, datetime
from time import sleep
from urllib.parse import urlparse
from json import dumps
from traceback import format_exc

from app.db.crud import *
from app.db.models import *
from app.helpers import default_logger
from core import get_article_text_and_title, start_analyze, calculate_final_fake_score
from aux_tools import get_relative_urls, get_antiplag_uid, get_grammatical_error_count, get_spam_percent, get_plagiary_percentage


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


def analyze_document(document: Document, logger=default_logger):
    """
    Осуществляет анализ документа

    Args:
        document: документ, по которому проводится анализ
        logger: логгер
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
        grammatic_errors_count = get_grammatical_error_count(ap_uuid)
    except Exception as e:
        logger.warning('Exception raised during "grammatical_errors_count"', exc=repr(e))
        grammatic_errors_count = None
    update_entry_by_id(document.ar_id, AnalysisResult(grammatic_errors_count=grammatic_errors_count))

    # определяем spam_index
    try:
        spam_index = get_spam_percent(ap_uuid)
    except Exception as e:
        logger.warning('Exception raised during "spam_index"', exc=repr(e))
        spam_index = None
    update_entry_by_id(document.ar_id, AnalysisResult(spam_index=spam_index))

    # определяем get_water_from
    try:
        spam_index = get_spam_percent(ap_uuid)
    except Exception as e:
        logger.warning('Exception raised during "spam_index"', exc=repr(e))
        spam_index = None
    update_entry_by_id(document.ar_id, AnalysisResult(spam_index=spam_index))

    try:
        grammatic_errors_count = get_grammatical_error_count(ap_uuid)
    except Exception as e:
        logger.warning('Exception raised during "grammatical_errors_count"', exc=repr(e))
        grammatic_errors_count = None
    update_entry_by_id(document.ar_id, AnalysisResult(grammatic_errors_count=grammatic_errors_count))

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
            water_index = some_metrics.get("water_index", 1)
            sentiment_index = some_metrics.get("sentiment_index", 0)
            facts = some_metrics.get("facts")
            error_numerical_facts_score = some_metrics.get("error_numerical_facts_score", 0)
            error_ner_facts_score = some_metrics.get("error_ner_facts_score", 0)
            intuition_score = some_metrics.get("intuition_score", 0)
            speech_index = some_metrics.get("speech_index", 0)
        except Exception as e:
            logger.warning("Exception raised during 'start_analyze'", exc=repr(e), traceback=format_exc())

    update_entry_by_id(document.ar_id, AnalysisResult(sentiment_index=some_metrics.get('sentiment_index'),
                                                      facts=some_metrics.get('facts')))

    # Считаем percentage_blacklist
    if len(new_sources) > 0:
        blacklisted = db.query(BlacklistedSource
                               ).filter(BlacklistedSource.url in [ns.url for ns in new_sources]
                                        ).all()
        percentage_blacklist = len(blacklisted) / len(new_sources) * 100
    else:
        percentage_blacklist = 0
    update_entry_by_id(document.ar_id, AnalysisResult(percentage_blacklist=percentage_blacklist))

    fake_index = calculate_final_fake_score(timePublished=len(urls),
                                            percentageBlackList=percentage_blacklist,
                                            avgSourceScore=0.5,
                                            error_numerical_facts_score=error_numerical_facts_score,
                                            error_ner_facts_score=error_ner_facts_score,
                                            grammaticErrorsCount=grammatic_errors_count,
                                            waterIndex=water_index,
                                            speechIndex=speech_index,
                                            intuitionIndex=intuition_score)
    update_entry_by_id(document.ar_id, AnalysisResult(fake_index=fake_index))
    logger.info('Analysis has been finished')
    return

