from data_science import clickbait_predictor, ner_extractor, sentiment_extractor
import aux_tools as atls


def get_fake_score(text) -> float:
    """
    :param text:
    :return: fake score from 0 to 1 (0-not a fake, 1 - fake)
    """
    ner_extractor_obj = ner_extractor.NER_extractor()
    sentiment_extractor_obj = sentiment_extractor.Sentiment_extractor()

    eng_text = atls.translate_text(text, 'ru', 'en')
    cb_score = clickbait_predictor.get_clickbait_score(eng_text)
    sentiments, fig = sentiment_extractor_obj.get_sentiment_scores(text)
    ners = ner_extractor_obj.get_ner_elements(text)

    # TODO: придумать для MVP формулу расчета fake_score
    fake_score = cb_score
    return fake_score
