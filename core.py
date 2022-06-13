from collections import Counter
from typing import Tuple, Mapping, List

from razdel import sentenize
from scipy.spatial.distance import cosine
from wiki_ru_wordnet import WikiWordnet

from aux_tools import translate_text, get_text_from_url, get_antiplag_uid, get_antiplag_data_from_uid, TextFeatures, \
    ApTextTestResult, SeoCheckResult, TextKeysGroup, TextKeys, SpellCheckResult, \
    UniqTestResults, SimilarArticleData, ArticleBaseData
from data_science.clickbait_predictor import Clickbait_predictor
from data_science.fact_extractor import Fact_extractor
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

def start_analyze(article_id: int) -> None:
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
    ap_data = get_antiplag_data_from_uid(uid)
    # TODO: запустить дс модули и начать их результаты кидать в базу
    proto_text = ''
    proto_title = ''
    article_text = document.text
    article_title = document.title

    # float расстояние векторов эмоций между анализируемым текстом и текстом-первоисточником
    sentiment_score = text_source_sentiment_score(article_text, article_title, proto_text,
                                                  proto_title)  # TODO: Подать истенные данные первоисточника

    antiplagiat_score = None  # TODO добавить скор схожести текстов из антиплагиата

    # float скоры эмоций для анализируемого текста
    negative_score, positive_score, neutral_score, skip_score, speech_score, clickbait_score, rationality_score, intuition_score = get_sentiment_scores(
        article_text, article_title)

    # TODO Добавить функцию выделения семантического кора и подсчета скора соответствия
    semantic_core = ""
    distance_score = None

    # float скор ошибок фактов-чисел, float скор ошибок фактов-сущностей, str сообщение с выявлением ошибок фактов
    error_numerical_facts_score, error_ner_facts_score, facts_message = text_source_facts_comparison(article_text,
                                                                                                     proto_text)

    message_to_frontend = f"Семантическое ядро новости:\n\n" \
                          f"{semantic_core}\n\n\n" \
                          f"{facts_message}"
    # TODO: после того как весь дс выполнится - загрузить данные по уид с текстру

    # TODO: остальные действия которым необходимы урлы и прочее с текстру

    # TODO Финальный скор на фронт
    final_score = 0#calculate_final_fake_score(timePublished, percentageBlackList, avgSourceScore, error_numerical_facts_score,
                               #error_ner_facts_score, grammaticErrorsCount, waterIndex, speechIndex, intuitionIndex)
    pass


def calculate_final_fake_score(timesPublished, percentageBlackList, avgSourceScore, error_numerical_facts_score,
                               error_ner_facts_score, grammaticErrorsCount, waterIndex, speechIndex, intuitionIndex):
    """
    :param timesPublished: кол-во публикаций
    :param percentageBlackList: процент источников в "черном списке"
    :param avgSourceScore: средний рейтинг источников
    :param error_numerical_facts_score: искажение количественных фактов
    :param error_ner_facts_score:искажение качественных фактов
    :param grammaticErrorsCount: кол-во грамматических ошибок
    :param waterIndex: индекс "воды" в тексте
    :param speechIndex: "разговорная" речь
    :param intuitionIndex: "научная" речь
    :return: итоговая оценка
    """
    if timesPublished < 10:
        timePublished_coeff = 0.7
    elif 10 <= timesPublished < 20:
        timePublished_coeff = 0.95
    elif timesPublished >= 20:
        timePublished_coeff = 0

    if percentageBlackList < 20:
        percentageBlackList_coeff = 1
    elif 20 <= percentageBlackList < 50:
        percentageBlackList_coeff = 0.95
    elif percentageBlackList >= 50:
        percentageBlackList_coeff = 0.8

    if avgSourceScore < 0.3:
        avgSourceScore_coeff = 0.7
    elif 0.3 <= avgSourceScore < 0.7:
        avgSourceScore_coeff = 0.95
    elif avgSourceScore >= 0.7:
        avgSourceScore_coeff = 1

    if error_numerical_facts_score == 0:
        error_numerical_facts_score_coeff = 1
    elif error_numerical_facts_score == 1:
        error_numerical_facts_score_coeff = 0.6
    elif error_numerical_facts_score == 2:
        error_numerical_facts_score_coeff = 0.55
    elif error_numerical_facts_score >= 3:
        error_numerical_facts_score_coeff = 0.5

    if error_ner_facts_score == 0:
        error_ner_facts_score_coeff = 1
    elif error_ner_facts_score == 1:
        error_ner_facts_score_coeff = 0.8
    elif error_ner_facts_score == 2:
        error_ner_facts_score_coeff = 0.7
    elif error_ner_facts_score >= 3:
        error_ner_facts_score_coeff = 0.6

    if grammaticErrorsCount < 4:
        grammaticErrorsCount_coeff = 1
    elif 4 <= grammaticErrorsCount < 7:
        grammaticErrorsCount_coeff = 0.9
    elif grammaticErrorsCount >= 7:
        grammaticErrorsCount_coeff = 0.8

    if waterIndex < 30:
        waterIndex_coeff = 1
    elif 30 <= waterIndex < 40:
        waterIndex_coeff = 0.95
    elif waterIndex >= 40:
        waterIndex_coeff = 0.9

    if speechIndex < 0.02:
        speechIndex_coeff = 1
    elif 0.02 <= speechIndex < 0.1:
        speechIndex_coeff = 0.9
    elif speechIndex >= 0.1:
        speechIndex_coeff = 0.8

    if intuitionIndex < 0.5:
        intuitionIndex_coeff = 1
    elif intuitionIndex >= 0.5:
        intuitionIndex_coeff = 0.9

    raw_score = timePublished_coeff * percentageBlackList_coeff * avgSourceScore_coeff * \
                error_numerical_facts_score_coeff * error_ner_facts_score_coeff * grammaticErrorsCount_coeff * \
                waterIndex_coeff * speechIndex_coeff * \
                intuitionIndex_coeff

    normalized_score = 100*raw_score

    return 100*raw_score


