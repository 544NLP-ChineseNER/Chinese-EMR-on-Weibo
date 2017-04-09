# -*- coding: utf-8 -*-
import jieba
import multiprocessing
import os
import time

from logging import Logger
from gensim.corpora import WikiCorpus
from opencc import OpenCC
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence

from settings import config

class ChineseWikiTrain:
    def __init__(self,**kwargs):
        '''
        :param inp: (String) path of input file
        :param outp: (String) path of output file
        '''
        # self.logger = kwargs['logger']
        self.logger = Logger('train')
        self.input_path = kwargs.get("input",
                                     os.path.join(config.WORD2VEC_ROOT ,"zhwiki-latest-pages-articles.xml.bz2")
        self.output_path = kwargs.get("output", config.WORD2VEC_ROOT)

    def xml_to_txt(self):
        '''
        transfer xml version data into txt version
        '''
        self.logger.info("transfering xml to txt...")
        inp = self.input_path
        outp = os.path.join(self.output_path , "wiki.zh.text")
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
        inp = os.path.join(self.input_path, 'wiki.zh.text.simplified')
        output = os.path.join(self.output_path, 'wiki.zh.text.simplified_seg')

        log_f = open(output, "wb", encoding="utf-8")

        t1 = time.time()
        lines = open(inp, "rb", encoding="utf-8").readlines()
        for line in lines:
            words = " ".join(jieba.cut(line))
            log_f.write(words.encode('utf-8'))
        t2 = time.time()
        tm_cost = t2-t1
        self.logger.info('tokenization finished! time consumption:%s' %tm_cost)
        log_f.close()


    def train(self):
        '''
        train word2vec from wiki
        '''
        self.logger.info('start training...')
        inp = os.path.join(self.input_path, 'wiki.zh.text.simplified')
        outp1 = os.path.join(self.output_path, 'wiki.word2vec.model')

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