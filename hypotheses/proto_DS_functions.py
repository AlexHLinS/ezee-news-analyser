from typing import Dict, List, Union, Tuple

import plotly as plotly


def get_ner_elements(text_rus: str) -> List[Dict[str, Union[str, int]]]:
    """

    :param text_rus: Piece of text in string format. Can be sentence or whole article
    :return: List of dictionaries, each dictionary has form {"Normal span": str, "Type": str, "start": int,
    "end": int}, where Normal span - refer to normal form of marked word; Type - one of classes person,
    organization, location, time or money; start and end - number of characters in original text where token
    is located.
    """
    pass


def get_clickbait_score(title_eng: str) -> float:
    """

    :param title_eng: Piece of text in string format in English language, article title
    :return: Probability of title to be clickbait.
    """
    pass


def get_sentiment_scores(text: str) -> Tuple[Dict[str, float], plotly.graph_objs._figure.Figure]:
    """

    :param text: Piece of text in string format. Can be sentence or whole article
    :return: Dictionary, that has form {"positive": float, "negative": float, "neutral": float, "skip": float,
    "speech": float} with sentiment scores of the text (scores averaged per sentence) and
    visualisation of neutral, positive and negative scores of sentences in a text
    """
    pass
