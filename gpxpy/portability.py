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


try:
    # Python 2
    trial_dict = dict()
    trial_dict.has_key('foo')
    def has_key(d, key):
        return d.has_key(key)
except AttributeError:
    # Python 3
    def has_key(d, key):
        return key in d
finally:
    del trial_dict


try:
    # Python 2.x and Python 3.2+
    is_callable = callable
except NameError:
    # Python 3.0 and Python 3.1
    from collections import Callable

    def is_callable(x):
        return isinstance(x, Callable)
