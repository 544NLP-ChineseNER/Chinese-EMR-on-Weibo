 #-*- coding: UTF-8 -*-   
import heapq
from urllib.request import urlopen,quote
import json

class Translation:
    def __init__(self,namelist):
        #self.logger = kwargs['logger']
        #self.ce_translator = Translator(from_lang="zh",to_lang="en")
        self.name_list = namelist
        self.url = ""
        self.treshold = 10

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
        max=0
        #eng_part = Translator(from_lang="zh",to_lang="en").translate(str_b)
        #ch_part = Translator(from_lang="zh",to_lang="en").translate(str_a)
        eng_part = json.loads(urlopen(self.set_url(str_b)).read().decode("utf-8").encode("utf-8"))['translation'][0]
        ch_part = json.loads(urlopen(self.set_url(str_a)).read().decode("utf-8").encode("utf-8"))['translation'][0]

        if(self.calculate_similarity_score(eng_part,ch_part)>max):
            max = self.calculate_similarity_score(eng_part,ch_part)

        seg_list = eng_part.split(" ")
        for i in seg_list:
            if(self.calculate_similarity_score(ch_part,i)>max):
                max = self.calculate_similarity_score(ch_part,i)
        return max

        #return self.calculate_similarity_score(eng_part,ch_part)

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
            score = self.get_similarity_score(name,name_entity)
            if len(poss_names) < self.treshold:
                heapq.heappush(poss_names,(score,name_entity))
            else:
                if score > poss_names[0][0]:
                    heapq.heappop(poss_names)
                    heapq.heappush(poss_names,(score,name_entity))

        poss_names = sorted(poss_names, key=lambda x: x[0], reverse=True)

        return {name: score for (score, name) in poss_names}



            

def main(defvals=None):
    names = ["泰勒斯威夫特", "蕾哈娜", "酷玩", "贾斯汀比伯", "恩雅", "老鹰", "林肯公园","拉里伯德"]
    l = Translation(names)
    #name = quote('大鸟')
    #print(name)
    #result = urlopen("http://fanyi.youdao.com/openapi.do?keyfrom=csci544project&key=1099532634&type=data&doctype=json&version=1.1&q="+name).read().decode("utf-8").encode("utf-8")
    #print(json.loads(result)['translation'][0])
    #print(l.get_similar_names("鸟儿"))
    #print(l.get_similarity_score("鸟","拉里伯德"))
    #print(l.calculate_similarity_score("larry bird","the bird"))
    #print(json.loads(urlopen(l.set_url("拉里伯德")).read().decode("utf-8").encode("utf-8"))['translation'][0])
    #print(l.ce_translator.translate("伯德"))
    #print(Translator(from_lang="zh",to_lang="en").translate("伯德"))
        
if __name__=="__main__":
    main()