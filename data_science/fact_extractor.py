from collections import Counter

import pandas as pd
from IPython.display import display
from ipymarkup import show_span_ascii_markup as show_markup
from razdel import sentenize
from wiki_ru_wordnet import WikiWordnet
from yargy import (
    Parser
)

from data_science.ner_extractor import NER_extractor
from data_science.number import NUMBER_FACT
from data_science.number_extractor import NumberExtractor


class Fact_extractor:
    def __init__(self):
        self.number_extractor = NumberExtractor()
        self.parser = Parser(NUMBER_FACT)

    def extract_fact_from_text(self, text: str):
        fixed_text = self.number_extractor.replace_groups(text)
        matches = self.parser.findall(fixed_text)
        matches = sorted(matches, key=lambda _: _.span)
        spans = [(_.span.start, _.span.stop - 1) for _ in matches]
        facts = [_.fact for _ in matches]
        facts = self.process_facts(facts, spans, fixed_text)
        return fixed_text, facts

    def process_facts(self, facts, spans, text):
        processed_facts = {}
        sentences = list(sentenize(text))
        for fact, span in zip(facts, spans):
            if len(fact.adjs) != 0:
                fact_adjs = " ".join([" ".join(adj.parts) for adj in fact.adjs])
            else:
                fact_adjs = ""
            if len(fact.nouns) != 0:
                fact_nouns = " ".join([" ".join(noun.parts) for noun in fact.nouns])
            else:
                fact_nouns = ""
            fact_object = (fact_adjs + " " + fact_nouns).strip()

            fact_info = {"number": fact.number[0], 'start': span[0], 'end': span[1],
                         'sentence': self.get_sentence_with_fact(sentences, span)}
            if fact_object in processed_facts.keys():
                processed_facts[fact_object].append(fact_info)
            else:
                processed_facts[fact_object] = [fact_info]
        return processed_facts

    def get_sentence_with_fact(self, sentences, span):
        for sentence in sentences:
            if span[0] >= sentence.start and span[1] <= sentence.stop:
                return sentence.text
        return None


def show_matches(rule, *lines):
    parser = Parser(rule)
    for line in lines:
        matches = parser.findall(line)
        matches = sorted(matches, key=lambda _: _.span)
        spans = [_.span for _ in matches]
        show_markup(line, spans)
        if matches:
            facts = [_.fact for _ in matches]
            if len(facts) == 1:
                facts = facts[0]
            display(facts)


# text = "Выплаты за второго-третьего ребенка выросли на пятьсот двадцать пять тысячных процента и составили 90 тысяч рублей"

text = "В мире Москва занимает третье место, уступая лишь Нью-Йорку и Сан-Франциско. Москва признана первой среди европейских городов в рейтинге инноваций, помогающих в формировании устойчивости коронавирусу. Она опередила Лондон и Барселону. " \
       "Среди мировых мегаполисов российская столица занимает третью строчку — " \
       "после Сан-Франциско и Нью-Йорка. Пятерку замыкают Бостон и Лондон. Рейтинг " \
       "соcтавило международное исследовательское агентство StartupBlink." \
       "Добиться высоких показателей Москве помогло почти 160 передовых решений, " \
       "которые применяются для борьбы с распространением коронавируса. " \
       "Среди них алгоритмы компьютерного зрения на основе искусственного " \
       "интеллекта. Это методика уже помогла рентгенологам проанализировать более трех " \
       "миллионов исследований." \
       "Еще одно инновационное решение — облачная платформа, которая объединяет " \
       "пациентов, врачей, медицинские организации, страховые компании, " \
       "фармакологические производства и сайты. " \
       "Способствовали высоким результатам и технологии, которые помогают " \
       "адаптировать жизнь горожан во время пандемии. Это проекты в сфере умного туризма, " \
       "электронной коммерции и логистики, а также дистанционной работы и " \
       "онлайн-образования. Эксперты агентства StartupBlink оценивали принятые в Москве меры с точки зрения эпидемиологических показателей и влияния на экономику."
extractor = NumberExtractor()


# for match in extractor(text):
#     print(match.fact)

# print(extractor.replace(text))
# print(extractor.replace_groups(text))

# fixed_text = extractor.replace_groups(text)
#
# show_matches(NUMBER_FACT,
#              fixed_text
#              )
# fact_extractor = Fact_extractor()
def text_source_facts_comparison(text, title, id, text_source, title_source, id_source):
    text_numerical_facts, text_ner_facts = get_facts_from_text(text)
    source_numerical_facts, source_ner_facts = get_facts_from_text(text_source)
    numerical_error_messages = compare_numerical_facts(
        source_numerical_facts,
        text_numerical_facts)

    ner_error_messages = compare_ner_facts(source_ner_facts, text_ner_facts)
    return numerical_error_messages, ner_error_messages


