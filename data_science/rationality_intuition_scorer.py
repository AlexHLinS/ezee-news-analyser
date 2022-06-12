import os
from typing import Tuple, Mapping

import yaml
from nltk.tokenize import word_tokenize

from data_science.text_processor import Text_processor


class Rationality_intuition_scorer:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.text_processor = Text_processor()
        with open(os.path.join(current_dir, "models", 'rational_intuitive_keywords_rus.yml'), encoding='utf8') as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            keywords_rational_intuitive = yaml.load(file, Loader=yaml.FullLoader)
        self.keywords_rational = keywords_rational_intuitive['rationality']
        self.keywords_intuitive = keywords_rational_intuitive['intuition']

    def get_rationality_intuition_score(self, text_rus: str) -> Mapping[str, float]:
        """

        :param text_rus: Piece of text in string format in English language, article title
        :return: rationality, intuition scores - relative number of rational and intuitive words.
        """
        processed_text = self.text_preprocess(text_rus)
        num_rational = sum([self.calculate_number_of_occurances_of_word_in_text(processed_text, word) for word in
                            self.keywords_rational])
        num_intuitive = sum([self.calculate_number_of_occurances_of_word_in_text(processed_text, word) for word in
                             self.keywords_intuitive])
        num_words = len(processed_text.split())
        return {'rationality': num_rational / num_words, 'intuition': num_intuitive / num_words}

    def text_preprocess(self, text):
        return self.text_processor.stopword(self.text_processor.lemmatizer(self.text_processor.regexp_preprocess(text)))

    def calculate_number_of_occurances_of_word_in_text(self, text, word):
        words = list(text.split())
        return words.count(word)
