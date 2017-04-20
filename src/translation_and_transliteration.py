# -*- coding: UTF-8 -*-
from translate import Translator
import heapq


class Translation:
    def __init__(self, namelist):
        # self.logger = kwargs['logger']
        self.ec_translator = Translator(to_lang="zh")
        self.ce_translator = Translator(from_lang="zh", to_lang="en")

        self.name_list = namelist
        self.threshold = 10

    def get_levenshtein_distance(self, str_a, len_a, str_b, len_b):
        '''
        :Calculate the levenshtein distance of two strings
        :param str_a: (String) first candidate string
        :param str_b: (String) second candidate string
        :param len_a: (int) length of substring of str_a being calculating
        :param len_b: (int) length of substring of str_b being calculating
        :return: (float) unnormalized levenshtein distance score
        '''
        cost = 0

        # if anyone is empty
        if len_a == 0:
            return len_b
        if len_b == 0:
            return len_a

        # if last characters of the strings match
        if (str_a[len_a - 1:len_a] == str_b[len_b - 1:len_b]):
            cost = 0
        else:
            cost = 1

        # return the  minimum number of edits
        return min(self.get_levenshtein_distance(str_a, len_a - 1, str_b, len_b) + 1,
                   self.get_levenshtein_distance(str_a, len_a, str_b, len_b - 1) + 1,
                   self.get_levenshtein_distance(str_a, len_a - 1, str_b, len_b - 1) + cost)

    def calculate_similarity_score(self, str_a, str_b):
        '''
        Compute similarity of translted version of both entity
        :param str_a: (String) name entity
        :param str_b: (String) name entity
        :return: (float) Similarity score ranging between 0 to 1
        '''
        trans_a = self.ce_translator.translate(str_a).lower()
        trans_b = self.ce_translator.translate(str_b).lower()

        l_dist = self.get_levenshtein_distance(trans_a, len(trans_a), trans_b, len(trans_b))
        norm_l_dist = l_dist / max(len(trans_a), len(trans_b))
        return 1 - norm_l_dist

    def get_similarity_score(self, str_a, str_b):
        '''
        Compute similarity of all possible combination of entity names and return the maximum score
        :param str_a: (String) entity morph
        :param str_b: (String) name entity
        :return: (float) Similarity score ranging between 0 to 1
        '''
        max_score = 0
        if self.calculate_similarity_score(str_a, str_b) > max_score:
            max_score = self.calculate_similarity_score(str_a, str_b)
        eng_part = self.ce_translator.translate(str_b)
        ch_part = self.ce_translator.translate(str_a)
        seg_list = eng_part.split(" ")
        for i in seg_list:
            if self.calculate_similarity_score(str_a, i) > max_score:
                max_score = self.calculate_similarity_score(str_a, i)
            if self.calculate_similarity_score(ch_part, i) > max_score:
                max_score = self.calculate_similarity_score(ch_part, i)
        return max_score

    def get_similar_names(self, name):
        '''
        Predict top 10 of possible name from celevrity list for an entity morph
        :param name: the given morph
        :return:(Dict){<name>: <confidence score>, ...}
                       <name> : (String) name ofpossible entity morph
                       <confidence_score>: (float)
        '''
        poss_names = []
        for name_entity in self.name_list:
            score = self.get_similarity_score(name, name_entity)
            if len(poss_names) < self.threshold:
                heapq.heappush(poss_names, (score, name_entity))
            else:
                if score > poss_names[0][0]:
                    heapq.heappop(poss_names)
                    heapq.heappush(poss_names, (score, name_entity))

        poss_names = sorted(poss_names, key=lambda x: x[0], reverse=True)

        return {name: score for (score, name) in poss_names}


def main(defvals=None):
    names = ["泰勒斯威夫特", "蕾哈娜", "酷玩", "贾斯汀比伯", "恩雅", "老鹰", "林肯公园", "拉里伯德"]
    l = Translation(names)
    print(l.get_similar_names("鸟儿"))
    # print(l.get_similarity_score("鸟儿","拉里伯德"))
    # print(l.ce_translator.translate("伯德"))


if __name__ == "__main__":
    main()
