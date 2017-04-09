import json
import os

from settings import config
from src.logger import Logger, EmptyLogger

class SpellingDecomposition:
    def __init__(self, *args, **kwargs):

        self.logger = kwargs['logger']
        self.division_dict = None

        try:
            with open(os.path.join(config.DICT_ROOT, "word_division_dict"), encoding='utf-8') as f:
                self.division_dict = json.load(f)
        except FileExistsError as e:
            self.logger.error("word_division_dict does not exist. Division dictionary not loaded.")
        except json.decoder.JSONDecodeError as e:
            self.logger.error("Error while parsing division dictionary from word_division_dict.")

    def get_similarity_score(self, str_a, str_b):
        '''

        :param str_a: (String) name entity or morph
        :param str_b: (String) name entity or morph
        :return: (float) similarity score.
                         Since Spelling decomposition is deterministic about whether two spellings
                         are exactly the same, the score would be either 0 or 1.
        '''


    def get_similar_names(self, name):
        pass

