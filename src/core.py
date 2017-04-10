import os

from settings import config
from src.phonetic_substitution import PhoneticSubstitution
from src.nickname import NicknameGeneration
from src.common import CN_CHAR_REGEX
from src.logger import Logger

class EMRecognition:
    def __init__(self, config=None):
        '''
        Starting point for the whole project.
        '''

        '''Recognition_modules stores classes of every method for EMR recognition'''
        recognition_modules = [PhoneticSubstitution, NicknameGeneration]

        ''' recognition_objects stores instances of every module as
            {<module_name>: <module_object>}'''
        recognition_objects = {}

        ''' logger prints and stores log files and is passed on to every instance'''
        logger = Logger()

        args = []

        kwargs = {
            'logger': logger
        }

        for module in recognition_modules:
            module_name = module.__name__
            recognition_objects[module_name] = module(*args,  **kwargs)

        pass


if __name__ == '__main__':
     emr = EMRecognition()

