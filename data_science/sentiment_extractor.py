from typing import Tuple, Mapping, Dict

import pandas as pd
import plotly as plotly
import plotly.express as px
import razdel
from dostoevsky.models import FastTextSocialNetworkModel
from dostoevsky.tokenization import RegexTokenizer


class Sentiment_extractor:
    def __init__(self):
        self.tokenizer = RegexTokenizer()
        self.model = FastTextSocialNetworkModel(tokenizer=self.tokenizer)

    def get_sentiment_scores(self, text_rus: str) -> Tuple[Dict[str, float], plotly.graph_objects.Figure]:
        """

        :param text_rus: Piece of text in string format. Can be sentence or whole article
        :return: Dictionary, that has form {"positive": float, "negative": float, "neutral": float, "skip": float,
        "speech": float} with sentiment scores of the text (scores averaged per sentence) and
        visualisation of neutral, positive and negative scores of sentences in a text
        """
        sentences = [sentence.text for sentence in razdel.sentenize(text_rus)]
        results = self.model.predict(sentences)

        results_df = pd.DataFrame.from_dict(results).fillna(0)
        fig = px.scatter_ternary(results_df, a="neutral", b="positive", c="negative",
                                 color_discrete_map={"neutral": "blue", "positive": "green", "negative": "red"})
        results_mean = results_df.mean(axis=0).to_dict()
        return results_mean, fig
