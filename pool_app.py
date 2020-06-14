from datetime import datetime
from flask import Flask
import json

from pool_status import PoolStatus, LATESTDATA_PATH
from pool_trigger import PoolTrigger
from pump import run_pump

app = Flask(__name__)

@app.route('/')
def pool_status():
    out = ''
    out += 'Wassertemperatur:<br><div>{0} Grad</div><br>\n'.format(pd.temperature(pd.POOL_TEMP_SENSOR))
    out += 'Umgebungstemperatur:<br><div>{0} Grad</div><br>\n'.format(pd.temperature(pd.AIR_TEMP_SENSOR))
    out += 'Filterdruck:<br><div>{0:.2f} bar</div><br>\n'.format(pd.pressure(pd.FILTER_PRESSURE_CHANNEL))
    out += 'Die Pumpe l&auml;uft{0}.<br>\n'.format('' if pd.pump_status() else ' nicht')
    out += '<br>Daten vom {0:%d.%m.%Y %H:%M:%S}\n'.format(datetime.now())
    return out

@app.route('/status')
def pool_status_json():
    return LATESTDATA_PATH.read_text()

@app.route('/pump/on')
def pump_on():
    PoolTrigger(True, 100, minutes=5).save()
    run_pump(True)
    return pool_status_json()

@app.route('/pump/off')
def pump_off():
    PoolTrigger(False, 100, minutes=5).save()
    run_pump(False)
    return pool_status_json()
