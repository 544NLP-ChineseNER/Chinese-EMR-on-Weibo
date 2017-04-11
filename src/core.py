import os

from settings import config
from src.phonetic_substitution import PhoneticSubstitution
from src.spelling_decomposition import SpellingDecomposition
from src.nickname import NicknameGeneration
from src.translation_and_transliteration import Translation
from src.common import CN_CHAR_REGEX
from src.logger import Logger

class EMRecognition:
    def __init__(self, config=None):
        '''
        Starting point for the whole project.
        '''

        '''Recognition_modules stores classes of every method for EMR recognition'''
        self.recognition_modules = [PhoneticSubstitution, NicknameGeneration, SpellingDecomposition,Translation]

        ''' recognition_objects stores instances of every module as
            {<module_name>: ['object': <module_object>, 'confidence': <float>], ...}'''
        self.recognition_objects = {}

        ''' logger prints and stores log files and is passed on to every instance'''
        logger = Logger()

        args = []

        kwargs = {
            'logger': logger
        }

        for module in self.recognition_modules:
            module_name = module.__name__
            self.recognition_objects[module_name] = {
                'object': module(*args,  **kwargs),
                'confidence': 1.0
            }

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
        pass



if __name__ == '__main__':
    emr = EMRecognition()
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


