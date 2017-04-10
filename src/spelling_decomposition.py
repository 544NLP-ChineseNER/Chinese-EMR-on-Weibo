import json
import os

from settings import config
from src.logger import Logger, EmptyLogger
from src.common import CN_CHAR_REGEX

class SpellingDecomposition:
    def __init__(self, *args, **kwargs):

        self.logger = kwargs['logger']
        self.use_raw_dict = kwargs.get('use_raw_dict', True)

        self.decomposition_dict, self.inverse_decomposition_dict = {}, {}
        # Read decomposition dict
        try:
            if self.use_raw_dict:
                file_handler = open(os.path.join(config.SPELLING_ROOT, "division_raw.txt"), encoding='utf-8')
                self._load_raw_dict(file_handler)
                file_handler.close()
            else:
                with open(os.path.join(config.DICT_ROOT, "word_division_dict"), encoding='utf-8') as f:
                    self.decomposition_dict = json.load(f)
        except FileExistsError as e:
            self.logger.error("word_division_dict does not exist. Division dictionary not loaded.")
        except json.decoder.JSONDecodeError as e:
            self.logger.error("Error while parsing division dictionary from word_division_dict.")

        self.stem_similar_chars = {}
        # Read stem_similar_characters_dict
        try:
            file_handler = open(os.path.join(config.SPELLING_ROOT, "division_raw.txt"), encoding='utf-8')
            self._load_raw_dict(file_handler)
            file_handler.close()
        except FileExistsError as e:
            self.logger.warning("stem_similar_characters_dict does not exist.")
        except SyntaxError as e:
            self.logger.error("Error while parsing division dictionary from word_division_dict.")


    def _load_stem_character_dict(self, file_handler):
        '''
        Load character division from division_raw.txt
        :param file_handler: (Python file handler)
        :return: None
        '''
        for line in file_handler:
            cn_character = CN_CHAR_REGEX.findall(line)
            character = cn_character[0]
            stems = cn_character[1:]
            self.decomposition_dict[character] = stems


    def _load_raw_dict(self, file_handler):
        '''
        Load similar character for stems from division_raw.txt
        :param file_handler: (Python file handler)
        :return: None
        '''
        for line in file_handler:
            cn_character = CN_CHAR_REGEX.findall(line)
            if len(cn_character) > 1:
                ori_char = cn_character[0]
                decomp_chars = "".join(cn_character[1:])
                self.decomposition_dict[ori_char] = decomp_chars
                if decomp_chars not in self.inverse_decomposition_dict:
                    self.inverse_decomposition_dict[decomp_chars] = [ori_char]
                else:
                    self.inverse_decomposition_dict[decomp_chars].append(ori_char)


    def get_similarity_score(self, str_a, str_b):
        '''

        :param str_a: (String) name entity or morph
        :param str_b: (String) name entity or morph
        :return: (float) similarity score.
                         Since Spelling decomposition is deterministic about whether two spellings
                         are exactly the same, the score would be either 0 or 1.
        '''

        if str_a == str_b:
            return 1.0

        # Since spelling decomposition is specifically designed for Chinese characters
        # All non_chinese characters will be filtered out before processing
        str_a = "".join(CN_CHAR_REGEX.findall(str_a))
        str_b = "".join(CN_CHAR_REGEX.findall(str_b))



    def get_similar_names(self, name):
        pass


if __name__ == "__main__":
    empty_logger = EmptyLogger()
    spd = SpellingDecomposition(logger=empty_logger, use_raw_dict=True)