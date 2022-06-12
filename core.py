from typing import Tuple, Mapping
import asyncio
from aux_tools import translate_text, get_text_from_url, get_antiplag_uid, get_antiplag_data_from_uid
from aux_tools import TextFeatures, ApTextTestResult, SeoCheckResult, TextKeysGroup, TextKeys, SpellCheckResult, \
    UniqTestResults, SimilarArticleData, ArticleBaseData
from data_science.clickbait_predictor import Clickbait_predictor
from data_science.ner_extractor import NER_extractor
from data_science.rationality_intuition_scorer import Rationality_intuition_scorer
from data_science.sentiment_extractor import Sentiment_extractor
import json

from app.db.crud import get_entry_by_id, update_entry_by_id, Document


# TODO: описать и реализовать класс AnalyzedArticle
#  Класс доджен содержать всю информацию и методы
#  необходимые для манипуляций с данными

# описание структуры / полей:
# +id                                -   присваемый в момент получения на back-end и создания записи в базе данных
#                                       запроса на анализ статьи
# +header                            -   заголовок новости (получается или явно или после обработки ссылки на новость)
# +text                              -   заголовок новости (получается или явно или после обработки ссылки на новость)
# is_primary_source                 -   логический признак если первоисточник новости найден
# primary_source_url                -   ссылка на первоисточник
# source_reliability                -   рейтинг достоверности первоисточника
# date_delta                        -   дней между размещением первоисточником и этой новостью
# difference                        -   отличие от первоисточника по тексту (процент "плагиата")
# difference_sum                    -   отличие текса "саммаризации" статьи от оригинала
# deltav_tone_vector                -   изменение вектора тональности
# crossed_words                     -   список слов статьи, пересекающихся с первоисточником
# media_count                       -   список ресурсов, разместивших статью
# media_avg_rate                    -   средний рейтинг ресурсов, разместивших статью
# good_media_percentage             -   доля ресурсов с рейтингом доверия более 8 (по 10 бальной системе)
# diagram_1                         -   данные по динамике перепечатки статьи
# is_real_publication_date          -   указана ли в статье дата публикации
# is_publication_date_difference    -   различается ли дата публикации в статье с фактической датой публикации
# is_author_shown                   -   указан ли в статье автор публикации
# real_references                   -   ссылки на источник новости (организации, новости, исследователи и тд)
# is_organisation_real              -   реальны ли эти организации
# author_rate                       -   рейтинг автора
# Формальные признаки текста:
# mistakes_count                    -   количество ошибок в тексте
# spam_index                        -   индекс "мусора"
# water_index                       -   индекс "воды"
# is_directional_pronouns_used      -   использованы ли указательные местоимения
# is_direct_appear                  -   использованы ли прямые обращения к читателю
# is_any_links                      -   есть ли ссылки на сторонние сайты

'''class AnalyzedArticle(object):

    async def get_semilarity_data(self):
        self.similarity_data = ApTextTestResult

        self.similarity_data.uid = atls.get_text_from_url(self.text)
        raw_sem_data = atls.get_antiplag_data_from_uid(self.similarity_data.uid)
        rj = json.loads(raw_sem_data['result_json'])
        sch = json.loads(raw_sem_data['spell_check'])
        seo = json.loads(raw_sem_data['seo_check'])

        self.similarity_data.text_unique = raw_sem_data['text_unique']

        self.similarity_data.uniq_results = UniqTestResults
        self.similarity_data.uniq_results.similar_articles = []
        self.similarity_data.uniq_results.date_check = rj['date_check']
        self.similarity_data.uniq_results.unique_score = rj['unique']
        self.similarity_data.uniq_results.cleared_text = rj['clear_text']
        for element in rj['urls']:
            self.similarity_data.uniq_results.similar_articles.append(
                SimilarArticleData(url=element['url'], similarity_score=element['plagiat'],
                                   similar_words_list=str(element['words']).split(' ')))

        self.similarity_data.spell_results = []
        for element in sch:
            self.similarity_data.spell_results.append(
                SpellCheckResult(error_type=element['error_type'], reason=element['reason'],
                                 not_correct_text=element['error_text'],
                                 correct_replacements=element['replacements'],
                                 error_segment_start_position=element['start'],
                                 error_segment_end_position=element['end']))

        self.similarity_data.seo_results = SeoCheckResult
        self.similarity_data.seo_results.mixed_words_positions = rj['mixed_words']
        self.similarity_data.seo_results.count_chars_with_space = seo['count_chars_with_space']
        self.similarity_data.seo_results.count_chars_without_space = seo['count_chars_without_space']
        self.similarity_data.seo_results.count_words = seo['count_words']
        self.similarity_data.seo_results.water_percent = seo['water_percent']
        self.similarity_data.seo_results.list_keys = []
        # TODO: implement load list keys

        self.similarity_data.seo_results.list_keys_group = []
        # TODO: inplement load list keys group

        self.similarity_data.seo_results.spam_percent = seo['spam_percent']

        pass

    async def start_data_gethering(self):
        self.get_semilarity_data()
        pass

    def __init__(self, article_id: str, article_title: str, article_text: str) -> None:
        self.article_id = article_id
        self.title = article_title
        self.text = article_text

        self.is_primary_source = None  # -   логический признак если первоисточник новости найден
        self.primary_source_url = None  # -   ссылка на первоисточник
        self.source_reliability = None  # -   рейтинг достоверности первоисточника
        self.date_delta = None  # -   дней между размещением первоисточником и этой новостью
        self.difference = None  # -   отличие от первоисточника по тексту (процент "плагиата")
        self.difference_sum = None  # -   отличие текса "саммаризации" статьи от оригинала
        self.deltav_tone_vector = None  # -   изменение вектора тональности
        self.crossed_words = None  # -   список слов статьи, пересекающихся с первоисточником
        self.media_count = None  # -   список ресурсов, разместивших статью
        self.media_avg_rate = None  # -   средний рейтинг ресурсов, разместивших статью
        self.good_media_percentage = None  # -   доля ресурсов с рейтингом доверия более 8 (по 10 бальной системе)
        self.diagram_1 = None  # -   данные по динамике перепечатки статьи
        self.is_real_publication_date = None  # -   указана ли в статье дата публикации
        self.is_publication_date_difference = None  # -   различается ли дата публикации в статье с фактической датой публикации
        self.is_author_shown = None  # -   указан ли в статье автор публикации
        self.real_references = None  # -   ссылки на источник новости (организации, новости, исследователи и тд)
        self.is_organisation_real = None  # -   реальны ли эти организации
        self.author_rate = None  # -   рейтинг автора
        self.mistakes_count = None  # -   количество ошибок в тексте
        self.spam_index = None  # -   индекс "мусора"
        self.water_index = None  # -   индекс "воды"
        self.is_directional_pronouns_used = None  # -   использованы ли указательные местоимения
        self.is_direct_appear = None  # -   использованы ли прямые обращения к читателю
        self.is_any_links = None  #
        asyncio.run(self.start_data_gethering())
'''

