from datetime import datetime
from flask import Flask
import json
import pool_data as pd
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

def pool_status_dict():
    "Return dict with current data for the pool."
    return {'temperature':
                {'water': pd.temperature(pd.POOL_TEMP_SENSOR),
                 'surface': pd.temperature(pd.SURFACE_TEMP_SENSOR),
                 'air': pd.temperature(pd.AIR_TEMP_SENSOR)},
            'light': pd.light_intensity(),
            'pressure': pd.pressure(pd.FILTER_PRESSURE_CHANNEL),
            'pump':
                {'status': pd.pump_status(),
                 'pressure': pd.pressure(pd.FILTER_PRESSURE_CHANNEL),
                 'power': pd.powerconsumption(pd.POWER_CONSUMPTION_CHANNEL)},
            'relay':
                {'pump': pd.pump_status()},
            'timestamp': '{:%d.%m.%Y %H:%M:%S}'.format(datetime.now())}

@app.route('/status')
def pool_status_json():
    return json.dumps(pool_status_dict())

@app.route('/pump/on')
def pump_on():
    run_pump(True)
    return pool_status_json()

@app.route('/pump/off')
def pump_off():
    run_pump(False)
    return pool_status_json()
