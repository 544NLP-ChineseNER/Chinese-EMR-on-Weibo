import os

import settings.config as config

from warnings import warn


class Logger:
    def __init__(self, file_path=None):
        '''
        :param file_path: (String) path to log file.
        '''
        if file_path is None:
            self.log_file = open(os.path.join(config.PROJECT_ROOT, 'emr.log'), 'a+', encoding='utf-8')
        else:
            try:
                self.log_file = open(file_path, 'a+', encoding='utf-8')
            except FileExistsError as e:
                print("Log file does not exist. Further logs would only be printed on screen",
                      " and would not be saved.")

    def info(self, info_msg):
        '''
        :param info_str: (String)
        :return: None
        '''
        if config.LOG_LEVEL >= 2:
            print("[INFO] " + info_msg)

    def warning(self, warning_msg):
        '''
        :param warning_str: (String)
        :return: None
        '''
        if config.LOG_LEVEL >= 1:
            warn("[WARNING] " + warning_msg)

    def error(self, error_msg):
        '''
        :param error_msg: (String)
        :return: None
        '''
        warn("[ERROR] " + error_msg)


class EmptyLogger(Logger):
    '''
    EmptyLogger is a shell for class Logger, only designed for debugging.
    EmptyLogger prints out all debugging output to console.
    '''

    def __init__(self, file_path=None):
        pass

    def info(self, info_msg):
        print("[INFO] " + info_msg)

    def warning(self, warning_msg):
        print("[WARNING] " + warning_msg)

    def error(self, error_msg):
        warn("[ERROR] " + error_msg)