def compare_numerical_facts(source_numerical_facts, text_numerical_facts):
    error_messages = []
    facts_with_difference_text = []
    facts_with_difference_source = []
    for key in text_numerical_facts.keys():
        if key == "" or key == "год":
            continue
        if len(key.split()) <= 1:
            res, synonims = check_if_key_or_synonims_in_list(key, source_numerical_facts.keys())
        else:
            res = (key in source_numerical_facts.keys())
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
                # facts_with_difference_text.append(
                #     [find_first_number_obj_with_given_num(text_num_fact, number) for number in
                #      different_numbers])
                # facts_with_difference_source.append([fact for fact in source_num_fact])
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
    facts_with_difference_text = []
    facts_with_key_source_value = []
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
                facts_with_key_source_value.append(
                    [fact for fact in source_ner_fact if fact["Normal spans"] == most_important_value])
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
                    # facts_with_difference_text.append(
                    #     [fact for fact in text_ner_fact if
                    #      fact["Normal spans"] in different_values and fact["Normal spans"] != "covid-19"])
        else:
            message = f"\nВ тексте появился тип сущностей {ner_types[key]}, не представленный в источнике: \n"

            text_fact_texts = "\n\n".join(
                [f"Факт: {fact['Normal spans']} {ner_types[key]}\n Текст: {fact['sentence']}" for fact in
                 text_ner_facts[key]])
            error_messages.append(f"{message}{text_fact_texts}")
            # facts_with_difference_text.append(text_ner_facts[key])
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


text = 'Москва обошла европейские столицы в рейтинге инноваций по устойчивости к COVID-19, опередив Лондон и Барселону, сообщается на официальном сайте мэра Москвы.\nРоссийская столица также заняла третье место среди мировых мегаполисов. В пятерку лидеров вошли Бостон и Лондон.\nЗанять лидирующие позиции в рейтинге Москве помогли около 50 передовых решений, которые применяются для борьбы с распространением COVID-19.\nОдно из таких решений - алгоритмы компьютерного зрения на основе искусственного интеллекта, которые уже помогли рентгенологам проанализировать более трех миллионов исследований.\nТакже высоким результатам способствовали технологии, помогающие адаптировать жизнь москвичей во время пандемии. Среди них - проекты в сфере умного туризма, электронной коммерции и логистики, дистанционной работы и онлайн-образования.\nЭксперты оценивали, как принятые в Москве меры влияют на эпидемиологические показатели и экономику.'

text_source = 'Москва признана первой среди европейских городов в рейтинге инноваций, помогающих в формировании устойчивости коронавирусу. Она опередила Лондон и Барселону.\nСреди мировых мегаполисов российская столица занимает третью строчку — после Сан-Франциско и Нью-Йорка. Пятерку замыкают Бостон и Лондон. Рейтинг составило международное исследовательское агентство StartupBlink.\n\nДобиться высоких показателей Москве помогло почти 160 передовых решений, которые применяются для борьбы с распространением коронавируса. Среди них алгоритмы компьютерного зрения на основе искусственного интеллекта. Это методика уже помогла рентгенологам проанализировать более трех миллионов исследований.\n\nЕще одно инновационное решение — облачная платформа, которая объединяет пациентов, врачей, медицинские организации, страховые компании, фармакологические производства и сайты. Способствовали высоким результатам и технологии, которые помогают адаптировать жизнь горожан во время пандемии. Это проекты в сфере умного туризма, электронной коммерции и логистики, а также дистанционной работы и онлайн-образования.\n\nЭксперты агентства StartupBlink оценивали принятые в Москве меры с точки зрения эпидемиологических показателей и влияния на экономику.\n\nВ борьбе с коронавирусом Москва отказалась от крайностей. Ставку сделали на профилактику: увеличили количество пунктов бесплатного экспресс-тестирования и вакцинации, запатентовали онлайн-программы и платформы для обучения, развивали возможности телемедицины.\n\nМосковская система здравоохранения за время пандемии накопила достаточно большой запас прочности, который позволяет не останавливать плановую и экстренную помощь даже в периоды пиков заболеваемости COVID-19.\n\nСтолица поддерживает бизнес, выделяя субсидии и предоставляя льготы. В этом году мерами поддержки воспользовалось около 25 тысяч предприятий малого и среднего бизнеса.\n\nРейтинг составляется на базе глобальной карты инновационных решений по борьбе с коронавирусом и оценивает около 100 ведущих городов и 40 стран мира. Глобальная карта была создана в марте 2020 года, и в течение года на нее было добавлено более тысячи решений.'

data_test = pd.read_excel("./data_science/data/output.xlsx")


def check_percent_of_copy_from_source(text, title, id, text_source, title_source, id_source):
    sentences = [sentence.text for sentence in sentenize(text)]
    num_coincidences = 0
    for sentence in sentences:
        if sentence in text_source:
            num_coincidences += 1
        else:
            continue
    num_coincidences = sum([1 for sentence in sentences if sentence in text_source])
    return num_coincidences / len(sentences)


results = []

# for ind, row in data_test.iterrows():
#     print(ind)
#     text_init = row["initial_text"]
#     # text_source = row["source_text"]
#     result = text_source_facts_comparison(text_init, None, None, text_source, None, None)
#     # result = check_percent_of_copy_from_source(text_init, None, None, text_source, None, None)
#     results.append(result)
#
# text_source_facts_comparison(text, None, None, text_source, None, None)
