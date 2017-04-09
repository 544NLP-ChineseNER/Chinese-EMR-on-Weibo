# -*- coding: utf-8 -*-
from logging import Logger
from gensim.corpora import WikiCorpus
from opencc import OpenCC
import time
import jieba

import multiprocessing

from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence


class ChineseWikiTrain:
    def __init__(self,**kwargs):
        '''
        :param inp: (String) path of input file
        :param outp: (String) path of output file
        '''
        # self.logger = kwargs['logger']
        self.logger = Logger('train')
        if('input' not in kwargs):	self.input_path = "../../media/word2vec/zhwiki-latest-pages-articles.xml.bz2"
        else:	self.input_path = kwargs['input']
        if('ouput' not in kwargs):	self.output_path = "../../media/word2vec/"
        else:	self.output_path = kwargs['out']

    def xml_to_txt(self):
        '''
        transfer xml version data into txt version
        '''
        self.logger.info("transfering xml to txt...")
        inp = self.input_path
        outp = self.output_path + "wiki.zh.text"
        space = " "
        i = 0
        output = open(outp, 'w')
        wiki = WikiCorpus(inp, lemmatize=False, dictionary={})
        texts = wiki.get_texts()
        for text in texts:
            # print((text[0]).decode("utf-8"))
            # exit()
            output.write(space.join([t.decode('utf-8') for t in text]) + "\n")
            i = i + 1
            if (i % 10000 == 0):
                self.logger.info("Saved " + str(i) + " articles")
        output.close()
        self.logger.info("Finished Saved " + str(i) + " articles")

    def trad_to_simp(self):
        '''
        convert Chinese traditioinal characters into simplified ones.
        '''
        self.logger.info('convertion start...')
        openCC = OpenCC('t2s') # convert from Traditional Chinese to Simplified Chinese
        f = open(self.output_path+"wiki.zh.text",'r')
        lines = f.readlines()
        s = open(self.output_path+"wiki.zh.text.simplified",'w')
        for line in lines:
            converted = openCC.convert(line)
            s.write(converted)
        s.close()
        f.close()
        self.logger.info('convertion finished!')

    def tokenize(self):
        '''
        tokenize sentence into words
        '''
        self.logger.info('tokenization start...')
        jieba.enable_parallel(8)
        inp = self.output_path + 'wiki.zh.text.simplified'
        output = self.output_path + 'wiki.zh.text.simplified_seg'
        log_f = open(output,"wb")

        t1 = time.time()
        lines = open(inp,"rb").readlines()
        for line in lines:
            words = " ".join(jieba.cut(line))
            log_f.write(words.encode('utf-8'))
        t2 = time.time()
        tm_cost = t2-t1
        self.logger.info('tokenization finished! time consumption:%s' %tm_cost)

    def train(self):
        '''
        train word2vec from wiki
        '''
        self.logger.info('start training...')
        inp = self.output_path + 'wiki.zh.text.simplified'
        outp1 = self.output_path + 'wiki.word2vec.model'

        model = Word2Vec(LineSentence(inp), size=300, window=5, min_count=5,
                         workers=multiprocessing.cpu_count(), iter=3)

        model.save(outp1)
        self.logger.info('training finished!')

if __name__ == '__main__':
    t = ChineseWikiTrain()
    t.xml_to_txt()
    t.trad_to_simp()
    t.tokenize()
    t.train()