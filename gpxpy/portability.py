"""Utilities for assisting with portability between Python 2 and Python 3.
"""

try:
    # Python 2
    #noinspection PyCompatibility
    base = basestring
    def is_string(s):
        return isinstance(s, base)
except NameError:
    # Python 3
    def is_string(s):
        return isinstance(s, str)
