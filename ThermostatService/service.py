# -*- coding: utf-8 -*-

from .configuration import Configuration
from .serialcom import SerialCom

def main():
    cfg = Configuration()
    cfg.Load()
    com = SerialCom(cfg.SerialPort)
    while (True):
        sentence = com.Read()
        if sentence is None:
            continue
        if sentence[0] == 'TMP':
            print(sentence)
            break;
    cfg.Store()

if __name__ == "__main__":
    main()