def text_source_sentiment_score(text, title, text_source, title_source) -> float:  # delta_tone_vector
    """
    :param text: Текст статьи(новости)
    :param title: Заголовок новости
    :param text_source: Текст статьи(новости) источника
    :param title_source: Заголовок новости источника
    :return: sentiment distance - чем ближе к 0 - тем ближе тексты, чем ближе к 1 - тем дальше
    """
    _, text_scores = get_sentiment_scores(text, title)
    _, source_scores = get_sentiment_scores(text_source, title_source)

    column_names = ["negative", "positive", "neutral", "skip", "speech", 'clickbait_score', 'rationality', 'intuition']
    text_vector = [text_scores[column] for column in column_names]
    source_vector = [source_scores[column] for column in column_names]

    distance = cosine(text_vector, source_vector)

    return distance


def get_sentiment_scores(text, title) -> Mapping[str, float]:
    """
    :param text: Текст статьи(новости)
    :param title: Заголовок новости
    :return: Текст статьи(новости) str и результаты анализа текста в виде: Dict ["positive": float, "negative": float, "neutral": float, "skip": float,
        "speech": float, "clickbait_score":float]
    """

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

    column_names = ["negative", "positive", "neutral", "skip", "speech", 'clickbait_score', 'rationality', 'intuition']
    text_vector = [sentiment_scores_dict[column] for column in column_names]
    return text_vector


def get_fake_score_from_url(url, id) -> Tuple[str, Mapping[str, float]]:
    """
    :param id:
    :param url: Ccылка на статью (новость)
    :return:  Текст статьи(новости) str и результаты анализа текста в виде: Dict ["positive": float, "negative": float, "neutral": float, "skip": float,
        "speech": float, "clickbait_score":float]
    """
    article_text = get_text_from_url(url)[5]
    article_title = get_text_from_url(url)[0]
    return get_sentiment_scores(article_text, article_title)


def get_article_text_and_title(url) -> ArticleBaseData:
    """
    :param url: Ссылка на текст статьи (новости)
    :return: {'article_title':заголовок статьи, 'article_text':текст статьи}
    """
    return get_text_from_url(url)


def check_is_primary_source(url_list) -> Tuple[str, bool]:
    """
    :param url_list: список адресов для проверки
    :return: список пар адрес = признак первоисточника (True - первоисточник, False - нет)
    """
    return ["", False]


def check_percent_of_copy_from_source(text, text_source) -> float:
    """
    :param id: индитификатор новости из базы
    :param text: Текст статьи(новости)
    :param title: Заголовок новости
    :param id_source: индитификатор новости источника из базы
    :param text_source: Текст статьи(новости) источника
    :param title_source: Заголовок новости источника
    :return: similarity score - чем ближе к 0 - тем меньше одинаковых предложений, чем ближе к 1 - тем больше
    """
    sentences = [sentence.text for sentence in sentenize(text)]
    num_coincidences = 0
    for sentence in sentences:
        if sentence in text_source:
            num_coincidences += 1
        else:
            continue
    num_coincidences = sum([1 for sentence in sentences if sentence in text_source])
    return num_coincidences / len(sentences)


def text_source_facts_comparison(text, text_source) -> Tuple[float, float, str]:
    """
    :param id: индитификатор новости из базы
    :param text: Текст статьи(новости)
    :param title: Заголовок новости
    :param id_source: индитификатор новости источника из базы
    :param text_source: Текст статьи(новости) источника
    :param title_source: Заголовок новости источника
    :return: list of error messaqes для фактов-числительных and list of errors messages для фактов-объектов
    """
    text_numerical_facts, text_ner_facts = get_facts_from_text(text)
    source_numerical_facts, source_ner_facts = get_facts_from_text(text_source)
    numerical_error_messages = compare_numerical_facts(
        source_numerical_facts,
        text_numerical_facts)

    ner_error_messages = compare_ner_facts(source_ner_facts, text_ner_facts)

    if len(text_numerical_facts) != 0:
        error_numerical_facts_score = len(numerical_error_messages)  # / len(text_numerical_facts)
    else:
        error_numerical_facts_score = 1

    if len(text_ner_facts) != 0:
        error_ner_facts_score = len(ner_error_messages)  # / len(text_ner_facts)
    else:
        error_ner_facts_score = 1

    facts_message = "\n".join(numerical_error_messages + ner_error_messages)
    return error_numerical_facts_score, error_ner_facts_score, facts_message


