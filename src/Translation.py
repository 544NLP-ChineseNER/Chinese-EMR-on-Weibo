from translate import Translator
import jieba

class Translation:
    def __init__(self):
        self.ec_translator = Translator(to_lang="zh")
        self.ce_translator = Translator(from_lang="zh",to_lang="en")
    
    def get_levenshtein_distance(self,str_a,len_a,str_b,len_b):
        '''
        :Calculate the levenshtein distance of two strings
        :param str_a: (String) first candidate string
        :param str_b: (String) second candidate string
        :param len_a: (int) length of substring of str_a being calculating
        :param len_b: (int) length of substring of str_b being calculating
        :return: (float) unnormalized levenshtein distance score
        '''
        cost = 0;
        
        #if anyone is empty
        if(len_a == 0):
            return len_b
        if(len_b == 0):
            return len_a
        
        #if last characters of the strings match
        if(str_a[len_a-1:len_a] == str_b[len_b-1:len_b]):
            cost = 0;
        else:
            cost = 1;
            
        #return the  minimum number of edits
        return min(self.get_levenshtein_distance(str_a, len_a-1, str_b,len_b)+1,self.get_levenshtein_distance(str_a,len_a,str_b,len_b-1)+1,self.get_levenshtein_distance(str_a,len_a-1,str_b,len_b-1)+cost)
        
    def calculate_similarity_score(self,str_a,str_b):
        '''
        Compute similarity of translted version of both entity
        :param str_a: (String) name entity
        :param str_b: (String) name entity
        :return: (float) Similarity score ranging between 0 to 1
        '''
        trans_a = self.ce_translator.translate(str_a).lower()
        trans_b = self.ce_translator.translate(str_b).lower()
        
        l_dist = self.get_levenshtein_distance(trans_a,len(trans_a),trans_b,len(trans_b))
        norm_l_dist = l_dist/max(len(trans_a),len(trans_b))
        return 1-norm_l_dist
        
    def get_similarity_score(self,str_a,str_b):
        '''
        Compute similarity of all possible combination of entity names and return the maximum score
        :param str_a: (String) entity morph
        :param str_b: (String) name entity
        :return: (float) Similarity score ranging between 0 to 1
        '''
        max=0
        if(self.calculate_similarity_score(str_a,str_b)>max):
            max = self.calculate_similarity_score(str_a,str_b)
        seg_list = jieba.cut(str_b)
        for i in seg_list:
            if(self.calculate_similarity_score(str_a,i)>max):
                max = self.calculate_similarity_score(str_a,i)
        return max

def main(defvals=None):
    l = Translation()
    #print(l.get_similarity_score("拉里大鸟","拉里伯德"))
    #print(l.calculate_similarity_score("大鸟","伯德"))
    print(l.ce_translator.translate("大鸟"))
    print(l.ce_translator.translate("伯德"))
        
if __name__=="__main__":
    main()