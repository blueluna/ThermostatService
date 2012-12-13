# -*- coding: utf-8 -*-

import http
import json
import datetime
import http.client

class RPCError(Exception):
    def __init__(self, code=None, message=None):
        self._code = code
        self._message = message

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message


class Webfeeder:
    def __init__(self, host, uri):
        self._host = host
        self._uri = uri

    def _send_jsonrpc(self, id, method, params):
        client = http.client.HTTPConnection(self._host, timeout=5)
        req = json.dumps({'jsonrpc': '2.0', 'id': id, 'method': method, 'params': params })
        headers = {'content_type': 'text/javascript; charset=UTF-8'}
        client.request('POST', self._uri, body=req, headers=headers)
        response = client.getresponse()
        body = response.read()
        res = json.loads(body.decode('utf-8'))
        if 'error' in res:
            raise RPCError(res['error']['code'], res['error']['message'])
        elif 'result' in res:
            return res['result']
        return res

    def send_temperature(self, id, value):
        n = datetime.datetime.utcnow().replace(microsecond=0)
        return self._send_jsonrpc(id, 'thermostat.temperature.add',  [id, n.isoformat(), value])

    def set_configuration(self, id, mode, thresholdNormal, thresholdLow, hysteresisUpper, hysteresisLower, masterSensor):
        n = datetime.datetime.utcnow().replace(microsecond=0)
        return self._send_jsonrpc(id, 'thermostat.set_configuration',
            [id, n.isoformat(), mode, thresholdNormal, thresholdLow, hysteresisUpper, hysteresisLower, masterSensor])

    def get_configuration(self, id):
        return self._send_jsonrpc(id, 'thermostat.get_configuration',  [id])

    def send_state(self, id, state):
        n = datetime.datetime.utcnow().replace(microsecond=0)
        return self._send_jsonrpc(id, 'thermostat.set_state',  [id, n.isoformat(), state])
