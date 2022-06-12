from IPython.display import display
from ipymarkup import show_span_ascii_markup as show_markup
from yargy import (
    Parser
)

from data_science.number import NUMBER_FACT
from data_science.number_extractor import NumberExtractor


class Fact_extractor:
    def __init__(self):
        self.number_extractor = NumberExtractor()
        self.parser = Parser(NUMBER_FACT)

    def extract_fact_fromtext(self, text: str):
        fixed_text = self.number_extractor.replace_groups(text)
        matches = self.parser.findall(fixed_text)
        matches = sorted(matches, key=lambda _: _.span)
        spans = [(_.span.start, _.span.stop-1) for _ in matches]
        facts = [_.fact for _ in matches]
        facts = self.process_facts(facts, spans)
        return fixed_text, facts

    def process_facts(self, facts, spans):
        processed_facts = {}
        for fact, span in zip(facts, spans):
            if len(fact.adjs)!=0:
                fact_adjs = " ".join([" ".join(adj.parts) for adj in fact.adjs])
            else:
                fact_adjs = ""
            if len(fact.nouns)!=0:
                fact_nouns = " ".join([" ".join(noun.parts) for noun in fact.nouns])
            else:
                fact_nouns = ""
            fact_object = (fact_adjs+" "+fact_nouns).strip()
            if fact_object in processed_facts.keys():
                processed_facts[fact_object].append({"number": fact.number, 'start': span[0], 'end': span[1]})
            else:
                processed_facts[fact_object] = [{"number": fact.number, 'start': span[0], 'end': span[1]}]
        return processed_facts




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

fixed_text = extractor.replace_groups(text)

show_matches(NUMBER_FACT,
             fixed_text
             )
fact_extractor = Fact_extractor()
