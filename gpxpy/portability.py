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

try:
    # Python 2
    #noinspection PyCompatibility
    unicode()

    def has_unicode_type():
        return True

except NameError:
    # Python 3
    def has_unicode_type():
        return False
