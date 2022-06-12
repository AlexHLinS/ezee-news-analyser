# TO-DO
import re
import string
import os
import joblib
import nltk
from nltk.corpus import stopwords, wordnet

from data_science.text_processor import Text_processor

nltk.download('stopwords')
nltk.download('omw-1.4')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

from nltk import word_tokenize, WordNetLemmatizer


class Clickbait_predictor:
    def __init__(self):
        self.text_processor = Text_processor()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model = joblib.load(os.path.join(current_dir, "models", "clickbait_linear_classifier.joblib"))
        self.tfidf_vectorizer = joblib.load(os.path.join(current_dir, "models", "clickbait_tfidf_vectorizer.joblib"))

    def get_clickbait_score(self, title_eng: str) -> float:
        """

        :param title_eng: Piece of text in string format in English language, article title
        :return: Probability of title to be clickbait.
        """
        processed_text = self.text_preprocess(title_eng)
        tf_idf_text = self.tfidf_vectorizer.transform([processed_text])
        prediction = self.model.predict_proba(tf_idf_text)[0][1]
        return prediction

    def text_preprocess(self, text):
        return self.text_processor.lemmatizer(self.text_processor.regexp_preprocess(text))


