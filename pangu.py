#!/usr/bin/env python
# coding: utf-8
"""
Paranoid text spacing for good readability, to automatically insert whitespace
between CJK (Chinese, Japanese, Korean) and half-width characters (alphabetical
letters, numerical digits and symbols).

>>> import pangu
>>> nwe_text = pangu.spacing_text('當你凝視著bug，bug也凝視著你')
>>> print(nwe_text)
'當你凝視著 bug，bug 也凝視著你'
>>> nwe_content = pangu.spacing_file('path/to/file.txt')
>>> print(nwe_content)
'與 PM 戰鬥的人，應當小心自己不要成為 PM'
"""

from __future__ import print_function

import argparse
import os
import re
import sys

__version__ = '4.0.6'
__all__ = ['spacing_text', 'spacing_file', 'spacing', 'cli']

IS_PY2 = (sys.version_info[0] == 2)

if IS_PY2:
    def u(s):
        # return unicode(s.replace(r'\\', r'\\\\'), 'unicode_escape')  # noqa: F821
        return unicode(s, 'unicode_escape')  # noqa: F821
else:
    def u(s):
        return s

CJK = r'\u2e80-\u2eff\u2f00-\u2fdf\u3040-\u309f\u30a0-\u30fa\u30fc-\u30ff\u3100-\u312f\u3200-\u32ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff'

ANY_CJK = re.compile(u(r'[{CJK}]'.format(CJK=CJK)))

CONVERT_TO_FULLWIDTH_CJK_SYMBOLS_CJK = re.compile(u('([{CJK}])[ ]*([\\:]+|\\.)[ ]*([{CJK}])'.format(CJK=CJK)))
CONVERT_TO_FULLWIDTH_CJK_SYMBOLS = re.compile(u('([{CJK}])[ ]*([~\\!;,\\?]+)[ ]*'.format(CJK=CJK)))
DOTS_CJK = re.compile(u('([\\.]{{2,}}|\u2026)([{CJK}])'.format(CJK=CJK)))  # need to escape {}
FIX_CJK_COLON_ANS = re.compile(u('([{CJK}])\\:([A-Z0-9\\(\\)])'.format(CJK=CJK)))

CJK_QUOTE = re.compile(u('([{CJK}])([`"\u05f4])'.format(CJK=CJK)))  # no need to escape `
QUOTE_CJK = re.compile(u('([`"\u05f4])([{CJK}])'.format(CJK=CJK)))  # no need to escape `
FIX_QUOTE_ANY_QUOTE = re.compile(u(r'([`"\u05f4]+)(\s*)(.+?)(\s*)([`"\u05f4]+)'))

CJK_SINGLE_QUOTE_BUT_POSSESSIVE = re.compile(u("([{CJK}])('[^s])".format(CJK=CJK)))
SINGLE_QUOTE_CJK = re.compile(u("(')([{CJK}])".format(CJK=CJK)))
FIX_POSSESSIVE_SINGLE_QUOTE = re.compile(u("([{CJK}A-Za-z0-9])( )('s)".format(CJK=CJK)))

HASH_ANS_CJK_HASH = re.compile(u('([{CJK}])(#)([{CJK}]+)(#)([{CJK}])'.format(CJK=CJK)))
CJK_HASH = re.compile(u('([{CJK}])(#([^ ]))'.format(CJK=CJK)))
HASH_CJK = re.compile(u('(([^ ])#)([{CJK}])'.format(CJK=CJK)))

CJK_OPERATOR_ANS = re.compile(u('([{CJK}])([\\+\\-\\*\\/=&\\|<>])([A-Za-z0-9])'.format(CJK=CJK)))
ANS_OPERATOR_CJK = re.compile(u('([A-Za-z0-9])([\\+\\-\\*\\/=&\\|<>])([{CJK}])'.format(CJK=CJK)))

FIX_SLASH_AS = re.compile(u(r'([/]) ([a-z\-_\./]+)'))
FIX_SLASH_AS_SLASH = re.compile(u(r'([/\.])([A-Za-z\-_\./]+) ([/])'))

