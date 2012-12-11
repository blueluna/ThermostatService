# -*- coding: utf-8 -*-

import time
import bisect
from .configuration import Configuration
from .serialcom import SerialCom, SerialException
from .webfeeder import Webfeeder

TMP_TIMEOUT = 300.0

def main():
    cfg = Configuration()
    cfg.Load()
    try:
        com = SerialCom(cfg.SerialPort)
    except SerialException:
        com = None
    if com:
        feeder = Webfeeder(cfg.WebServiceHost, cfg.WebServiceUri)
        serviceId = cfg.WebServiceId
        devices = {}
        while (True):
            t = time.time()
            try:
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
                if sentence[0] == 'CFG' and len(sentence) == 4:
                    mode = sentence[1]
                    thresholdNormal = sentence[2]
                    thresholdLow = sentence[3]
                    feeder.send_configuration(serviceId, mode, thresholdNormal, thresholdLow)
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
