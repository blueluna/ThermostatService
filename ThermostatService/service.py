# -*- coding: utf-8 -*-

import time, datetime
import bisect
import argparse
import logging, logging.handlers
import sys
from .configuration import Configuration
from .serialcom import SerialCom, SerialException
from .webfeeder import Webfeeder, RPCError
from .iso8601 import parse_date
from .log import loggingSetup, getLog

TMP_TIMEOUT = 300.0

def openSerialPort(cfg):
    try:
        com = SerialCom(cfg.SerialPort)
    except SerialException:
        getLog().exception('Failed to open serial port.')
        com = None
    return com

def main():
    parser = argparse.ArgumentParser(description='Thermostat service.')
    parser.add_argument("-d", "--debug", help="Debug output", action="store_true")
    parser.add_argument("-f", "--front", help="Output to stdout.", action="store_true")
    args = parser.parse_args()
    cfg = Configuration()
    cfg.Load()
    loggingSetup(cfg.LoggingDir)
    log = getLog()
    if args.front:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s'))
        log.addHandler(handler)
    if args.debug:
        log.setLevel('DEBUG')
    else:
        log.setLevel('INFO')
    log.info("Starting service");
    com = openSerialPort(cfg)
    feeder = Webfeeder(cfg.WebServiceHost, cfg.WebServiceUri)
    serviceId = cfg.WebServiceId
    devices = {}
    device_cfg = None
    service_cfg = None
    last_cfg = None
    check_timeout = time.time() + 10.0;
    while (True):
        try:
            t = time.time()
            if t > check_timeout:
                service_cfg = feeder.get_configuration(serviceId)
                dt_service = parse_date(service_cfg['datetime'])
                if last_cfg == None or dt_service > last_cfg:
                    if com:
                        com.Write('CFG', [
                            int(service_cfg['mode']), int(service_cfg['thresholdNormal']),
                            int(service_cfg['thresholdLow']), int(service_cfg['hysteresisUpper']),
                            int(service_cfg['hysteresisLower']), service_cfg['masterSensor']
                            ])
                check_timeout = t + TMP_TIMEOUT
                last_cfg = dt_service
            if com:
                sentence = com.Read()
                if sentence is None:
                    continue
                if sentence[0] != 'TMP':
                    log.debug(sentence)
                if sentence[0] == 'TMP':
                    device = sentence[1]
                    value = sentence[2]
                    if device in devices:
                        if t > devices[device]['timeout']:
                            count = len(devices[device]['values'])
                            median = devices[device]['values'][count//2]
                            try:
                                feeder.send_temperature(device, median)
                            except RPCError as error:
                                log.error(error.message)
                            except Exception as error:
                                log.error(error)
                            devices[device]['timeout'] = t + TMP_TIMEOUT
                            devices[device]['values'] = [value]
                        else:
                            bisect.insort(devices[device]['values'], value)
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
                    try:
                        feeder.set_configuration(
                            serviceId, mode, thresholdNormal, thresholdLow,
                            hysteresisUpper, hysteresisLower, masterSensor)
                    except RPCError as error:
                        log.exception(error.message)
                    except Exception as error:
                        log.exception("An error occured")
                if sentence[0] == 'CTL' and len(sentence) == 2:
                    state = sentence[1]
                    try:
                        feeder.set_state(serviceId, state)
                    except RPCError as error:
                        log.error(error.message)
                    except Exception as error:
                        log.error(error)
                if sentence[0] == 'SCN':
                    pass
            else:
                break
        except KeyboardInterrupt:
            break
        except Exception as error:
            log.exception("An error occured")
            time.sleep(1.0)
    log.info("Ending service");
    cfg.Store()

if __name__ == "__main__":
    main()