CJK_LEFT_BRACKET = re.compile(u('([{CJK}])([\\(\\[\\{{<>\u201c])'.format(CJK=CJK)))  # need to escape {
RIGHT_BRACKET_CJK = re.compile(u('([\\)\\]\\}}<>\u201d])([{CJK}])'.format(CJK=CJK)))  # need to escape }
FIX_LEFT_BRACKET_ANY_RIGHT_BRACKET = re.compile(u(r'([\(\[\{<\u201c]+)(\s*)(.+?)(\s*)([\)\]\}>\u201d]+)'))  # need to escape {}
ANS_CJK_LEFT_BRACKET_ANY_RIGHT_BRACKET = re.compile(u('([A-Za-z0-9{CJK}])[ ]*([\u201c])([A-Za-z0-9{CJK}\\-_ ]+)([\u201d])').format(CJK=CJK))
LEFT_BRACKET_ANY_RIGHT_BRACKET_ANS_CJK = re.compile(u('([\u201c])([A-Za-z0-9{CJK}\\-_ ]+)([\u201d])[ ]*([A-Za-z0-9{CJK}])').format(CJK=CJK))

AN_LEFT_BRACKET = re.compile(u(r'([A-Za-z0-9])([\(\[\{])'))
RIGHT_BRACKET_AN = re.compile(u(r'([\)\]\}])([A-Za-z0-9])'))

CJK_ANS = re.compile(u('([{CJK}])([A-Za-z\u0370-\u03ff0-9@\\$%\\^&\\*\\-\\+\\\\=\\|/\u00a1-\u00ff\u2150-\u218f\u2700—\u27bf])'.format(CJK=CJK)))
# print(CJK_ANS)
# print(CJK_ANS.sub(r'\1 \2', '中文$'))
# print(CJK_ANS.sub(r'\1 \2', '中文%'))
# print(CJK_ANS.sub(r'\1 \2', '中文^'))
# print(CJK_ANS.sub(r'\1 \2', '中文*'))
# print(CJK_ANS.sub(r'\1 \2', '中文-'))
# print(CJK_ANS.sub(r'\1 \2', '中文+'))
# print(CJK_ANS.sub(r'\1 \2', '中文\\'))
# print(CJK_ANS.sub(r'\1 \2', '中文='))
# print(CJK_ANS.sub(r'\1 \2', '中文|'))
# print(CJK_ANS.sub(r'\1 \2', '中文/'))

ANS_CJK = re.compile(u('([A-Za-z\u0370-\u03ff0-9~\\!\\$%\\^&\\*\\-\\+\\\\=\\|;:,\\./\\?\u00a1-\u00ff\u2150-\u218f\u2700—\u27bf])([{CJK}])'.format(CJK=CJK)))

S_A = re.compile(r'(%)([A-Za-z])')

MIDDLE_DOT = re.compile(u(r'([ ]*)([\u00b7\u2022\u2027])([ ]*)'))

# Python version only
TILDES = re.compile(r'~+')
EXCLAMATION_MARKS = re.compile(r'!+')
SEMICOLONS = re.compile(r';+')
COLONS = re.compile(r':+')
COMMAS = re.compile(r',+')
PERIODS = re.compile(r'\.+')
QUESTION_MARKS = re.compile(r'\?+')


def convert_to_fullwidth(symbols):
    symbols = TILDES.sub(u('～'), symbols)
    symbols = EXCLAMATION_MARKS.sub(u('！'), symbols)
    symbols = SEMICOLONS.sub(u('；'), symbols)
    symbols = COLONS.sub(u('：'), symbols)
    symbols = COMMAS.sub(u('，'), symbols)
    symbols = PERIODS.sub(u('。'), symbols)
    symbols = QUESTION_MARKS.sub(u('？'), symbols)
    return symbols.strip()


