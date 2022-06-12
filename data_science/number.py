import re

from yargy import rule, or_, and_, Parser
from yargy.pipelines import morph_pipeline, caseless_pipeline
from yargy.interpretation import fact, const, attribute
from yargy.predicates import eq, caseless, normalized, type, gram, in_
from yargy import interpretation as interp

Number = fact('Number', ['int', 'multiplier'])
NUMS_ORDINAL = {
    'нулевой': 0,
    'нулевая': 0,
    'нулевоe': 0,
    'первый': 1,
    'первая': 1,
    'первое': 1,
    'второй': 2,
    'вторая': 2,
    'второе': 2,
    'третий': 3,
    'третья': 3,
    'третье': 3,
    'четвертый': 4,
    'четвертая': 4,
    'четвертое': 4,
    'пятый': 5,
    'пятая': 5,
    'пятое': 5,
    'шестой': 6,
    'шестая': 6,
    'шестое': 6,
    'седьмой': 7,
    'седьмая': 7,
    'седьмое': 7,
    'восьмой': 8,
    'восьмая': 8,
    'восьмое': 8,
    'девятый': 9,
    'девятая': 9,
    'девятое': 9,
    'десятый': 10,
    'десятая': 10,
    'десятое': 10,
    'одиннадцатый': 11,
    'одиннадцатая': 11,
    'одиннадцатое': 11,
    'двенадцатый': 12,
    'двенадцатая': 12,
    'двенадцатое': 12,
    'тринадцатый': 13,
    'тринадцатая': 13,
    'тринадцатое': 13,
    'четырнадцатый': 14,
    'четырнадцатая': 14,
    'четырнадцатое': 14,
    'пятнадцатый': 15,
    'пятнадцатая': 15,
    'пятнадцатое': 15,
    'шестнадцатый': 16,
    'шестнадцатая': 16,
    'шестнадцатое': 16,
    'семнадцатый': 17,
    'семнадцатая': 17,
    'семнадцатое': 17,
    'восемнадцатый': 18,
    'восемнадцатая': 18,
    'восемнадцатое': 18,
    'девятнадцатый': 19,
    'девятнадцатая': 19,
    'девятнадцатое': 19,
    'двадцатый': 20,
    'двадцатая': 20,
    'двадцатое': 20,
    'тридцатый': 30,
    'тридцатая': 30,
    'тридцатое': 30,
    'сороковой': 40,
    'сороковое': 40,
    'сороковая': 40,
    'пятьдесятый': 50,
    'пятьдесятая': 50,
    'пятьдесятое': 50,
    'шестьдесятый': 60,
    'шестьдесятая': 60,
    'шестьдесятое': 60,
    'семидесятый': 70,
    'семидесятая': 70,
    'семидесятое': 70,
    'восьмидесятый': 80,
    'восьмидесяая': 80,
    'восьмидесятое': 80,
    'девяностый': 90,
    'девяностая': 90,
    'девяностое': 90,
    'сотый': 100,
    'сотая': 100,
    'сотое': 100,
    'двухсотый': 200,
    'двухсотая': 200,
    'двухсотое': 200,
    'трехсотый': 300,
    'трехсотая': 300,
    'трехсотое': 300,
    'четырехсотый': 400,
    'четырехсотая': 400,
    'четырехсотое': 400,
    'пятисотый': 500,
    'пятисотое': 500,
    'пятисотое': 500,
    'шестисотый': 600,
    'шестисотая': 600,
    'шестисотое': 600,
    'семисотый': 700,
    'семисотая': 700,
    'семисотое': 700,
    'восьмисотый': 800,
    'восьмисотая': 800,
    'восьмисотое': 800,
    'девятисотый': 900,
    'девятисотая': 900,
    'девятисотое': 900,
    'тысячный': 10 ** 3,
    'тысячная': 10 ** 3,
    'тысячное': 10 ** 3,
    'миллионный': 10 ** 6,
    'миллионная': 10 ** 6,
    'миллионное': 10 ** 6,
    'миллиардный': 10 ** 9,
    'миллиардная': 10 ** 9,
    'миллиардное': 10 ** 9,
    'триллионный': 10 ** 12,
    'триллионная': 10 ** 12,
    'триллионное': 10 ** 12,
}
NUMS_RAW = {
    'ноль': 0,
    'нуль': 0,
    'один': 1,
    'два': 2,
    'три': 3,
    'четыре': 4,
    'пять': 5,
    'шесть': 6,
    'семь': 7,
    'восемь': 8,
    'девять': 9,
    'десять': 10,
    'одиннадцать': 11,
    'двенадцать': 12,
    'тринадцать': 13,
    'четырнадцать': 14,
    'пятнадцать': 15,
    'шестнадцать': 16,
    'семнадцать': 17,
    'восемнадцать': 18,
    'девятнадцать': 19,
    'двадцать': 20,
    'тридцать': 30,
    'сорок': 40,
    'пятьдесят': 50,
    'шестьдесят': 60,
    'семьдесят': 70,
    'восемьдесят': 80,
    'девяносто': 90,
    'сто': 100,
    'двести': 200,
    'триста': 300,
    'четыреста': 400,
    'пятьсот': 500,
    'шестьсот': 600,
    'семьсот': 700,
    'восемьсот': 800,
    'девятьсот': 900,
    'тысяча': 10 ** 3,
    'миллион': 10 ** 6,
    'миллиард': 10 ** 9,
    'триллион': 10 ** 12,
}
DOT = eq('.')
INT = type('INT')
THOUSANDTH = rule(caseless_pipeline(['тысячных', 'тысячная'])).interpretation(const(10 ** -3))
HUNDREDTH = rule(caseless_pipeline(['сотых', 'сотая'])).interpretation(const(10 ** -2))
TENTH = rule(caseless_pipeline(['десятых', 'десятая'])).interpretation(const(10 ** -1))
THOUSAND = or_(
    rule(caseless('т'), DOT),
    rule(caseless('тыс'), DOT.optional()),
    rule(normalized('тысяча')),
    rule(normalized('тыща'))
).interpretation(const(10 ** 3))
MILLION = or_(
    rule(caseless('млн'), DOT.optional()),
    rule(normalized('миллион')),
    rule(normalized('миллиона')),
    rule(normalized('миллиону')),
    rule(normalized('миллионов')),
    rule(normalized('миллионами')),
    rule(normalized('миллионах')),
    rule(normalized('миллионам'))
).interpretation(const(10 ** 6))
MILLIARD = or_(
    rule(caseless('млрд'), DOT.optional()),
    rule(normalized('миллиард'))
).interpretation(const(10 ** 9))
TRILLION = or_(
    rule(caseless('трлн'), DOT.optional()),
    rule(normalized('триллион'))
).interpretation(const(10 ** 12))
MULTIPLIER = or_(
    THOUSANDTH,
    HUNDREDTH,
    TENTH,
    THOUSAND,
    MILLION,
    MILLIARD,
    TRILLION
).interpretation(Number.multiplier)
NUM_RAW = rule(morph_pipeline(NUMS_RAW).interpretation(Number.int.normalized().custom(NUMS_RAW.get)))
NUM_ORDINAL = rule(morph_pipeline(NUMS_ORDINAL).interpretation(Number.int.normalized().custom(NUMS_ORDINAL.get)))
NUM_INT = rule(INT).interpretation(Number.int.custom(int))
NUM = or_(
    NUM_RAW,
    NUM_INT,
    NUM_ORDINAL
).interpretation(Number.int)
NUMBER = or_(
    rule(NUM, MULTIPLIER.optional())
).interpretation(Number)


