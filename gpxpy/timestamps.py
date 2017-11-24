# -*- coding: utf-8 -*-

import datetime as mod_datetime
import re as mod_re

def parse_time(string):
    from . import gpx as mod_gpx
    if not string:
        return None
    if 'T' in string:
        string = string.replace('T', ' ')
    if 'Z' in string:
        string = string.replace('Z', '')
    if '.' in string:
        string = string.split('.')[0]
    if len(string) > 19:
        # remove the timezone part
        d = max(string.rfind('+'), string.rfind('-'))
        string = string[0:d]
    if len(string) < 19:
        # string has some single digits
        p = '^([0-9]{4})-([0-9]{1,2})-([0-9]{1,2}) ([0-9]{1,2}):([0-9]{1,2}):([0-9]{1,2}).*$'
        s = mod_re.findall(p, string)
        if len(s) > 0:
            string = '{0}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}'\
                .format(*[int(x) for x in s[0]])
    for date_format in mod_gpx.DATE_FORMATS:
        try:
            return mod_datetime.datetime.strptime(string, date_format)
        except ValueError:
            pass
    raise mod_gpx.GPXException('Invalid time: %s' % string)


