# -*- coding: utf-8 -*-

import time, datetime
import bisect
from .configuration import Configuration
from .serialcom import SerialCom, SerialException
from .webfeeder import Webfeeder
from .iso8601 import parse_date

TMP_TIMEOUT = 300.0

def main():
    cfg = Configuration()
    cfg.Load()
    try:
        com = SerialCom(cfg.SerialPort)
    except SerialException:
        com = None
    feeder = Webfeeder(cfg.WebServiceHost, cfg.WebServiceUri)
    serviceId = cfg.WebServiceId
    devices = {}
    device_cfg = None
    service_cfg = None
    check_timeout = time.time() + 10.0;
    while (True):
        t = time.time()
        try:
            if t > check_timeout:
                if device_cfg:
                    service_cfg = feeder.get_configuration(serviceId)
                    print(service_cfg)
                    dt_service = parse_date(service_cfg['datetime'])
                    dt_device = parse_date(device_cfg['datetime'])
                    if dt_service > dt_device:
                        com.Write('CFG',
                            [
                                service_cfg['mode'], service_cfg['thresholdNormal'], service_cfg['thresholdLow'],
                                service_cfg['hysteresisUpper'], service_cfg['hysteresisLower'], service_cfg['masterSensor']
                            ])
                    check_timeout = t + TMP_TIMEOUT
                else:
                    if com:
                        com.Write('CFG', [])
                    check_timeout = t + 10.0
            if com:
                sentence = com.Read()
                if sentence is None:
                    continue
                print(sentence)
                if sentence[0] == 'TMP':
                    device = sentence[1]
                    value = sentence[2]
                    if device in devices:
                        if t > devices[device]['timeout']:
                            count = len(devices[device]['values'])
                            median = devices[device]['values'][count//2]
                            feeder.send_temperature(device, median)
                            devices[device]['timeout'] = t + TMP_TIMEOUT
                            devices[device]['values'] = [value]
                        else:
                            bisect.insort(devices[device]['values'], value)
                            print('time left: {0:.0f}'.format(devices[device]['timeout'] - t))
                    else:
                        devices[device] = {'values': [sentence[2]], 'timeout': t + TMP_TIMEOUT }
                if sentence[0] == 'CFG' and len(sentence) == 7:
                    mode = sentence[1]
                    thresholdNormal = sentence[2]
                    thresholdLow = sentence[3]
                    hysteresisUpper = sentence[4]
                    hysteresisLower = sentence[5]
                    masterSensor = sentence[6]
                    dt = datetime.datetime.utcnow().replace(microsecond=0)
                    device_cfg = {
                        'mode': mode,
                        'thresholdNormal': thresholdNormal,
                        'thresholdLow': thresholdLow,
                        'hysteresisUpper': hysteresisUpper,
                        'hysteresisLower': hysteresisLower,
                        'masterSensor': masterSensor,
                        'datetime': dt.isoformat()
                    }
                    feeder.set_configuration(
                        serviceId, mode, thresholdNormal, thresholdLow,
                        hysteresisUpper, hysteresisLower, masterSensor)
                if sentence[0] == 'CTL' and len(sentence) == 2:
                    state = sentence[1]
                    feeder.send_state(serviceId, state)
                if sentence[0] == 'SCN':
                    pass
        except KeyboardInterrupt:
            break
    else:
        print("Couldn't open serial port {0}".format(cfg.SerialPort))
    cfg.Store()

if __name__ == "__main__":
    main()