def normalize_float(value):
    value = re.sub('[\s,.]+', '.', value)
    return float(value)


ADJF = gram('ADJF')
NOUNF = gram('NOUN')
PRTF = gram('PRTF')

Adjs = fact(
    'Adjs',
    [attribute('parts').repeatable()]
)

Nouns = fact(
    'Nouns',
    [attribute('parts').repeatable()]
)

ADJ = or_(
    ADJF,
    PRTF,
).interpretation(
    interp.normalized()
).interpretation(
    Adjs.parts
)

NOUN = NOUNF.interpretation(
    interp.normalized()
).interpretation(
    Nouns.parts
)

ADJS = ADJ.repeatable(max=1).interpretation(
    Adjs
)
NOUNS = NOUN.repeatable(max=1).interpretation(
    Nouns
)

Number_fact = fact(
    'Number fact',
    [attribute('number').repeatable(), attribute('adjs').repeatable(), attribute('nouns').repeatable()])


def normalize_float(value):
    value = re.sub('[\s,.]+', '.', value)
    return float(value)


FLOAT = rule(
    INT,
    in_('.,'),
    INT
).interpretation(
    interp.custom(normalize_float)
).interpretation(Number_fact.number)

DIGIT = INT.interpretation(
    interp.custom(int)
).interpretation(Number_fact.number)

NUMBER_FACT = rule(or_(FLOAT, DIGIT).interpretation(Number_fact.number),
                   ADJS.optional().interpretation(
                       Number_fact.adjs), NOUNS.optional().interpretation(
        Number_fact.nouns)).interpretation(
    Number_fact
)
