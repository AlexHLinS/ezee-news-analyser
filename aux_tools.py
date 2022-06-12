import json
from typing import Tuple, NamedTuple
import requests
from razdel import sentenize
from translate import Translator
from time import sleep
from newspaper import Article, ArticleException
import razdel

from htmldate import find_date

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

    result = json.loads(requests.post(antiplag_request_url, requests_params).text)

    return result

#------
def get_errors_words(uid:str, text:str):
    '''
    :param uid: идентификатор результатов анализа для API text.ru
    :param text: текст статьи
    :return: ['номера позиций слов с ошибками в тексте']
    '''
    all_ap_data = get_antiplag_data_from_uid(uid)
    tokens = list(razdel.tokenize(text))
    words = [_.text for _ in tokens]
    spell_check = all_ap_data['spell_check']
    errors = json.loads(spell_check)
    result = list()
    for error in errors:
        result.append(words.index(error['error_text']))
    return result

def get_relative_urls(uid:str, similarity_criteria:int):
    """
    :param uid: идентификатор результатов анализа для API text.ru
    :param similarity_criteria:  процент совпадения, ниже которого результаты не выдаются целое число от 0 до 100
    :return: [{'url': 'https://адрес сайта', 'plagiat': '100', 'words': ['номера позиций "совпадающих" слов в тексте']}, ...]
    """
    result_json = get_antiplag_data_from_uid(uid)['result_json']
    urls = json.loads(result_json)['urls']
    result = list()
    for url in urls:
        if int(url['plagiat']) >= similarity_criteria:
            result.append(url)
    return result

def get_relative_urls_and_error_indexes(uid:str, similarity_criteria:int, text:str):
    """
    :param uid: идентификатор результатов анализа для API text.ru
    :param similarity_criteria: процент совпадения, ниже которого результаты не выдаются целое число от 0 до 100
    :param text: текст статьи
    :return: [[{'url': 'https://адрес сайта', 'plagiat': '100', 'words': ['номера позиций "совпадающих" слов в тексте']}, ...], ['номера позиций слов с ошибками в тексте']]

    """
    urls = get_relative_urls(uid,similarity_criteria)
    errors = get_errors_words(uid, text)
    result = list()
    result.append(urls)
    result.append(errors)
    return result

# ------------------ black lists
# TODO: добавить функционал загрузки black lists

# ------------------- loading data from url's

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



