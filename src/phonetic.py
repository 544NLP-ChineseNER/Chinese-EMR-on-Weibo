import jellyfish
import re

from pypinyin import pinyin, lazy_pinyin

from src.common import CN_CHAR_REGEX

from settings import config

class PhoneticSubstitution:
    def __init__(self, *args, **kwargs):
        self.logger = kwargs['logger']
        try:
            self.name_dict = kwargs.get("person_name_dict")
        except KeyError as e:
            self.logger.warning(e + " is not provided when initializing PhoneticSubstitution.")

        self.mis_match_penalty = 4
        self.mis_match_similar_phone_penalty = 1
        self.ignore_phone_penalty = 3
        self.ignore_phone_list_penalty = 2

        self.similar_phones = {"SX", "JK", "LR", "IY", "FW", "MN"}
        self.ignore_phones = {"R", "Y"}


    def phone_edit_distance(self, str_a, str_b):
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

        if config.DEBUG:
            print(cn_str_a, cn_str_b)

        phone_a, phone_b = jellyfish.metaphone(cn_str_a), jellyfish.metaphone(cn_str_b)

        if config.DEBUG:
            print(phone_a, phone_b)

        edit_distance = self.phone_edit_distance(phone_a, phone_b)

        max_score = max(len(phone_a), len(phone_b)) * 4 - abs(len(phone_a) - len(phone_b))

        similarity = 1 - edit_distance / max_score

        return similarity


if __name__ == '__main__':
    py_converter = PhoneticSubstitution([])
    #print(py_converter.get_pinyin("菜English", space_seperated=True))
    print(py_converter.get_similarity_score(u"抖森", "Hiddlestondanger"))
    #print(py_converter.phone_edit_distance("KBBRYNT", "KBBLNT"))
