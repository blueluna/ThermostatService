# -*- coding: utf-8 -*-

import http
import json
import datetime
import http.client

class Webfeeder:
    def __init__(self, host):
        self._client = http.client.HTTPConnection(host, timeout=5)

    def send_temperature(self, id, value):
        n = datetime.datetime.now().replace(microsecond=0)
        req = json.dumps({'jsonrpc': '2.0', 'id': id, 'method': 'thermostat.temperature.add', 'params': [ id, n.isoformat(sep=' '), value ] })
        print(req)
        headers = {'content_type': 'text/javascript; charset=UTF-8'}
        try:
            self._client.request('post', '/json/', body=req, headers=headers)
            response = self._client.getresponse()
            body = response.read()
            res = json.loads(body.decode('utf-8'))
            print(res)
        except Exception as e:
            print(e)
            pass