def compare_numerical_facts(source_numerical_facts, text_numerical_facts):
    error_messages = []
    for key in text_numerical_facts.keys():
        if key == "" or key == "год":
            continue
        if len(key.split()) <= 1:
            res, synonims = check_if_key_or_synonims_in_list(key, source_numerical_facts.keys())
        else:
            res = True
            synonims = [key]
        if res:
            text_num_fact = text_numerical_facts[key]
            source_num_fact = []
            for synonim in synonims:
                source_num_fact += source_numerical_facts[synonim]
            text_nums = [num_obj['number'] for num_obj in text_num_fact]
            source_nums = [num_obj['number'] for num_obj in source_num_fact]
            different_numbers = list(set(text_nums) - set(source_nums))
            if len(different_numbers) > 0:
                message = "\nФакты требуют подтверждения: \n"
                source_message = "Факты в источнике: \n"
                source_fact_texts = "\n\n".join(
                    [f"Факт: {fact['number']} {synonim}\n Текст: {fact['sentence']}" for fact in
                     source_num_fact])
                text_message = f"\n\n\nФакты в тексте: \n"
                diff_facts = [find_first_number_obj_with_given_num(text_num_fact, number) for number in
                              different_numbers]
                text_fact_texts = "\n\n".join(
                    [f"Факт: {fact['number']}  {key}\n Текст: {fact['sentence']}" for fact in diff_facts])
                error_messages.append(f"{message}{source_message}{source_fact_texts}{text_message}{text_fact_texts}")
    return error_messages


def check_if_key_or_synonims_in_list(key, list_check):
    if key in list_check:
        return True, [key]
    wikiwordnet = WikiWordnet()
    synsets = wikiwordnet.get_synsets(key)
    synonims = []
    for synset in synsets:
        for w in synset.get_words():
            synonims.append(w.lemma())
    if key == "место":
        synonims.append("строчка")
    intersection = list(set(synonims).intersection(set(list_check)))
    if len(intersection) != 0:
        return True, intersection
    else:
        return False, [key]


def compare_ner_facts(source_ner_facts, text_ner_facts):
    ner_types = {"PER": "ЛИЧНОСТЬ",
                 "LOC": "ЛОКАЦИЯ",
                 "ORG": "ОРГАНИЗАЦИЯ"}
    error_messages = []

    for key in source_ner_facts.keys():
        source_ner_fact = source_ner_facts[key]
        if len(source_ner_fact) > 2:
            values = [fact["Normal spans"] for fact in source_ner_fact]
            counter = Counter(values)
            most_important_value = counter.most_common(1)[0][0]
            values_text = [fact["Normal spans"] for fact in text_ner_facts[key]]
            if most_important_value not in values_text:
                message = "\nВажная сущность исходного текста пропущена: \n"
                source_message = f"Сущность в источнике: {most_important_value}, тип: {ner_types[key]}\n"
                source_fact_texts = "\n\n".join(
                    [f"Текст: {fact['sentence']}" for fact in source_ner_fact])
                error_messages.append(f"{message}{source_message}{source_fact_texts}")

    for key in text_ner_facts.keys():
        if key in source_ner_facts.keys():
            text_ner_fact = text_ner_facts[key]
            source_ner_fact = source_ner_facts[key]
            text_values = [fact["Normal spans"] for fact in text_ner_fact]
            source_values = [fact["Normal spans"] for fact in source_ner_fact]
            different_values = list(set(text_values) - set(source_values))
            if len(different_values) > 0:
                if len(different_values) != 1 or different_values[0] != 'covid-19':
                    message = f"\nВ тексте появились сущности типа {ner_types[key]}, не совпадающие с сущностями этого типа в источнике: \n"

                    diff_facts = [fact for fact in text_ner_fact if
                                  fact["Normal spans"] in different_values and fact["Normal spans"] != "covid-19"]
                    text_fact_texts = "\n\n".join(
                        [f"Факт: {fact['Normal spans']} {ner_types[key]}\n Текст: {fact['sentence']}" for fact in
                         diff_facts])
                    error_messages.append(f"{message}{text_fact_texts}")
        else:
            message = f"\nВ тексте появился тип сущностей {ner_types[key]}, не представленный в источнике: \n"

            text_fact_texts = "\n\n".join(
                [f"Факт: {fact['Normal spans']} {ner_types[key]}\n Текст: {fact['sentence']}" for fact in
                 text_ner_facts[key]])
            error_messages.append(f"{message}{text_fact_texts}")
    return error_messages


def find_first_number_obj_with_given_num(num_fact, num):
    for numbers in num_fact:
        if numbers['number'] == num:
            return numbers


def get_facts_from_text(text: str):
    ner_extractor_obj = NER_extractor()
    fact_extractor_obj = Fact_extractor()

    _, numerical_facts = fact_extractor_obj.extract_fact_from_text(text)
    ner_facts = ner_extractor_obj.get_ner_elements(text)

    return numerical_facts, ner_facts
