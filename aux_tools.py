import json
from typing import Tuple, NamedTuple
import requests
from razdel import sentenize
from translate import Translator
from time import sleep
from newspaper import Article, ArticleException

from htmldate import find_date


# ------------------ translator

def translate_text(text, from_lang, to_lang) -> str:
    """
    :param text: text for translation
    :param from_lang: origin language code according ISO_639-1 (see: https://en.wikipedia.org/wiki/ISO_639-1)
    :param to_lang: target language code according ISO_639-1 (see: https://en.wikipedia.org/wiki/ISO_639-1)
    :return: translated text
    """
    sentences = list(sentenize(text))
    result = ''

    for sentence in sentences:
        translator = Translator(from_lang=from_lang, to_lang=to_lang)
        result = result + translator.translate(sentence.text) + ' '

    return result


# ------------------ antiplag

def get_token_from_file(token_file_name) -> str:
    """
    :param token_file_name: файл, содержащий токен
    :return: строку с токеном
    """
    with open(token_file_name, 'r') as token_file:
        token = token_file.read()
    if not token or len(token) < 1:
        return None
    return token


def get_antiplag_uid(text) -> str:
    """
    :param text: текст для проверки в системе антиплагиат
    :return: UID результата проверки
    """

    antiplag_request_url = 'http://api.text.ru/post'
    antiplag_token = get_token_from_file('antiplag.token')

    requests_params = {'text': text,
                       'userkey': antiplag_token}

    result_uid = json.loads(requests.post(antiplag_request_url, requests_params).text)['text_uid']

    return result_uid


def get_antiplag_data_from_uid(uid):
    """
    :param uid: UID результата проверки
    :return: JSON результатов проверки:
    ['text_unique', 'result_json', 'spell_check', 'seo_check', 'unique']
    описание схемы: https://text.ru/api-check/manual
    """

    antiplag_request_url = 'http://api.text.ru/post'
    antiplag_token = get_token_from_file('antiplag.token')

    requests_params = {'uid': uid,
                       'userkey': antiplag_token,
                       'jsonvisible': 'detail'}

    while True:
        result = json.loads(requests.post(antiplag_request_url, requests_params).text)
        try:
            a = result['result_json']
            break
        except KeyError:
            sleep(1000)

    return result


# ------------------ black lists
# TODO: добавить функционал загрузки black lists

# ------------------- loading data from url's
class ArticleBaseData(NamedTuple):
    url: str
    title: str
    text: str

def get_text_from_url(url) -> ArticleBaseData:
    """
    :param url: Адрес статьи
    :return: объект ArticleBaseData(url=присланный адрес, title=заголовок статьи, text=текст статьи)
    """
    try:
        article = Article(url=url)
        article.download()
        article.parse()
        article_text = article.text
        article_title = article.title
    except ArticleException:
        return ArticleBaseData(url=url, title='', text='')

    return ArticleBaseData(url=url, title=article_title, text=article_text)


#### Structures

class ArticleBaseData(NamedTuple):
    url: str
    title: str
    text: str


class SimilarArticleData(NamedTuple):
    url: str
    similarity_score: float
    similar_words_list: Tuple[str]


class UniqTestResults(NamedTuple):
    date_check: str
    unique_score: float
    cleared_text: str
    similar_articles: Tuple[SimilarArticleData]


class SpellCheckResult(NamedTuple):
    error_type: str
    reason: str
    not_correct_text: str
    correct_replacements: Tuple[str]
    error_segment_start_position: int
    error_segment_end_position: int


class TextKeys(NamedTuple):
    key_title = str
    count = int


class TextKeysGroup(NamedTuple):
    key_title = str
    count = int
    sub_keys = Tuple[TextKeys]


class SeoCheckResult(NamedTuple):
    count_chars_with_space: int
    count_chars_without_space: int
    count_words: int
    water_percent: float
    spam_percent: float
    mixed_words_positions: int
    list_keys: Tuple[TextKeys]
    list_keys_group: Tuple[TextKeysGroup]


class ApTextTestResult(NamedTuple):
    uid: str
    text_unique: float
    uniq_results: UniqTestResults
    spell_results: Tuple[SpellCheckResult]
    seo_results: SeoCheckResult


class TextFeatures(NamedTuple):
    mistakes_count: int
    spam_index: float
    water_index: float
    is_directional_pronouns_used: bool
    is_direct_appear: bool
    is_any_links: bool
