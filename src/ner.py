# -*- coding: utf-8 -*-
from nltk.tag import StanfordNERTagger
from settings import config
import logging
import os
import jieba
import jieba.posseg as pseg

class ChineseNER:
    def __init__(self, *args, **kwargs):
        self.model_path = os.path.join(config.NER_ROOT, 'classifiers/chinese.misc.distsim.crf.ser.gz')
        self.ner_jar_path = os.path.join(config.NER_ROOT, 'stanford-ner.jar')
        self.ner = StanfordNERTagger(self.model_path, self.ner_jar_path)
        self.logger = logging.Logger('ner')
        # self.logger = kwargs['logger']
        self.CLASS = ['LOCATION', 'PERSON', 'ORGANIZATION', 'MISC', 'MONEY', 'PERCENT', 'DATE', 'TIME']
        self.PATTERNS = ['_n_n_nr', '_b_nr_d', '_nr_s', '_n_s', '_a_nr_c', '_a_nr_v', '_nr_r', '_nr_v', \
         '_n_r', '_nr_n_uj', '_m_ns_x', '_j_n_zg', '_n_c', '_a_ng_x', '_g_ng_n_c', '_nr_n_v', '_g_ng_n_v', \
          '_nr_n', '_nr_uj', '_nr_m', '_nrt_uj', '_nrt_x', '_a_n_d', '_r_n_c', '_n_l', '_nrt_x_nr_d', \
          '_nr_l', '_nr_d', '_a_n_nr', '_nrt_p', '_nr_a', '_ns_nrt_x', '_a_ng_y']

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

    def extract_morph(self,s,patterns):
        '''
        Extract morph from a sentence by pos patterns
        :param s:  (UTF-8 or Unicode String) sentence text in Chinese
               patterns:    pos patterns to match
        :return:    (List[String]) morphs extracted from sentence
        '''
        words = pseg.cut(s)
        tag_seg = ""
        word_list = []
        res = []
        for word, tag in words:
            tag_seg += "_" + tag
            word_list += [word]
        for pattern in patterns:
            temp = self.match(pattern,tag_seg,word_list)
            # print(temp)
            res += temp
        return list(set(res))

    def match(self,pattern,tag_seg,word_list):
        '''
        match pattern in tag_seg and return matched word list
        '''
        res = []
        wIndex = 0
        pattern_tag_count = len(pattern.split("_")) - 1
        # print(pattern)
        while tag_seg.find(pattern) >=0:
            front = tag_seg.find(pattern)
            wIndex += len(tag_seg[:front].split("_")) - 1
            # print("wIndex:" + str(wIndex))
            morph = ""
            for i in range(wIndex,wIndex+pattern_tag_count-1):
                morph += word_list[i]
            if len(morph <=3)
                res += [morph]
            wIndex += pattern_tag_count
            tag_seg = tag_seg[(front+len(pattern)):]
            # print(tag_seg)
            # print(tag_seg.find(pattern))
        return res


if __name__ == '__main__':
    s = "来自中国的小巨人姚明和浓眉哥的对决令人期待。"
    s = "到手了！終於到達小妹的手上了"
    # s = "我觉得把何老师搞辞职的那位教授的朋友们要斟酌一下自己交的友了"
    # s = "张大仙@张智霖 说：每次吵架我都会想到我失去她会怎样"
    ner = ChineseNER()
    # print(ner.extract_name_entities_from_sentence(s))
    print(ner.extract_morph(s,patterns))
