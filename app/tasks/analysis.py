from app.db.crud import *
from app.db.models import *
from app.helpers import default_logger


def analyze_document(document: Document, logger=default_logger) -> None:
    """
    Таска на анализ документа

    Проводит анализ документа
    """

    logger.info('Starting the analysis', doc_id=document.id, ar_id=document.ar_id)

    # TODO: Пока просто для примера. Вместо этого подставить реальный анализ
    from time import sleep
    from datetime import datetime
    from json import dumps
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
        diagram_data=dumps([{"date": datetime.now().replace(day=randint(1, 29)).strftime('%m/%d/%Y'), "is_valid": bool(randint(0, 1))}
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


