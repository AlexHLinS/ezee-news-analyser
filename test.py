import datetime

import pandas as pd

import core
from aux_tools import *
import razdel
import json
from htmldate import find_date
from bs4 import BeautifulSoup as bs
import re
from app.db.crud import get_entry_by_id, Document

test_uid = '62a678a14b054'

title = '''Проектный офис ФЭСН РАНХиГС завершает 30 проектов. И начинает новые.'''
text = '''Ежегодно в мае-июне Проектный офис Факультета экономических и социальных наук завершает работу над бизнес-проектами и представляет результаты заказчикам – российским и международным компаниям.
Среди компаний-заказчиков были крупные российские компании и организации: Сбер, РЖД, ВЭБ, Минстрой РФ, Ростуризм, Правительство Москвы, киностудия им. Горького, холдинг САВООВ ФУДС, Альфа-Банк, ВТБ, Дом РФ, Очаково, Сегежа-Групп а также представительства зарубежных компаний: BMW, DeLonghi, L’Oreal, Pfizer, Ritter Sport, Xiaomi, Avon, Schneider Group и др.
Проектный офис ФЭСН является крупнейшим университетским проектным центром не только по количеству и сложности проектов, и не только по количеству студентов-участников. Он уже создал и создает новые масштабные форматы проектной работы. Так, еще пять лет назад ФЭСН вовлек в проектную деятельность университеты пяти стран Европы и стал разрабатывать с ними полугодичные проекты для международных компаний на английском языке. Некоторые сложные проекты делались усилиями проектных групп нескольких стран; например, в проекте от генерального директора BMW Russia по «Разработке маркетинговой стратегии перехода компании BMW с бензиновых двигателей на электрические в России» бакалавры ФЭСН работали вместе с магистрами из Германии и Бельгии. А в одном из проектов участвовали команды из Германии, Бельгии, Италии, 4 проектные группы из Франции и 5 из Бразилии.'''


def get_errors_words(uid: str, text: str):
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


def get_relative_urls(uid: str, similarity_criteria: int):
    """
    :param uid: идентификатор результатов анализа для API text.ru
    :param similarity_criteria:  процент совпадения, ниже которого результаты не выдаются целое число от 0 до 100
    :return: [{'url': 'https://адрес сайта', 'plagiat': '100', 'words': ['номера позиций "совпадающих" слов в тексте']}, ...]
    """
    result_json = get_antiplag_data_from_uid(test_uid)['result_json']
    urls = json.loads(result_json)['urls']
    result = list()
    for url in urls:
        if int(url['plagiat']) >= similarity_criteria:
            result.append(url)
    return result


def get_relative_urls_and_error_indexes(uid: str, similarity_criteria: int, text: str):
    """
    :param uid: идентификатор результатов анализа для API text.ru
    :param similarity_criteria: процент совпадения, ниже которого результаты не выдаются целое число от 0 до 100
    :param text: текст статьи
    :return: [[{'url': 'https://адрес сайта', 'plagiat': '100', 'words': ['номера позиций "совпадающих" слов в тексте']}, ...], ['номера позиций слов с ошибками в тексте']]

    """
    urls = get_relative_urls(test_uid, similarity_criteria)
    errors = get_errors_words(uid, text)
    result = list()
    result.append(urls)
    result.append(errors)
    return result


def get_url_indexation_date(url: str):
    months = {
        'янв': '01',
        'фев': '02',
        'мар': '03',
        'апр': '04',
        'май': '05',
        'июн': '06',
        'июл': '07',
        'авг': '08',
        'сен': '09',
        'окт': '10',
        'ноя': '11',
        'дек': '12'
    }
    template = r'\d{1,2}\s\D*\s\d{4}\s\d{2}\:\d{2}\:\d{2}\s[GMT]{3}'
    webarch_url = 'http://webcache.googleusercontent.com/search?q=cache:' + url + '&strip=1&vwsrc=0'
    raw_text = requests.get(webarch_url).text
    soup = bs(raw_text, 'lxml')
    date_str = soup.find_all('span')[1].text
    result = re.findall(template, date_str)[0].split()[0:3]
    result.reverse()
    if len(result[-1]) <2: result[-1] = '0'+result[-1]
    result = '-'.join(result)
    for key in months.keys():
        result = result.replace(key, str(months[key]))
    return result