def spacing(text):
    """
    Perform paranoid text spacing on text.
    """
    # always use unicode
    if IS_PY2 and isinstance(text, str):
        text = text.decode('utf-8')

    if len(text) <= 1 or not ANY_CJK.search(text):
        return text

    new_text = text

    matched = CONVERT_TO_FULLWIDTH_CJK_SYMBOLS_CJK.search(new_text)
    while matched:
        start, end = matched.span()
        print(matched.groups())
        print(matched.span())
        print(1, new_text[:start + 1].strip())
        print(2, convert_to_fullwidth(new_text[start + 1:end]))
        print(3, new_text[end:].strip())
        new_text = u('').join((new_text[:start + 1].strip(), convert_to_fullwidth(new_text[start + 1:end]), new_text[end:].strip()))
        print(4, new_text)
        matched = CONVERT_TO_FULLWIDTH_CJK_SYMBOLS_CJK.search(new_text)

    matched = CONVERT_TO_FULLWIDTH_CJK_SYMBOLS.search(new_text)
    while matched:
        start, end = matched.span()
        new_text = u('').join((new_text[:start + 1].strip(), convert_to_fullwidth(new_text[start + 1:end]), new_text[end:].strip()))
        matched = CONVERT_TO_FULLWIDTH_CJK_SYMBOLS.search(new_text)

    new_text = DOTS_CJK.sub(r'\1 \2', new_text)
    new_text = FIX_CJK_COLON_ANS.sub(r'\1：\2', new_text)

    new_text = CJK_QUOTE.sub(r'\1 \2', new_text)
    new_text = QUOTE_CJK.sub(r'\1 \2', new_text)
    new_text = FIX_QUOTE_ANY_QUOTE.sub(r'\1\3\5', new_text)

    new_text = CJK_SINGLE_QUOTE_BUT_POSSESSIVE.sub(r'\1 \2', new_text)
    new_text = SINGLE_QUOTE_CJK.sub(r'\1 \2', new_text)
    new_text = FIX_POSSESSIVE_SINGLE_QUOTE.sub(r"\1's", new_text)

    new_text = HASH_ANS_CJK_HASH.sub(r'\1 \2\3\4 \5', new_text)
    new_text = CJK_HASH.sub(r'\1 \2', new_text)
    new_text = HASH_CJK.sub(r'\1 \3', new_text)

    new_text = CJK_OPERATOR_ANS.sub(r'\1 \2 \3', new_text)
    new_text = ANS_OPERATOR_CJK.sub(r'\1 \2 \3', new_text)

    new_text = FIX_SLASH_AS.sub(r'\1\2', new_text)
    new_text = FIX_SLASH_AS_SLASH.sub(r'\1\2\3', new_text)

    new_text = CJK_LEFT_BRACKET.sub(r'\1 \2', new_text)
    new_text = RIGHT_BRACKET_CJK.sub(r'\1 \2', new_text)
    new_text = FIX_LEFT_BRACKET_ANY_RIGHT_BRACKET.sub(r'\1\3\5', new_text)
    new_text = ANS_CJK_LEFT_BRACKET_ANY_RIGHT_BRACKET.sub(r'\1 \2\3\4', new_text)
    new_text = LEFT_BRACKET_ANY_RIGHT_BRACKET_ANS_CJK.sub(r'\1\2\3 \4', new_text)

    new_text = AN_LEFT_BRACKET.sub(r'\1 \2', new_text)
    new_text = RIGHT_BRACKET_AN.sub(r'\1 \2', new_text)

    new_text = CJK_ANS.sub(r'\1 \2', new_text)
    new_text = ANS_CJK.sub(r'\1 \2', new_text)

    new_text = S_A.sub(r'\1 \2', new_text)

    new_text = MIDDLE_DOT.sub(u('・'), new_text)

    return new_text.strip()


def spacing_text(text):
    """
    Perform paranoid text spacing on text. An alias of `spacing()`.
    """
    return spacing(text)


def spacing_file(path):
    """
    Perform paranoid text spacing from file.
    """
    with open(os.path.abspath(path)) as f:
        return spacing_text(f.read())


def cli(args=None):
    if not args:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog='pangu',
        description='pangu.py -- Paranoid text spacing for good readability, to automatically insert whitespace between CJK and half-width characters (alphabetical letters, numerical digits and symbols).',
    )
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument('-t', '--text', action='store_true', dest='is_text', required=False, help='specify the input value is a text')
    parser.add_argument('-f', '--file', action='store_true', dest='is_file', required=False, help='specify the input value is a file path')
    parser.add_argument('text_or_path', action='store', type=str, help='the text or file path to apply spacing')

    if not sys.stdin.isatty():
        print(spacing_text(sys.stdin.read()))  # noqa: T003
    else:
        args = parser.parse_args(args)
        if args.is_text:
            print(spacing_text(args.text_or_path))  # noqa: T003
        elif args.is_file:
            print(spacing_file(args.text_or_path))  # noqa: T003
        else:
            print(spacing_text(args.text_or_path))  # noqa: T003


if __name__ == '__main__':
    cli()
