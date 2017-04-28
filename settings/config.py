# Configuration file for EMR Project
import os


DEBUG = True

# LOG_LEVEL:
# |-- 0 - Only record error messages;
# |-- 1 - Record errors and warnings
# |-- 2 - All available messages are recorded
LOG_LEVEL = 2

# Directory related configs
PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
DICT_ROOT = os.path.join(MEDIA_ROOT, 'dicts')
LOG_ROOT = os.path.join(PROJECT_ROOT, 'logs')

SPELLING_ROOT = os.path.join(DICT_ROOT, 'spelling_decomposition')
WORD2VEC_ROOT = os.path.join(DICT_ROOT, 'word2vec')
NER_ROOT = os.path.join(DICT_ROOT, 'ner')

