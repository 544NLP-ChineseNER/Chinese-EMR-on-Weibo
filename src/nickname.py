#import jieba


class NicknameGeneration:
    stopwords = ["阿", "哥", "姐", "弟", "爷", "叔", "姑", "婆", "大", "小", "老", "太"]

    def __init__(self, nickname):
        self.nickname = nickname

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
        if (self.calculate_similarity_score(str_a, str_b) > max):
            max = self.calculate_similarity_score(str_a, str_b)
        seg_list = jieba.cut(str_b)
        for i in seg_list:
            if (self.calculate_similarity_score(str_a, i) > max):
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
        max = 0.0
        for name in name_entity:
            outerkey = name
            innerkey = morph
            prior[outerkey] = prior.get(outerkey, 0.0)
            likelihood[outerkey] = likelihood.get(outerkey, {})
            likelihood[outerkey][innerkey] = likelihood[outerkey].get(innerkey, 0.0)
            p_likelihood = likelihood[outerkey][innerkey]
            p = prior[name] * p_likelihood
            if p > max:
                result = name
                max = p
        return result

    def nickname_generation(self):
        with open("../media/dicts/celebrity.txt", "r", encoding='UTF-8')as infile:
            data = infile.read()
        line = data.splitlines()
        name_entity = []
        for l in line:
            for index in self.nickname:
                if index in l and index not in self.stopwords and l not in name_entity:
                    name_entity.append(l)
        return name_entity

if __name__ == '__main__':
    morph = '涛涛'
    nick = NicknameGeneration(morph)
    name_entity = nick.nickname_generation()
    prior, likelihood = nick.nb_learn("../media/dicts/morph-entity.txt")
    result = nick.nb_classify(name_entity, morph, prior, likelihood)
    print(result)

