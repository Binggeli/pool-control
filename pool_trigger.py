from pprint import pprint
from datetime import date, datetime, timedelta
from pathlib import Path

import os
import json

DATE_FORMAT = r'%Y-%m-%d %H:%M:%S'
DATA_PATH = Path.home() / "Documents"
DATA_NAME = r'trigger_{0}.json'


class PoolTrigger:
    """Contains triggering information for the pool.

    Objects of this class contain triggering information for the pool, which
    are normally set manually to override the automated pool control.

    This class implements methods to save objects to json files and load them
    again. As some attributes are datetime objects, which are loaded as strings
    from json, it needs to know which attributes have to be converted.
    """

    def __init__(self, status=True, priority=None, starttime=datetime.now(),
                 seconds=0, minutes=0, hours=0, days=0, weeks=0):
        self.status = status
        self.priority = priority
        self.timestamp = datetime.now()
        self.timedelta = timedelta(seconds=seconds, minutes=minutes, hours=hours,
                                   days=days, weeks=weeks)
        self.starttime = starttime

    @property
    def stoptime(self):
        "Return the stoptime of the trigger."
        return self.starttime + self.timedelta

    def __str__(self):
        return 'PoolTrigger with priority {0}'.format(self.priority)

    def __repr__(self):
        return 'PoolTrigger({0}, {1}): {1}'.format(repr(self.status),
                                                   repr(self.priority),
                                                   repr(self.__dict__))

    def json(self):
        "Return object as json-encoded string."
        data = self.__dict__.copy()
        for k in data:
            if isinstance(data[k], datetime):
                data[k] = data[k].strftime(DATE_FORMAT)
            if isinstance(data[k], timedelta):
                data[k] = data[k].total_seconds()
        return json.dumps(data)

    def save(self):
        """Save object to a json file and return its path."""
        datafile = DATA_PATH / DATA_NAME.format(self.priority)
        datafile.write_text(self.json())
        return str(datafile)

    @classmethod
    def load(cls, priority=None):
        """Return the trigger object for the given priority.

        If no priority is given the object with highest priority is returned,
        which is still active (stoptime in the future).
        """
        obj = None
        if priority is None:
            filepattern = DATA_NAME.format('*')
        else:
            filepattern = DATA_NAME.format(priority)
        for filepath in DATAPATH.glob(filepattern):
            try:
                data = json.load(filepath.read_text())
            except json.JSONDecodeError:
                continue
            if obj is None or data['priority'] > obj.priority:
                newobj = cls(data['status'], data['priority'], seconds=data['timedelta'])
                newobj.timestamp = datetime.strptime(data['timestamp'],
                                                     DATE_FORMAT)
                newobj.starttime = datetime.strptime(data['starttime'],
                                                     DATE_FORMAT)
                if newobj.stoptime > datetime.now():
                    obj = newobj
        return obj


if __name__ == "__main__":
    pprint(PoolTrigger.load())
