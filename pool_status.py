from pprint import pprint
from datetime import datetime, timedelta
from pathlib import Path
from jsondt import dumps, loads

import pool_data as pd

DATE_FORMAT = r'%Y-%m-%d %H:%M:%S'
DATA_PATH = Path.home() / "Documents"
DATA_NAME = r'data_{:%Y%m%d%H%M%S}.json'
LATESTDATA_PATH = DATA_PATH / "latestdata.json"


class PoolStatus:
    """Contains status information of the pool.

    This class implements methods to save objects to json files and load them
    again. As some attributes are datetime objects, which are loaded as strings
    from json, it needs to know which attributes have to be converted.
    """

    def __init__(self, timestamp=datetime.now()):
        self.timestamp = timestamp
        self.temperature = {}
        self.min_temperature = {}
        self.max_temperature = {}
        self.light = 0
        self.pump = {'status': None,
                     'runtime': timedelta(hours=0)}

    def __str__(self):
        return 'PoolStatus as of {0}'.format(self.timestamp.strftime(DATE_FORMAT))

    def __repr__(self):
        return 'PoolStatus({0}): {1}'.format(repr(self.timestamp),
                                             repr(self.__dict__))

    def update(self):
        "Update status information."
        self.temperature['water'] = pd.temperature(pd.POOL_TEMP_SENSOR)
        self.temperature['surface'] = pd.temperature(pd.SURFACE_TEMP_SENSOR)
        self.temperature['air'] = pd.temperature(pd.AIR_TEMP_SENSOR)
        self.temperature['cpu'] = pd.cpu_temperature(),
        self.temperature['gpu'] = pd.gpu_temperature(),
        self.light = pd.light_intensity()
        self.pump['status'] = pd.pump_status()
        self.pump['pressure'] = pd.pressure(pd.FILTER_PRESSURE_CHANNEL)
        self.pump['power'] = pd.powerconsumption(pd.POWER_CONSUMPTION_CHANNEL)
        self.timestamp = datetime.now()
        return self

    def save(self, latest=True):
        """Save object to a json file and return its path.

        The filename contains the timestamp of the data object.
        If latest is True (default) a symbolic link is created
        with the name "latestdata".
        """
        datafile = DATA_PATH / DATA_NAME.format(self.timestamp)
        datafile.write_text(dumps(self.__dict__))
        if latest:
            if LATESTDATA_PATH.is_symlink():
                LATESTDATA_PATH.unlink()
            LATESTDATA_PATH.symlink_to(datafile)
        return str(datafile)

    @classmethod
    def load(cls):
        "Return the latest data object loaded from the json file."
        try:
            data = loads(LATESTDATA_PATH.read_text())
        except FileNotFoundError:
            return cls().update()
        else:
            obj = cls()
            obj.temperature = data['temperature']
            obj.light = data['light']
            obj.pump = data['pump']
            obj.timestamp = data['timestamp']
            return obj


if __name__ == "__main__":
    print(PoolStatus().update().save())
