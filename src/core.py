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
                'object': _class(*args,  **kwargs),
                'confidence': 1.0
            }

        #self.ner_module = ChineseNER()

        pass

    def recognize_tweet(self, tweet):
        '''
        Extract name entity morphs from a tweet.
        :param tweet: (String) content of the tweet(weibo)
        :return: (Two dimensional array) [[<String>, <float>], ...]
                Explanation: [[<morph>, <confidence>], [<morph>, <confidence>], ...]
                Every inner array has two components, a string and a float number.
                The string represents possible name morphs;
                The float number represents confidence calculate by our model.
        '''

        # Extract names from tweet:
        names_to_identify = self.ner_module.extract_name_entities_from_sentence(tweet)
        #names_to_identify = ["李月月鸟", "海涛", "泰勒十万伏特", "日日"]

        # Recognize with every method and generate a list of
        # possible names from each method

        results = {}
        for n in names_to_identify:
            results[n] = {}
            for module_name in self.recognition_modules:
                module = self.recognition_modules[module_name]['object']
                results[n][module_name] = module.get_similar_names(n)

        print(results)


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


