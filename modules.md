# DS
## methods
- text_source_sentiment_score(article_text, article_title, proto_text, proto_title) -> sentiment distance - чем ближе к 0 - тем ближе тексты, чем ближе к 1 - тем дальше
- get_sentiment_scores(article_text, article_title) -> Текст статьи(новости) str и результаты анализа текста в виде: Dict ["positive": float, "negative": float, "neutral": float, "skip": float, "speech": float, "clickbait_score":float]
- ? -> semantic_core 
- text_source_facts_comparison(article_text,proto_text) -> list of error messaqes для фактов-числительных and list of errors messages для фактов-объектов
- calculate_final_fake_score(timePublished, percentageBlackList, avgSourceScore, error_numerical_facts_score,
                               error_ner_facts_score, grammaticErrorsCount, waterIndex, speechIndex, intuitionIndex): -> final_score
- compare_numerical_facts(source_numerical_facts, text_numerical_facts) -> error_messages
- check_if_key_or_synonims_in_list(key, list_check) -> {bool, key}
- compare_ner_facts(source_ner_facts, text_ner_facts) -> error_messages
- find_first_number_obj_with_given_num(num_fact, num) -> num
- get_facts_from_text(text: str) -> numerical_facts, ner_facts

## result
- 'sentiment_index': sentiment_score,
- 'facts': message_to_frontend,
- 'error_numerical_facts_score': error_numerical_facts_score,
- 'error_ner_facts_score': error_ner_facts_score,
- 'intuition_score': intuition_score,
- 'speech_index': speech_score

# External API user
## methods
- get_antiplag_uid(text) -> uid
- get_antiplag_data_from_uid(uid) -> ['text_unique', 'result_json', 'spell_check', 'seo_check', 'unique'] описание схемы: https://text.ru/api-check/manual
- get_article_text_and_title(url) -> {'article_title':заголовок статьи, 'article_text':текст статьи}
- check_is_primary_source(url_list) -> список пар адрес = признак первоисточника (True - первоисточник, False - нет)
- check_percent_of_copy_from_source(text, text_source) ->
- def translate_text(text, from_lang, to_lang) -> translated text
- def get_errors_words(uid: str, text: str) ->['номера позиций слов с ошибками в тексте']
- def get_relative_urls(uid: str, similarity_criteria: int)->[{'url': 'https://адрес сайта', 'plagiat': '100', 'words': ['номера позиций "совпадающих" слов в тексте']}, ...]
- get_relative_urls_and_error_indexes(uid: str, similarity_criteria: int, text: str)->[[{'url': 'https://адрес сайта', 'plagiat': '100', 'words': ['номера позиций "совпадающих" слов в тексте']}, ...], ['номера позиций слов с ошибками в тексте']]
- get_urls_dates(urls) ->[{'url': 'https://...', 'plagiat': '...', 'words': ..., date:'YYYY-MM-DD'}, ... ]
- get_earlest_url(urls) -> по самому раннему {'url': 'https://...', 'plagiat': '...', 'words': ..., date:'YYYY-MM-DD'}
- def get_published_count(uid: str, similarity_criteria: int)-> kол-во публикаций с совпадением не ниже similarity_criteria
- get_grammatical_error_count(uid: str) ->количество ошибок в тексте
- get_spam_percent(uid: str) ->метрика spam_percent %
- get_plagiary_percentage(uid: str, unique: bool)->процент уникальности или процент совпадения в зависимости от выбора
- get_water_from(uid: str) ->  процент "воды" в тексте
- get_text_from_url(url) -> объект (url=присланный адрес, title=заголовок статьи, text=текст статьи)