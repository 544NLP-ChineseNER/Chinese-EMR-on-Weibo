import json
import os

from settings import config
from src.logger import Logger, EmptyLogger
from src.common import CN_CHAR_REGEX

class SpellingDecomposition:
    def __init__(self, *args, **kwargs):

        self.logger = kwargs['logger']
        self.use_raw_dict = kwargs.get('use_raw_dict', True)

        self.name_list = kwargs.get('name_list', None)
        if self.name_list is None:
            self.logger.warning("name_list is not provided when initialing Spelling Decomposition. "
                                "Use default dict instead.")


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
            file_handler = open(os.path.join(config.SPELLING_ROOT, "stem_similar_characters.txt"), encoding='utf-8')
            self._load_stem_character_dict(file_handler)
            file_handler.close()
        except FileExistsError as e:
            self.logger.warning("stem_similar_characters_dict does not exist.")
        except SyntaxError as e:
            self.logger.error("Error while parsing division dictionary from word_division_dict.")

        #print(self.inverse_decomposition_dict["月月"])

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

        :param str_a: (String) name entity
        :param str_b: (String) morph
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

        # Here we assume there's no spelling decomposition element in name entity
        # so only deal with morph here.
        morphs = self._get_name_entities(str_b)

        if str_a in morphs:
            return 1.0
        else:
            return 0.0

    def _get_name_entities(self, morph):
        '''
        Generate all possible name entities from morph,
        regardless of whether the name is in name_list or not.
        :param morph: (String) morph
        :return: (List[String]) List of name entities
        '''

        possible_entities = set()
        possible_entities.add(morph)
        morphs = [morph]

        while len(morphs) > 0:
            cur_morph = morphs.pop()
            res = self._combine_characters(cur_morph, 0, "")
            for r in res:
                if r not in possible_entities:
                    possible_entities.add(r)
                    morphs.append(r)

        return possible_entities

    def _combine_characters(self, s, pos, cur_str):
        '''
        :param s: (String)
        :param pos: (int) current pointer to string s
        :param cur_str: (String) processed string so far
        :return: (List[String] combined characters)
        '''
        if pos == len(s):
            return [cur_str]

        # Recursively look for characters that can be combined
        # using greedy method.
        res = []
        res += self._combine_characters(s, pos + 1, cur_str + s[pos])
        for i in range(2, 5):
            if pos + i > len(s):
                break
            comb_str = "".join(s[pos : pos + i])
            if comb_str in self.inverse_decomposition_dict:
                for comb in self.inverse_decomposition_dict[comb_str]:
                    res += self._combine_characters(s, pos + i, cur_str + comb)

        return res


    def get_similar_names(self, name):
        '''
        Predict possible name for an entity morph
        :param _name: (String) name to compare
        :return:(Dict){<name>: <confidence score>, ...}
                       <name> : (String) name ofpossible entity morph
                       <confidence_score>: (float)
        '''
        if self.name_list is None:
            self.logger.error("name_list not provided when initializing spelling decomposition")
            return None

        names = self._get_name_entities(name)
        return {name: 1 for name in names if name in self.name_list}



if __name__ == "__main__":
    empty_logger = EmptyLogger()
    name_list = ["Bakery", "和谐社会", "李鹏", "李咏", "这是啥啊", "Barack Obama"]
    #   [Bakery, Harmonic Society, Peng Li (A former Chinese leader), Yong Li (Famous host), WhatIsDat, Barack Obama
    spd = SpellingDecomposition(logger=empty_logger, use_raw_dict=True, name_list=name_list)

                                # Li Moon Moon Bird
                                # Moon Moon Bird => Name of a huge bird
                                # Moon Moon   => Friend
    print(spd.get_similar_names("李月月鸟"))
