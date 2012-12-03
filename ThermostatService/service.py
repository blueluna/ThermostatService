# -*- coding: utf-8 -*-

from .configuration import Configuration
from .serialcom import SerialCom, SerialException
from .webfeeder import Webfeeder

def main():
    cfg = Configuration()
    cfg.Load()
    try:
        com = SerialCom(cfg.SerialPort)
    except SerialException:
        com = None
    if com:
        feeder = Webfeeder(cfg.WebServiceHost)
        while (True):
            try:
                sentence = com.Read()
                if sentence is None:
                    continue
                if sentence[0] == 'TMP':
                    print(sentence)
                    feeder.send_temperature(sentence[1], sentence[2])
            except KeyboardInterrupt:
                break
    cfg.Store()

if __name__ == "__main__":
    main()