######
def start_analyze(article_id:int) -> None:
    """
    :param article_id: индитификатор анализируемой новости в базе данных
    :return: None
    """
    # TODO: получить документ
    document = get_entry_by_id(article_id, Document)
    text = document.text
    title = document.title
    url = document.url

    # TODO: проверить есть ли при наличии урл, текст и  заголовок, если текста или заголовка нет - попробовать прогрузить
    # TODO: закинуть запрос по тексту на текстру и получить уид
    uid = get_antiplag_uid(text)
    # TODO: запустить дс модули и начать их результаты кидать в базу
    # TODO: после того как весь дс выполнится - загрузить данные по уид с текстру
    ap_data = get_antiplag_data_from_uid(uid)
    # TODO: остальные действия которым необходимы урлы и прочее с текстру
    pass



def get_fake_score(text, title, id) -> Tuple[str, Mapping[str, float]]:
    """
    :param id: индитификатор новости из базы
    :param text: Текст статьи(новости)
    :param title: Заголово новости
    :return: Текст статьи(новости) str и результаты анализа текста в виде: Dict ["positive": float, "negative": float, "neutral": float, "skip": float,
        "speech": float, "clickbait_score":float]
    """
    ner_extractor_obj = NER_extractor()
    sentiment_extractor_obj = Sentiment_extractor()
    clickbait_predictor_obj = Clickbait_predictor()
    rationality_intuition_scorer_obj = Rationality_intuition_scorer()

    sentiment_scores_dict, _ = sentiment_extractor_obj.get_sentiment_scores(text)
    eng_title = translate_text(title, 'ru', 'en')
    clickbait_score = clickbait_predictor_obj.get_clickbait_score(eng_title)
    rationality_intuition_scores_dict = rationality_intuition_scorer_obj.get_rationality_intuition_score(text)
    sentiment_scores_dict['clickbait_score'] = clickbait_score
    for key in rationality_intuition_scores_dict.keys():
        sentiment_scores_dict[key] = rationality_intuition_scores_dict[key]
    return text, sentiment_scores_dict


def get_fake_score_from_url(url, id) -> Tuple[str, Mapping[str, float]]:
    """
    :param id:
    :param url: Ccылка на статью (новость)
    :return:  Текст статьи(новости) str и результаты анализа текста в виде: Dict ["positive": float, "negative": float, "neutral": float, "skip": float,
        "speech": float, "clickbait_score":float]
    """
    article_text = get_text_from_url(url)[5]
    article_title = get_text_from_url(url)[0]
    return get_fake_score(article_text, article_title, id)


def get_article_text_and_title(url) -> ArticleBaseData:
    """
    :param url: Ссылка на текст статьи (новости)
    :return: {'article_title':заголовок статьи, 'article_text':текст статьи}
    """
    article_text = get_text_from_url(url)[5]
    article_title =get_text_from_url(url)[0]
    return ArticleBaseData(url=url, title=article_title, text=article_text)


def check_is_primary_source(url_list) -> Tuple[str, bool]:
    """
    :param url_list: список адресов для проверки
    :return: список пар адрес = признак первоисточника (True - первоисточник, False - нет)
    """
    return ["", False]
