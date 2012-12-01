# -*- coding: utf-8 -*-
__author__ = 'Erik Svensson'

import serial

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

    def readCount(self):
        return self._port.inWaiting()

    def checksum(self, sentence):
        checksum = 0
        func = lambda b: b
        if isinstance(sentence, (str)):
            func = lambda b: ord(b)
        for b in sentence:
            checksum ^= func(b)
        return checksum

    def read(self):
        data = self._port.readline()
        print(data.decode('ascii').strip('\r\n'))
        if len(data) > 6 and data[0] == 36 and data[-5] == 42:
            checksum = self.checksum(data[1:-5])
            text = data.decode('ascii').strip('\r\n')
            checksum_message = int(text[-2:], 16)
            if checksum == checksum_message:
                fields = text[1:-3].split(',')
                if fields[0] == 'TMP':
                    fields[1] = int(fields[1], 16)
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
        return None, None, None

    def write(self, method, fields):
        fs = [method] + fields
        sentence = ','.join([str(f) for f in fs])
        checksum = self.checksum(sentence)
        sentence = '${0}*{1:02X}\r\n'.format(sentence, checksum)
        print(sentence.strip('\r\n'))
        data = self._port.write(sentence.encode('ascii'))

com = SerialCom('COM9')

count = com.readCount()
while count <= 0:
    count = com.readCount()
print('{0} {1:08X} {2}'.format(*com.read()))

com.write('CFG', [0, 200, 50])
count = com.readCount()
while count <= 0:
    count = com.readCount()
print(*com.read())

com.write('CFG', [])

while True:
    try:
        count = com.readCount()
        while count <= 0:
            count = com.readCount()
        print(*com.read())
    except KeyboardInterrupt:
        break

# 'SCN', Scan for sensors
# 'TMP', Temperature
# 'CFG', Configure
# 'STO' Store configuration

# 0x00, id, 0x4D
# 0x01, version
# 0x10, selected threshold
# 0x11, threshold 1
# 0x12, threshold 2
