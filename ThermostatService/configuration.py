# -*- coding: utf-8 -*-

import os
import json

class Configuration:
    def __init__(self):
        self._filepath = os.path.expandvars('$HOME/.config/thermostatservice/configuration.json')
        os.makedirs(os.path.dirname(self._filepath), exist_ok=True)
        self._configuration = {
            'serial':
                {
                    'port': '/dev/ttyS0'
                },
            'webservice':
                {
                    'host': 'http://coldstar.mine.nu/thermostat/'
                }
        }

    def Load(self):
        try:
            with open(self._filepath, 'r') as f:
                cfg = json.load(f)
                if isinstance(cfg, dict):
                    self._UpdateMap(self._configuration, cfg)
        except IOError:
            self.Store()

    def Store(self):
        with open(self._filepath, 'w') as f:
            json.dump(self._configuration, f, indent=2)

    def _UpdateMap(self, a, b):
        for key in a.keys():
            if key in b:
                if isinstance(a[key], dict):
                    if isinstance(b[key], dict):
                        self._UpdateMap(a[key], b[key])
                else:
                    a[key] = b[key]

    @property
    def SerialPort(self):
        return self._configuration['serial']['port']

    @property
    def WebServiceHost(self):
        return self._configuration['webservice']['host']
