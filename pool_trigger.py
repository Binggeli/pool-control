from pprint import pprint
from datetime import date, datetime, timedelta
from pathlib import Path
from jsondt import dumps, loads, JSONDecodeError
from argparse import ArgumentParser

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

    def __init__(self, status=True, priority=None, starttime=None,
                 seconds=0, minutes=0, hours=0, days=0, weeks=0):
        self.status = status
        self.priority = priority
        self.starttime = starttime if starttime is not None else datetime.now()
        self.timestamp = datetime.now()
        self.timedelta = timedelta(seconds=seconds, minutes=minutes, hours=hours,
                                   days=days, weeks=weeks)

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

    def save(self):
        """Save object to a json file and return its path."""
        datafile = DATA_PATH / DATA_NAME.format(self.priority)
        datafile.write_text(dumps(self.__dict__))
        return str(datafile)

    @classmethod
    def load(cls, timestamp=datetime.now(), priority=None):
        """Return the trigger object for the given priority.

        If no priority is given the object with highest priority is returned,
        which is still active (stoptime in the future).
        """
        obj = None
        if priority is None:
            filepattern = DATA_NAME.format('*')
        else:
            filepattern = DATA_NAME.format(priority)
        for filepath in DATA_PATH.glob(filepattern):
            try:
                data = loads(filepath.read_text())
            except JSONDecodeError:
                continue
            if obj is None or data['priority'] > obj.priority:
                newobj = cls(data['status'], data['priority'])
                newobj.timestamp = data['timestamp']
                newobj.starttime = data['starttime']
                newobj.timedelta = data['timedelta']
                if newobj.stoptime > timestamp:
                    obj = newobj
        return obj


def argparser():
    """Create an argument parser for the command line."""
    parser = ArgumentParser(description='Change pump state based on arguments and sensors.')
    parser.add_argument('state', choices=['on', 'off'],
                        help='Trigger the switch to this state.')
    parser.add_argument('hours', type=int,
                        help='Trigger the switch for this number of hours.')
    parser.add_argument('-p', '--priority', type=int, default=1,
                        help='Priority of this trigger.')
    return parser

if __name__ == "__main__":
    args = argparser().parse_args()
    PoolTrigger(args.state == 'on', args.priority, hours=args.hours).save()
    pprint(PoolTrigger.load())
