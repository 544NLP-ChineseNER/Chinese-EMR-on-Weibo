# -*- coding: utf-8 -*-
from nltk.tag import StanfordNERTagger
from settings import config
import logging
import os
import jieba

class ChineseNER:

	def __init__(self, *args, **kwargs):
		self.model_path = os.path.join(config.MEDIA_ROOT,'dicts/ner/classifiers/chinese.misc.distsim.crf.ser.gz')
		self.ner_jar_path = os.path.join(config.MEDIA_ROOT,'dicts/ner/stanford-ner.jar')
		self.ner = StanfordNERTagger(self.model_path,self.ner_jar_path)
		# self.logger = logging.Logger('ner')
		self.logger = kwargs['logger']
		self.CLASS = ['LOCATION','PERSON','ORGANIZATION','MISC','MONEY','PERCENT','DATE','TIME']
		pass

	def extract_from_list(self,l):
		'''
		extract named entity from a segmented word list eg:['我','爱','中国']
		'''
		res = []
		raw = self.ner.tag(l)
		for r in raw:
			print(r[0]," ",r[1])
			if r[1] in self.CLASS:
				res += [r[0]]
		return res

if __name__ == '__main__':
	s = "来自中国的小巨人姚明和鲨鱼奥尼尔的对决令人期待。"
	ner = ChineseNER()
	l = [i for i in jieba.cut(s)]
	print(ner.extract_from_list(l))