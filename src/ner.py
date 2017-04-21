# -*- coding: utf-8 -*-
from nltk.tag import StanfordNERTagger
from settings import config
import logging
import os
import jieba

class ChineseNER:
    def __init__(self, *args, **kwargs):
        self.model_path = os.path.join(config.NER_ROOT, 'classifiers/chinese.misc.distsim.crf.ser.gz')
        self.ner_jar_path = os.path.join(config.NER_ROOT, 'stanford-ner.jar')
        self.ner = StanfordNERTagger(self.model_path, self.ner_jar_path)
        self.logger = logging.Logger('ner')
        # self.logger = kwargs['logger']
        self.CLASS = ['LOCATION', 'PERSON', 'ORGANIZATION', 'MISC', 'MONEY', 'PERCENT', 'DATE', 'TIME']
        pass

    def extract_from_list(self, l):
        '''
        extract named entity from a segmented word list eg:['我','爱','中国']
        :param l: 
        :return: 
        '''
        res = []
        raw = self.ner.tag(l)
        for r in raw:
            print(r[0], " ", r[1])
            if r[1] in self.CLASS:
                res += [r[0]]
        return res

    def extract_name_entities_from_sentence(self, s):
        '''
        Extract name entities from a sentence.
        :param s: (UTF-8 or Unicode String) sentence text in Chinese
        :return: (List[String]) name entites extracted from sentence
        '''
        l = [i for i in jieba.cut(s)]
        res = self.extract_from_list(l)

        return res


if __name__ == '__main__':
    s = "来自中国的小巨人姚明和鲨鱼奥尼尔的对决令人期待。"
    ner = ChineseNER()
    print(ner.extract_name_entities_from_sentence(s))
