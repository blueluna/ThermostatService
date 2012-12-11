# -*- coding: utf-8 -*-

import http
import json
import datetime
import http.client

class Webfeeder:
    def __init__(self, host, uri):
        self._host = host
        self._uri = uri

    def _send_jsonrpc(self, id, method, params):
        client = http.client.HTTPConnection(self._host, timeout=5)
        req = json.dumps({'jsonrpc': '2.0', 'id': id, 'method': method, 'params': params })
        print(req)
        headers = {'content_type': 'text/javascript; charset=UTF-8'}
        client.request('POST', self._uri, body=req, headers=headers)
        response = client.getresponse()
        body = response.read()
        res = json.loads(body.decode('utf-8'))
        print(res)
        return res

    def send_temperature(self, id, value):
        n = datetime.datetime.utcnow().replace(microsecond=0)
        try:
            self._send_jsonrpc(id, 'thermostat.temperature.add',  [id, n.isoformat(), value])
        except Exception as e:
            print(e)

    def send_configuration(self, id, mode, thresholdNormal, thresholdLow):
        n = datetime.datetime.utcnow().replace(microsecond=0)
        try:
            self._send_jsonrpc(id, 'thermostat.set_configuration',  [id, n.isoformat(), mode, thresholdNormal, thresholdLow])
        except Exception as e:
            print(e)

    def send_state(self, id, state):
        n = datetime.datetime.utcnow().replace(microsecond=0)
        try:
            self._send_jsonrpc(id, 'thermostat.set_state',  [id, n.isoformat(), state])
        except Exception as e:
            print(e)
