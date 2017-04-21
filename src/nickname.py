import jieba
import os

from settings import config


class NicknameGeneration:
    stopwords = ["阿", "哥", "姐", "弟", "爷", "叔", "姑", "婆", "大", "小", "老", "太"]

    def __init__(self, *args, **kwargs):
        pass

    def calculate_similarity_score(self, str_a, str_b):
        '''
        Compute similarity of translted version of both entity
        :param str_a: (String) name entity
        :param str_b: (String) name entity
        :return: (float) Similarity score ranging between 0 to 1
        '''
        trans_a = self.ce_translator.translate(str_a).lower()
        trans_b = self.ce_translator.translate(str_b).lower()

        l_dist = self.get_levenshtein_distance(trans_a, len(trans_a), trans_b, len(trans_b))
        norm_l_dist = l_dist / max(len(trans_a), len(trans_b))
        return 1 - norm_l_dist

    def get_similarity_score(self, str_a, str_b):
        '''
        Compute similarity of all possible combination of entity names and return the maximum score
        :param str_a: (String) entity morph
        :param str_b: (String) name entity
        :return: (float) Similarity score ranging between 0 to 1
        '''
        max = 0
        if self.calculate_similarity_score(str_a, str_b) > max:
            max = self.calculate_similarity_score(str_a, str_b)
        seg_list = jieba.cut(str_b)
        for i in seg_list:
            if self.calculate_similarity_score(str_a, i) > max:
                max = self.calculate_similarity_score(str_a, i)
        return max

    def nb_learn(self, training_file):
        prior = {}
        likelihood = {}
        with open(training_file, "r", encoding='UTF-8') as inFile:
            data = inFile.read()
        line = data.splitlines()
        size = len(line)
        for l in line:
            wordlist = l.split(' ')
            if wordlist[1] not in prior:
                prior[wordlist[1]] = 1.0
            else:
                prior[wordlist[1]] += 1
            outerkey = wordlist[1]
            innerkey = wordlist[0]
            likelihood[outerkey] = likelihood.get(outerkey, {})
            likelihood[outerkey][innerkey] = likelihood[outerkey].get(innerkey, 0.0)
            likelihood[outerkey][innerkey] += 1
        # Prior probability
        for key in prior:
            prior[key] /= size
        # Convert to probability
        for key in likelihood:
            di = likelihood[key]
            s = sum(di.values())
            for innkey in di:
                di[innkey] /= s
            likelihood[key] = di
        return prior, likelihood

    def nb_classify(self, name_entity, morph, prior, likelihood):
        max_likelihood = 0.0
        result = name_entity[0]
        for name in name_entity:
            outerkey = name
            innerkey = morph
            prior[outerkey] = prior.get(outerkey, 0.0)
            likelihood[outerkey] = likelihood.get(outerkey, {})
            likelihood[outerkey][innerkey] = likelihood[outerkey].get(innerkey, 0.0)
            p_likelihood = likelihood[outerkey][innerkey]
            p = prior[name] * p_likelihood
            if p > max_likelihood:
                result = name
                max_likelihood = p
        return result

    def nickname_generation(self, _name):
        with open(os.path.join(config.DICT_ROOT, "celebrity.txt"), "r", encoding='UTF-8')as infile:
            data = infile.read()
        line = data.splitlines()
        name_entity = []
        for l in line:
            for index in _name:
                if index in l and index not in self.stopwords and l not in name_entity:
                    name_entity.append(l)
        return name_entity

    def find_amount(self, name, morph, file):
        with open(file, "r", encoding='UTF-8') as inFile:
            data = inFile.read()
        line = data.splitlines()
        name_num = 0.0
        morph_num = 0.0
        for l in line:
            wordlist = l.split(' ')
            if wordlist[0] == morph and wordlist[1] != name:
                morph_num += 1
            elif wordlist[0] == morph and wordlist[1] == name:
                name_num += 1
                morph_num += 1
        return name_num, morph_num

    def get_similar_names(self, _name):
        '''
        Generate possible name for a specific morph
        :param _name: (String) morph
        :return: ()
        '''
        name_entity = self.nickname_generation(_name)
        #print(name_entity)
        #print(len(name_entity))
        prior, likelihood = self.nb_learn(os.path.join(config.DICT_ROOT, "morph-entity.txt"))

        # TODO(pwwp):
        # Currently this method returns a string as possible name for a morph
        # Change it to Dict{<name>: <confidence_score>, <name>: <confidence_score>}

        result = self.nb_classify(name_entity, _name, prior, likelihood)
        result_num, morph_num = self.find_amount(result, morph, os.path.join(config.DICT_ROOT, "morph-entity.txt"))
        if 2*result_num <= len(name_entity) < 10*result_num:
            confidence_score = result_num/(morph_num + len(name_entity)/10.0)
        elif len(name_entity) < 2*result_num:
            confidence_score = result_num / (morph_num + len(name_entity)/3.0)
        else:
            confidence_score = result_num / (morph_num + len(name_entity) / 50.0)
        result_dict = {}
        result_dict[result] = result_dict.get(result, 0.0)
        result_dict[result] = confidence_score
        return result_dict


if __name__ == '__main__':
    morph = '赫赫'
    nick = NicknameGeneration()
    print(nick.get_similar_names(morph))
