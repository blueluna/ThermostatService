# -*- coding: utf-8 -*-
import os
from logging import Logger, getLogger, Formatter
from logging.handlers import RotatingFileHandler

LOGGERNAME = 'ThermostatService'

def loggingSetup(logdir):
    path = os.path.join(logdir, 'thermostatservice.log')
    log = getLogger(LOGGERNAME)
    # Use rotating log of size 1 Mib and at most 5 log files
    handler = RotatingFileHandler(path, maxBytes=1048576, backupCount=5, encoding='utf-8')
    # change formatting to <time>\t<level>\t<message>
    handler.setFormatter(Formatter('%(asctime)s\t%(levelname)s\t%(message)s'))
    log.addHandler(handler)

def getLog():
    return getLogger(LOGGERNAME)
