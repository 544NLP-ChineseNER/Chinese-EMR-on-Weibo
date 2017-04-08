import os

import settings.config as config

from warnings import warn


class Logger:
    def __init__(self, file_path=None):
        if file_path is None:
            self.log_file = open(os.path.join(config.PROJECT_ROOT, 'emr.log'), 'a+', encoding='utf-8')
        else:
            try:
                self.log_file = open(file_path, 'a+', encoding='utf-8')
            except FileExistsError as e:
                print("Log file does not exist. Further logs would only be printed on screen",
                      " and would not be saved.")

    def info(self, info_str):
        if config.LOG_LEVEL >= 2:
            print("[INFO] " + info_str)

    def warning(self, warning_str):
        if config.LOG_LEVEL >= 1:
            warn("[WARN] " + warning_str)

    def error(self, error_msg):
        warn("[ERROR] " + error_msg)