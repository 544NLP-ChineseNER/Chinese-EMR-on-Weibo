from gensim.models import Word2Vec
from settings.config import WORD2VEC_ROOT
from src.logger import EmptyLogger
import os

class Characteristic:

    def __init__(self, *args, **kwargs):
        try:
            self.logger = kwargs['logger']
        except KeyError as e:
            self.logger = EmptyLogger()
        self.model = None
        self.load_model()

    def load_model(self):
        '''
        load the word2vec model
        :return:
        '''
        try:
            self.logger.info("[Characteristic] Loading word2vec model")
            self.model = Word2Vec.load(os.path.join(WORD2VEC_ROOT,'news.word2vec.model'))
            self.logger.info("[Characteristic] Loading completed")
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
            self.logger.info("[Characteristic] %s %s similarity: %f" %(w1,w2,similarity))
            return similarity
        except KeyError as e:
            self.logger.error(e)

    def get_related(self,word,N=20):
        '''
        :param word:
        :return: (list) a list of related words
        '''
        names = []
        try:
            self.logger.info("[Characteristic] %d related words of %s are as follows:" %(N,word))
            names = self.model.similar_by_word(word, topn=N)
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
        names = []
        res = {}
        try:
            self.logger.info("[Characteristic] Extacting possible name entities of: %s" %morph)
            names = self.model.similar_by_word(morph, topn=5)
        except KeyError as e:
            self.logger.error(e)
        for name in names:
            res[name[0]] = name[1]
        self.logger.info("[Characteristic] Possible name entities of %s are \n %s" %(morph,str(res)))
        return res


if __name__ == '__main__':
    c = Characteristic()
    query = "戚哥" #O'Neal
    query2 = "戚薇" #Kobe
    c.get_similar_names(query)
    c.get_related(query,10)
    c.get_similarity_score(query,query2)