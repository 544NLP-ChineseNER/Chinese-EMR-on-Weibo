# -*- coding: utf-8 -*-
import re

from warnings import warn

# Regular Expression for finding all Chinese characters
# Reference: http://stackoverflow.com/questions/2718196/find-all-chinese-text-in-a-string-using-python-and-regex
# -------------------- Start ------------------------

LHan = [[0x2E80, 0x2E99],    # Han # So  [26] CJK RADICAL REPEAT, CJK RADICAL RAP
        [0x2E9B, 0x2EF3],    # Han # So  [89] CJK RADICAL CHOKE, CJK RADICAL C-SIMPLIFIED TURTLE
        [0x2F00, 0x2FD5],    # Han # So [214] KANGXI RADICAL ONE, KANGXI RADICAL FLUTE
        0x3005,              # Han # Lm       IDEOGRAPHIC ITERATION MARK
        0x3007,              # Han # Nl       IDEOGRAPHIC NUMBER ZERO
        [0x3021, 0x3029],    # Han # Nl   [9] HANGZHOU NUMERAL ONE, HANGZHOU NUMERAL NINE
        [0x3038, 0x303A],    # Han # Nl   [3] HANGZHOU NUMERAL TEN, HANGZHOU NUMERAL THIRTY
        0x303B,              # Han # Lm       VERTICAL IDEOGRAPHIC ITERATION MARK
        [0x3400, 0x4DB5],    # Han # Lo [6582] CJK UNIFIED IDEOGRAPH-3400, CJK UNIFIED IDEOGRAPH-4DB5
        [0x4E00, 0x9FC3],    # Han # Lo [20932] CJK UNIFIED IDEOGRAPH-4E00, CJK UNIFIED IDEOGRAPH-9FC3
        [0xF900, 0xFA2D],    # Han # Lo [302] CJK COMPATIBILITY IDEOGRAPH-F900, CJK COMPATIBILITY IDEOGRAPH-FA2D
        [0xFA30, 0xFA6A],    # Han # Lo  [59] CJK COMPATIBILITY IDEOGRAPH-FA30, CJK COMPATIBILITY IDEOGRAPH-FA6A
        [0xFA70, 0xFAD9],    # Han # Lo [106] CJK COMPATIBILITY IDEOGRAPH-FA70, CJK COMPATIBILITY IDEOGRAPH-FAD9
        [0x20000, 0x2A6D6],  # Han # Lo [42711] CJK UNIFIED IDEOGRAPH-20000, CJK UNIFIED IDEOGRAPH-2A6D6
        [0x2F800, 0x2FA1D]]  # Han # Lo [542] CJK COMPATIBILITY IDEOGRAPH-2F800, CJK COMPATIBILITY IDEOGRAPH-2FA1D

def build_re():
    L = []
    for i in LHan:
        if isinstance(i, list):
            f, t = i
            try:
                f = chr(f)
                t = chr(t)
                L.append('%s-%s' % (f, t))
            except:
                pass # A narrow python build, so can't use chars > 65535 without surrogate pairs!

        else:
            try:
                L.append(chr(i))
            except:
                pass

    RE = '[%s]' % ''.join(L)
    return re.compile(RE)

CN_CHAR_REGEX = build_re()

# -------------------- End ------------------------

URL_REGEX = re.compile(r"(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-z]{2,6}\b[-a-zA-Z0-9@:%_\+.~#?&//=]*)")
# Courtset of Daveo
# Reference: http://stackoverflow.com/questions/3809401/what-is-a-good-regular-expression-to-match-a-url

def extract_tiny_url_from_string(s):
    '''
    Extract tiny url from a string.
    :param s: (String) a string with or without url
    :return: List[String] A list of urls
            Example: ["http://www.google.com", "http://t.cn/JustKidding"]
            If not url was found, returns an empty list.
    '''
    match_result = URL_REGEX.findall(s)
    return [p[0] for p in match_result]



def test_visible(element):
    '''
    Judge if an element is visible to end-user
    :param element: (BeautifulSoup object) souped page
    :return: True if element is visible, False otherwise
    '''
    # Filter out scripts, stylesheets and other tags not showing on page
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    # Filter out commented elements
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True