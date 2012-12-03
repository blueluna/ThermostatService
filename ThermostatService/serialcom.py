# -*- coding: utf-8 -*-

import serial
from serial.serialutil import SerialException

class SerialCom:
    def __init__(self, address):
        self._port = serial.Serial(address,
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
            parity=serial.PARITY_NONE,
            timeout=0.1,
            writeTimeout=0.1
        )

    def ReadCount(self):
        return self._port.inWaiting()

    def Checksum(self, sentence):
        checksum = 0
        func = lambda b: b
        if isinstance(sentence, (str)):
            func = lambda b: ord(b)
        for b in sentence:
            checksum ^= func(b)
        return checksum

    def Read(self):
        data = self._port.readline()
        if len(data) > 6 and data[0] == 36 and data[-5] == 42:
            checksum = self.Checksum(data[1:-5])
            text = data.decode('ascii').strip('\r\n')
            checksum_message = int(text[-2:], 16)
            if checksum == checksum_message:
                fields = text[1:-3].split(',')
                if fields[0] == 'TMP':
                    fields[1] = str(fields[1])
                    fields[2] = float(fields[2])
                elif fields[0] == 'CFG':
                    fields[1] = int(fields[1])
                    fields[2] = int(fields[2])
                    fields[3] = int(fields[3])
                else:
                    pass
                return fields
            else:
                print('Invalid checksum {0:02x} != {1:02x}'.format(checksum, checksum_message))
        return None

    def Write(self, method, fields):
        fs = [method] + fields
        sentence = ','.join([str(f) for f in fs])
        checksum = self.Checksum(sentence)
        sentence = '${0}*{1:02X}\r\n'.format(sentence, checksum)
        self._port.write(sentence.encode('ascii'))

# 'SCN', Scan for sensors
# 'TMP', Temperature
# 'CFG', Configure
# 'STO' Store configuration
