from datetime import date, datetime, timedelta

import json
import re

DATETIME_FORMAT = r'%Y-%m-%dT%H:%M:%S'
DATETIME_RE = re.compile(r'([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})([.]([0-9]{6}))?')

TIMEDELTA_RE = re.compile(r'(([0-9]+) days?, )?([0-9]{1,2}):([0-9]{2}):([0-9]{2})([.]([0-9]{6}))?')

class JSONDateTimeDecoder(json.JSONDecoder):
    def int(self, match, index):
        if match.group(index) is None:
            return 0
        else:
            return int(match.group(index))

    def datetime_parser(self, obj):
        if isinstance(obj, str):
            m = DATETIME_RE.match(obj)
            if m is not None:
                obj = datetime(year=self.int(m, 1), month=self.int(m, 2), day=self.int(m, 3),
                               hour=self.int(m, 4), minute=self.int(m, 5), second=self.int(m, 6),
                               microsecond=self.int(m, 8))
            m = TIMEDELTA_RE.match(obj)
            if m is not None:
                obj = timedelta(days=self.int(m, 2), hours=self.int(m, 3),
                                minutes=self.int(m, 4), seconds=self.int(m, 5),
                                microseconds=self.int(m, 7))
        else:
            try:
                for el in iter(obj):
                    el = self.datetime_parser(el)
            except TypeError:
                pass
        return obj

    def decode(self, s):
        obj = super().decode(s)
        return self.datetime_parser(obj)

class JSONDateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime(DATETIME_FORMAT)
        elif isinstance(obj, timedelta):
            return str(obj)
        else:
            return super().default(obj)

def dump(obj, fp, **kwargs):
    return json.dump(obj, fp, cls=JSONDateTimeEncode, kwargs)

def dumps(obj, **kwargs):
    return json.dumps(obj, cls=JSONDateTimeEncode, kwargs)

def load(fp, **kwargs):
    return json.load(fp, cls=JSONDateTimeDecode, kwargs)

def loads(s, **kwargs):
    return json.loads(s, cls=JSONDateTimeDecode, kwargs)
