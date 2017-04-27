import os

from settings import config
from src.common import CN_CHAR_REGEX
from src.logger import Logger

from src.ner import ChineseNER
from src.nickname import NicknameGeneration
from src.phonetic_substitution import PhoneticSubstitution
from src.spelling_decomposition import SpellingDecomposition
from src.translation_and_transliteration import Translation


class EMRecognition:
    def __init__(self, runtime_config=None):
        '''
        Starting point for the whole project.
        '''

        '''Recognition_modules stores classes of every method for EMR recognition'''
        self.recognition_classes = [PhoneticSubstitution, NicknameGeneration, SpellingDecomposition]

        ''' recognition_objects stores instances of every module as
            {<module_name>: ['object': <module_object>, 'confidence': <float>], ...}'''
        self.recognition_modules = {}

        ''' logger prints and stores log files and is passed on to every instance'''
        logger = Logger()

        # Load a dictionary with all celebrities' names
        known_name_list = []
        with open(os.path.join(config.DICT_ROOT, "name_list.txt"), encoding='utf-8') as f:
            for line in f:
                known_name_list.append(line.strip())

        args = []

        kwargs = {
            'logger': logger,
            'name_list': known_name_list,
        }

        for _class in self.recognition_classes:
            class_name = _class.__name__
            self.recognition_modules[class_name] = {
                'instance': _class(*args,  **kwargs),
                'confidence': 1.0
            }

        #self.ner_module = ChineseNER()

        pass

    def recognize_tweet(self, tweet):
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
        extrated_morphs = self.ner_module.extract_name_entities_from_sentence(tweet)

        # Recognize with every method and generate a list of
        # possible names from each method
        results = {}
        for morph in extrated_morphs:
            results[morph] = {}
            for module_name in self.recognition_modules:
                module = self.recognition_modules[module_name]['instance']
                results[morph][module_name] = module.get_similar_names(morph)




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


