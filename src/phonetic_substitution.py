import heapq
import jellyfish
import os
import re

from pypinyin import pinyin, lazy_pinyin

from settings import config
from src.common import CN_CHAR_REGEX
from src.logger import Logger, EmptyLogger


class PhoneticSubstitution:
    def __init__(self, *args, **kwargs):
        self.logger = kwargs['logger']
        self.max_similar_names = kwargs.get('max_similar_names', 5)

        try:
            self.name_list = kwargs.get("name_list")
        except KeyError as e:
            if e == "logger":
                self.logger = EmptyLogger()
            elif e == "name_list":
                self.logger.warning(str(e) + " is not provided when initializing PhoneticSubstitution.")

        self.mis_match_penalty = 4
        self.mis_match_similar_phone_penalty = 1
        self.ignore_phone_penalty = 3
        self.ignore_phone_list_penalty = 2

        self.similar_phones = {"SX", "JK", "LR", "IY", "FW", "MN"}
        self.ignore_phones = {"R", "Y"}

        self.similarity_score_lower_bound = 0.75

    def _phone_edit_distance(self, str_a, str_b):
        '''
        Calculate string-edit-distance-like difference for two strings
        considering special conditions when translating phones from
        English to Chinese.
        :param str_a: (String) metaphone for a string
        :param str_b: (String) metaphone for the other string
        :return: (int) phone edit distance
        '''
        len_a, len_b = len(str_a), len(str_b)

        dp = [[0 for i in range(len_b + 1)] for j in range(len_a + 1)]

        for i in range(1, len_a + 1):
            dp[i][0] = self.ignore_phone_penalty * i

        for j in range(1, len_b + 1):
            dp[0][j] = self.ignore_phone_penalty * j

        for i in range(len_a):
            for j in range(len_b):
                ignore_a_penalty = self.ignore_phone_list_penalty if str_a[i] in self.ignore_phones else \
                                   self.ignore_phone_penalty
                ignore_b_penalty = self.ignore_phone_list_penalty if str_b[j] in self.ignore_phones else \
                                   self.ignore_phone_penalty
                match_penalty = 0 if str_a[i] == str_b[j] else \
                                self.mis_match_similar_phone_penalty \
                                    if "".join(sorted([str_a[i], str_b[j]])) in self.similar_phones else \
                                self.mis_match_penalty

                dp[i + 1][j + 1] = min(
                    ignore_a_penalty + dp[i][j + 1],
                    ignore_b_penalty + dp[i + 1][j],
                    match_penalty + dp[i][j]
                )

        return dp[len_a][len_b]

    def get_pinyin(self, characters, space_seperated=False):
        '''
        Convert Chinese characters to latin-style pinyin
        :param space_seperated: (Boolean) determiner for adding a space between output words
        :param characters: (String) Chinese characters
        :return: (String) converted pinyin, with a space between every character's pinyin
        '''

        result = []
        cur_alpha_str = []

        # convert every Chinese character to pinyin while leave others untouched
        for c in characters:
            if CN_CHAR_REGEX.match(c) is not None:
                if len(cur_alpha_str) > 0:
                    alpha_str = "".join(cur_alpha_str)
                    result.append(alpha_str)
                    cur_alpha_str = []
                result += lazy_pinyin(c)
            else:
                cur_alpha_str.append(c)

        if len(cur_alpha_str) > 0:
            alpha_str = "".join(cur_alpha_str)
            result.append(alpha_str)

        if space_seperated:
            return " ".join(result)

        return "".join(result)

    def _get_initial_pinyin_letter(self, characters):
        '''
        Convert Chinese characters into latin-style pinyin
        and get all initial letters for every pinyin
        :param characters: (Unicode String) Chinese characters
        :return: (String) Corresponding pinyin
        '''
        pinyin_string = self.get_pinyin(characters)
        return "".join([p[0] for p in pinyin_string.split(" ")])

    def get_similarity_score(self, str_a, str_b):
        '''
        Compare phonetic similarity of two strings.
        Input strings are converted into pinyin before comparing.
        :param str_a: (String) name entity
        :param str_b: (String) name entity
        :return: (float) Similarity score ranging between 0 to 1
        '''
        cn_str_a = self.get_pinyin("".join(str_a), space_seperated=False)
        cn_str_b = self.get_pinyin("".join(str_b), space_seperated=False)
        phone_a, phone_b = jellyfish.metaphone(cn_str_a), jellyfish.metaphone(cn_str_b)

        if config.DEBUG:
            print(phone_a, phone_b)

        # Calculate phone edit distance and phone similarity
        edit_distance = self._phone_edit_distance(phone_a, phone_b)
        max_score = max(len(phone_a), len(phone_b)) * 4 - abs(len(phone_a) - len(phone_b))
        similarity = 1 - edit_distance / max_score

        return similarity

    def get_similar_names(self, _name):
        '''
        Predict possible name for an entity morph
        :param _name: (String) name to compare
        :return:(Dict){<name>: <confidence score>, ...}
                       <name> : (String) name ofpossible entity morph
                       <confidence_score>: (float)
        '''

        if self.name_list is None:
            self.logger.error("name_dict is not initialized.")
            return

        # Use heap to store names with the highest score
        top_names = []

        for person_name in self.name_list:
            similarity_score = self.get_similarity_score(_name, person_name)
            if len(top_names) < self.max_similar_names:
                heapq.heappush(top_names, (similarity_score, person_name))
            else:
                if similarity_score > top_names[0][0]:
                    heapq.heappop(top_names)
                    heapq.heappush(top_names, (similarity_score, person_name))

        top_names = sorted(top_names, key=lambda x: x[0], reverse=True)

        return {name: score for (score, name) in top_names}


if __name__ == '__main__':
    logger = EmptyLogger()

    names = ['Eminem', "泰勒斯威夫特", "蕾哈娜", "酷玩", "Gotye", "ColdPlay", "贾斯汀比伯", "Drake",
             "恩雅", "老鹰", "Colben", "KitHarrington", "Chainsmokers", "GreenDay", "林肯公园"]

    py_converter = PhoneticSubstitution(logger=logger, name_list=names)
    print(py_converter.get_pinyin("菜English", space_seperated=True))

    #print(py_converter.get_similarity_score(u"泰勒斯威夫特", "泰勒十万伏特"))
    #print(py_converter.phone_edit_distance("KBBRYNT", "KBBLNT"))
    print(py_converter.get_similar_names("泰勒十万伏特"))
