 #-*- coding: UTF-8 -*-   
import heapq
from urllib.request import urlopen,quote
import json
import enchant

from src.logger import Logger, EmptyLogger

class Translation:
    def __init__(self, *args, **kwargs):


        try:
            self.name_list = kwargs.get("name_list")
            self.logger = kwargs['logger']
        except KeyError as e:
            if e == "logger":
                self.logger = EmptyLogger()
            elif e == "name_list":
                self.logger.warning(str(e) + " is not provided when initializing Translation.")

        self.url = ""
        self.treshold = 10
        self.poss_names = []
        self.dict = enchant.Dict("en_US")

    def set_url(self,name):
        self.url = "http://fanyi.youdao.com/openapi.do?keyfrom=csci544project&key=1099532634&type=data&doctype=json&version=1.1&q="+quote(name)
        return self.url

    def get_levenshtein_distance(self,str_a,len_a,str_b,len_b):
        '''
        :Calculate the levenshtein distance of two strings
        :param str_a: (String) first candidate string
        :param str_b: (String) second candidate string
        :param len_a: (int) length of substring of str_a being calculating
        :param len_b: (int) length of substring of str_b being calculating
        :return: (float) unnormalized levenshtein distance score
        '''
        dp = [[0 for x in range(len_b+1)] for x in range(len_a+1)]
        for i in range(len_a+1):
            for j in range(len_b+1):
                if i==0:
                    dp[i][j] = j
                elif j==0:
                    dp[i][j] = i
                elif str_a[i-1] == str_b[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1+ min(dp[i][j-1],dp[i-1][j],dp[i-1][j-1])
        return dp[len_a][len_b]
    def calculate_similarity_score(self,str_a,str_b):
        '''
        Compute similarity of translted version of both entity
        :param str_a: (String) name entity
        :param str_b: (String) name entity
        :return: (float) Similarity score ranging between 0 to 1
        '''
        #trans_a = self.ce_translator.translate(str_a).lower()
        #trans_b = self.ce_translator.translate(str_b).lower()
        
        l_dist = self.get_levenshtein_distance(str_a,len(str_a),str_b,len(str_b))
        norm_l_dist = l_dist/max(len(str_a),len(str_b))
        return 1-norm_l_dist
        
    def get_similarity_score(self,str_a,str_b):
        '''
        Compute similarity of all possible combination of entity names and return the maximum score
        :param str_a: (String) entity morph
        :param str_b: (String) name entity
        :return: (float) Similarity score ranging between 0 to 1
        '''
        maxi = 0.0
        # eng_part = Translator(from_lang="zh",to_lang="en").translate(str_b)
        # ch_part = Translator(from_lang="zh",to_lang="en").translate(str_a)
        eng_part = json.loads(urlopen(self.set_url(str_b)).read().decode("utf-8").encode("utf-8"))['translation'][0]
        ch_part = json.loads(urlopen(self.set_url(str_a)).read().decode("utf-8").encode("utf-8"))['translation'][0]

        maxi = max(maxi, self.calculate_similarity_score(eng_part, ch_part))

        seg_list = eng_part.split(" ")
        for i in seg_list:
            maxi = max(maxi, self.calculate_similarity_score(ch_part, i))
        return maxi

        #return self.calculate_similarity_score(eng_part,ch_part)

    def get_similar_names(self, name):
        '''
        Predict top 10 of possible name from celevrity list for an entity morph
        :param name: the given morph
        :return:(Dict){<name>: <confidence score>, ...}
                       <name> : (String) name ofpossible entity morph
                       <confidence_score>: (float)
        '''
        eng_name = json.loads(urlopen(self.set_url(name)).read().decode("utf-8").encode("utf-8"))['translation'][0];
        splitted_word = eng_name.split(" ")
        #splitted_word = ["tiger"]
        position = len(splitted_word)
        for word in splitted_word:
            self.get_word_score(word,position,0)
            ed1 = self.edit1(word)
            for ed in ed1:
                if self.dict.check(ed):
                    self.get_word_score(ed,position,1)
            position-=1
        self.poss_names = sorted(self.poss_names, key=lambda x: x[0], reverse=True)

        return {name: score for (score, name) in self.poss_names[:5]}

    def get_word_score(self,word,position,ed):
        sim = 1-ed/len(word)
        translate = json.loads(urlopen(self.set_url(word)).read().decode("utf-8").encode("utf-8"))
        if 'basic' in translate:
            explains = translate['basic']['explains']
            print(explains)
            for ex in explains:
                exs = ex.split("；")
                if '人名' in exs[0]:
                    for x in range(1, len(exs)):
                        heapq.heappush(self.poss_names, (1/position*sim,exs[x][exs[x].find(")") + 1:]))
        return

    def edit1(self,word):
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i],word[i:]) for i in range(len(word)+1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes+transposes+replaces+inserts)

def main(defvals=None):
    names = ["泰勒斯威夫特", "蕾哈娜", "酷玩", "贾斯汀比伯", "恩雅", "老鹰", "林肯公园","拉里伯德","泰格伍兹"]
    l = Translation(name_list=names)
    #name = quote('大鸟')
    #print(name)
    #result = urlopen("http://fanyi.youdao.com/openapi.do?keyfrom=csci544project&key=1099532634&type=data&doctype=json&version=1.1&q="+name).read().decode("utf-8").encode("utf-8")
    #print(json.loads(result)['translation'][0])
    print(l.get_similar_names("鸟"))
    #print(l.get_similarity_score("鸟","拉里伯德"))
    #print(l.calculate_similarity_score("larry bird","the bird"))
    #print(json.loads(urlopen(l.set_url("老虎")).read().decode("utf-8").encode("utf-8"))['translation'][0])
    #x = json.loads(urlopen(l.set_url("tiger")).read().decode("utf-8").encode("utf-8"))['basic']['explains'][1].split("；")[1]
    #print(x[x.find(")")+1:])
    #print(l.ce_translator.translate("伯德"))
    #print(Translator(from_lang="zh",to_lang="en").translate("伯德"))
        
if __name__=="__main__":
    main()