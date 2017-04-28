import os
import re
import heapq

from settings import config
from src.common import CN_CHAR_REGEX
from src.logger import Logger

from src.ner import ChineseNER
from src.characteristic import Characteristic
from src.nickname import NicknameGeneration
from src.phonetic_substitution import PhoneticSubstitution
from src.spelling_decomposition import SpellingDecomposition
from src.translation_and_transliteration import Translation
from src.tweet_name_extraction import TweetNameExtractor


class EMRecognition:
    def __init__(self, *args, **kwargs):
        '''
        Starting point for the whole project.
        '''

        '''Recognition_modules stores classes of every method for EMR recognition'''
        self.recognition_classes = [PhoneticSubstitution, NicknameGeneration, SpellingDecomposition, Translation,
                                    Characteristic]

        ''' recognition_objects stores instances of every module as
            {<module_name>: ['object': <module_object>, 'confidence': <float>], ...}'''
        self.recognition_modules = {}

        ''' logger prints and stores log files and is passed on to every instance'''
        self.logger = Logger()

        '''ner_mode: 0 - Rule Based NER, 1 - Stanford NER, 2 - Given NER List'''
        self.ner_mode = kwargs.get("ner_mode", 0)

        '''enabled_module: binary '''
        self.enabled_module = kwargs.get('enabled_module', 31)

        # Load a dictionary with all celebrities' names
        known_name_list = []
        with open(os.path.join(config.DICT_ROOT, "name_list.txt"), encoding='utf-8') as f:
            for line in f:
                known_name_list.append(line.strip())

        args = []

        kwargs = {
            'logger': self.logger,
            'name_list': known_name_list,
        }

        for i in range(len(self.recognition_classes)):
            if self.enabled_module & (1 << i) == 0:
                continue
            _class = self.recognition_classes[i]
            class_name = _class.__name__
            self.logger.info("[Core] Initializing module " + class_name)
            self.recognition_modules[class_name] = {
                'instance': _class(*args, **kwargs),
                'confidence': 1.0
            }

        self.ner_module = ChineseNER()

        pass

    def recognize_tweet(self, tweet, morphs=None):
        '''
        Extract name entity morphs from a tweet.
        :param tweet: (String) content of the tweet(weibo)
        :return: (Dict) {
                            <String> : [(String, float) {5}],
                            <String> : [(String, float) {5}],
                            ...
                        }
                Explanation:
                        {
                            <morph> : [0-5 * (<name>, <confidence_score>)],
                            <morph> : [0-5 * (<name>, <confidence_score>)],
                        }
                A tweet may have multiple morphs, thus we use a dictionary to store
                possible names for every morph.
        '''

        # Extract morphs from tweet:
        extracted_morphs = None

        if self.ner_mode == 0:
            extracted_morphs = self.ner_module.extract_morph(tweet)
            extracted_morphs = [m for m in extracted_morphs if re.match(r"^[0-9 ,.:]+$", m) is None]
        elif self.ner_mode == 1:
            extracted_morphs = self.ner_module.extract_name_entities_from_sentence(tweet)
        elif self.ner_mode == 2:
            extracted_morphs = morphs

        self.logger.info("Morphs: " + " ".join(extracted_morphs))
        # Recognize with every method and generate a list of
        # possible names from each method
        candidate_lists = {}
        results = {}
        for morph in extracted_morphs:
            self.logger.info("Dealing with morph: %s " % morph)
            results[morph] = {}
            for module_name in self.recognition_modules:
                module = self.recognition_modules[module_name]['instance']
                try:
                    results[morph][module_name] = module.get_similar_names(morph)
                except Exception as e:
                    self.logger.warning("[Core] %s raised an exception. %s." % (module_name, str(e)))
                    results[morph][module_name] = {}

            morph_result = self.combine_results(morph, results[morph])
            candidate_lists[morph] = list(morph_result.keys())
        return candidate_lists

    def combine_results(self, morph, morph_result):
        '''
        Get final score of possible entity names combining all methods
        :param morph: (string) morph computing
        :param morph_result: (dict) entity-confidence score pairs of each module (result[morph] in recognize_tweet)
        :return: (Dict) {
                            <String> : [(float) {5}],
                            <String> : [(float) {5}],
                            ...
                        }
                Explanation:
                        {
                            <name> : [0-5 * <confidence_score>],
                            <morph> : [0-5 * <confidence_score>],
                        }
        '''
        result = []
        prob, prior = self.train_nbmodel()
        for module in morph_result:
            probability = prior[module]
            if morph in prob:
                probability *= prob[morph][module]
            for candidate in morph_result[module]:
                new_score = probability * morph_result[module][candidate]
                heapq.heappush(result, (new_score, candidate))

            result = sorted(result, key=lambda x: x[0], reverse=True)

        self.logger.info("[Core] Final Result : " + str(result))

        return {name: score for (score, name) in result[:5]}

    def train_nbmodel(self):
        pri = {}
        total_size = 0
        pro = {}

        using_classes = self.recognition_modules.keys()
        with open(os.path.join(config.DICT_ROOT, "method_classification.txt"), encoding='utf-8') as f:
            for line in f:
                data = line.strip().split(" ")
                classes = data[1].split(",")
                for c in classes:
                    if c not in using_classes:
                        continue
                    total_size += 1
                    pri[c] = pri.get(c, 0) + 1
                    if data[0] not in pro:
                        pro[data[0]] = {}
                    pro[data[0]][c] = pro[data[0]].get(c, 0) + 1
            for i in pro:
                for class_name in using_classes:
                    pro[i][class_name] = (pro[i].get(class_name, 0) + 1) / (pri[class_name] + len(pro))

            for p in pri:
                pri[p] = pri.get(p) / total_size
        return pro, pri


if __name__ == '__main__':
    emr = EMRecognition()
    emr.recognize_tweet("这是就是一个测试而已")

    # names = set()
    # with open(os.path.join(config.DICT_ROOT, "celebrity.txt"), encoding="utf-8") as f:
    #     for line in f:
    #         names.add(line)
    #
    # new_file = open(os.path.join(config.DICT_ROOT, "celebrity_dedup.txt"), 'w', encoding="utf-8")
    # for n in names:
    #     new_file.write(n)
    #
    # new_file.close()
