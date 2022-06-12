from typing import List, Dict, Union

import pymorphy2
from natasha import Segmenter, MorphVocab, NewsEmbedding, NewsNERTagger, NewsMorphTagger, NewsSyntaxParser, \
    NamesExtractor, DatesExtractor, MoneyExtractor, AddrExtractor, Doc
from razdel import sentenize


class NER_extractor:
    def __init__(self):
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()

        self.emb = NewsEmbedding()
        self.ner_tagger = NewsNERTagger(self.emb)

        self.morph = pymorphy2.MorphAnalyzer()

    def get_ner_elements(self, text_rus: str) -> List[Dict[str, Union[str, int]]]:
        """

        :param text_rus: Piece of text in string format. Can be sentence or whole article
        :return: List of dictionaries, each dictionary has form {"Normal span": str, "Type": str, "start": int,
        "end": int}, where Normal span - refer to normal form of marked word; Type - one of classes person,
        organization, location, time or money; start and end - number of characters in original text where token
        is located.
        """
        doc = Doc(text_rus)
        doc.segment(self.segmenter)
        doc.tag_ner(self.ner_tagger)

        for span in doc.spans:
            span.normalize(self.morph_vocab)

        spans_data = [{"Normal spans": self.morph.parse(span.normal)[0].normal_form, "Type": span.type, "start": span.start, "end": span.stop}
                      for span in doc.spans]

        return self.process_ners(spans_data, text_rus)

    def process_ners(self, spans_data, text):
        sentences = list(sentenize(text))
        processed_spans_data = {}
        for span_data in spans_data:
            span_object = {"Normal spans": span_data["Normal spans"], 'start': span_data["start"], 'end': span_data["end"], 'sentence':
                           self.get_sentence_with_fact(sentences, span_data)}
            if span_data["Type"] in processed_spans_data.keys():
                processed_spans_data[span_data["Type"]].append(span_object)
            else:
                processed_spans_data[span_data["Type"]] = [span_object]
        return processed_spans_data

    def get_sentence_with_fact(self, sentences, span):
        for sentence in sentences:
            if span['start'] >= sentence.start and span['end'] <= sentence.stop:
                return sentence.text
        return None