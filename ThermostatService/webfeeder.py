# -*- coding: utf-8 -*-

import http
import json
import datetime
import http.client
import pytz

class Webfeeder:
    def __init__(self, host):
        self._host = host
        self._timezone = pytz.timezone('Europe/Stockholm')

    def send_temperature(self, id, value):
        client = http.client.HTTPConnection(self._host, timeout=5)
        n = datetime.datetime.now().replace(microsecond=0)
        n = self._timezone.localize(n)
        req = json.dumps({'jsonrpc': '2.0', 'id': id, 'method': 'thermostat.temperature.add', 'params': [ id, n.isoformat(sep=' '), value ] })
        print(req)
        headers = {'content_type': 'text/javascript; charset=UTF-8'}
        try:
            client.request('post', '/json/', body=req, headers=headers)
            response = client.getresponse()
            body = response.read()
            res = json.loads(body.decode('utf-8'))
            print(res)
        except Exception as e:
            print(e)
            pass