def get_urls_date(url: str):
    result = str(datetime.date.today())
    try:
        result = find_date(url)
    except ValueError:
        try:
            result = get_url_indexation_date(url)
        except IndexError:
            result = str(datetime.date.today())
    return result


def get_urls_dates(urls):
    """
    :param urls: список из выгрузки text.ru urls [{'url': 'https://...', 'plagiat': '...', 'words': ...}, ... ]
    :return: [{'url': 'https://...', 'plagiat': '...', 'words': ..., date:'YYYY-MM-DD'}, ... ]
    """
    result = list()
    for url in urls:
        url['date'] = get_urls_date(url['url'])
        result.append(url)
    return result

def get_earlest_url(urls):
    """
    :param urls: [{'url': 'https://...', 'plagiat': '...', 'words': ..., date:'YYYY-MM-DD'}, ... ]
    :return: по самому раннему {'url': 'https://...', 'plagiat': '...', 'words': ..., date:'YYYY-MM-DD'}
    """
    df = pd.DataFrame(urls)
    return  df.sort_values(by='date').to_dict('records')[0]


def get_water_from(uid:str) -> int:
    """
    :param uid: UID результатов анализа на text.ru
    :return: процент "воды" в тексте
    """
    ap_all = get_antiplag_data_from_uid(uid)
    water = json.loads(ap_all['seo_check'])['water_percent']
    return water


def get_earlest_url_from_uid(uid:str, similarity_criteria):
    """
    :param uid: uid: UID результатов анализа на text.ru
    :param similarity_criteria: процент совпадения, ниже которого результаты не выдаются целое число от 0 до 100
    :return: по самому раннему {'url': 'https://...', 'plagiat': '...', 'words': ..., date:'YYYY-MM-DD'}
    """
    relative_urls = get_relative_urls(uid, similarity_criteria)
    relative_urls_with_dates = get_urls_dates(relative_urls)
    earlest = get_earlest_url(relative_urls_with_dates)
    return earlest

def get_published_count(uid: str, similarity_criteria: int):
    """
    :param uid: uid: UID результатов анализа на text.ru
    :param similarity_criteria: процент совпадения, ниже которого результаты не выдаются целое число от 0 до 100
    :return: кол-во публикаций с совпадением не ниже similarity_criteria
    """
    result = len(get_relative_urls(uid, similarity_criteria))
    return result

def get_plagiary_percentage(uid: str, unique: bool):
    """
    :param uid: UID результатов анализа на text.ru
    :param unique: флаг выбора True - процент уникальности / False - процент совпадения
    :return: процент уникальности или процент совпадения в зависимости от выбора
    """
    ap_all = get_antiplag_data_from_uid(uid)
    pp = json.loads(ap_all['result_json'])['unique']
    if unique:
        return pp
    return 100-pp

def get_grammatical_error_count(uid:str) -> int:
    """
    :param uid: UID результатов анализа на text.ru
    :return: количество ошибок в тексте
    """
    ap_all = get_antiplag_data_from_uid(uid)
    count = len(json.loads(ap_all['spell_check']))
    return count

def get_spam_percent(uid:str) -> int:
    """
    :param uid: UID результатов анализа на text.ru
    :return: метрика spam_percent %
    """
    ap_all = get_antiplag_data_from_uid(uid)
    count = json.loads(ap_all['seo_check'])['spam_percent']
    return count

"""def get_speech_index(article_id: int | title, text):
    if article_id:
        document = get_entry_by_id(article_id, Document)
        index = core.get_sentiment_scores(document.text, document.title)["speech"]
    else:
        index = core.get_sentiment_scores(text, title)["speech"]
    return index
"""
print(get_spam_percent(title, text))
