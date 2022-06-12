from typing import List, Dict, Union

from natasha import Segmenter, MorphVocab, NewsEmbedding, NewsNERTagger, NewsMorphTagger, NewsSyntaxParser, \
    NamesExtractor, DatesExtractor, MoneyExtractor, AddrExtractor, Doc


class NER_extractor:
    def __init__(self):
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()

        self.emb = NewsEmbedding()
        self.ner_tagger = NewsNERTagger(self.emb)

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

        spans_data = [{"Normal spans": span.normal, "Type": span.type, "start": span.start, "end": span.stop}
                               for span in doc.spans]

        return spans_data