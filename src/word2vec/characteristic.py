from gensim.models import Word2Vec
import logging
import sys
import os
sys.path.append('../../')
from settings.config import WORD2VEC_ROOT

class Characteristic:

    def __init__(self, *args, **kwargs):
        # self.logger = kwargs['logger']
        self.model = None
        self.logger = logging.Logger('characteristic')

    def load_model(self):
        '''
        load the word2vec model
        :return:
        '''
        try:
            self.model = Word2Vec.load(os.path.join(WORD2VEC_ROOT,'wiki.word2vec.model'))
        except FileNotFoundError as e:
            self.logger.error(e)
            raise


    def get_similarity_score(self,w1,w2):
        '''
        Calculate the characteristic similarity of name entity
        :param w1: (String) the first word to calculate similarity
        :param w2: (String) the second word to calculate similarity
        :return: (Double) similarity of the two words
        '''
        try:
            similarity = self.model.wv.similarity(w1,w2)
            print(w1,w2,'similarity:',similarity)
            return similarity
        except KeyError as e:
            self.logger.error(e)

    def get_related(self,word):
        '''
        :param word:
        :return: (list) a list of related words
        '''
        try:
            names = self.model.similar_by_word(word, topn=500)
        except KeyError as e:
            self.logger.error(e)
        for name in names:
            print(name[0], ' ', name[1])
        return names

    def get_similar_names(self,morph):
        '''
        Recognize morph
        :param morph:
        :return: (list) a list of possible objects of the morph
        '''
        pass


if __name__ == '__main__':
    c = Characteristic()
    c.load_model()
    query = "姚明"
    query2 = "杨幂"
    c.get_related(query)
    c.get_similarity_score(query,query2)