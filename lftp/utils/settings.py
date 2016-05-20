"""
This module contains :py:class:`Settings` which reads and writes settings to
files
"""

from __future__ import unicode_literals

import os
import json
import logging


class Settings(object):
    def __init__(self, path):
        self.path = path
        self.load()

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def get(self, key, default=None):
        return self._data.get(key, default)

    def load(self):
        if os.path.isfile(self.path):
            try:
                with open(self.path, 'r') as f:
                    self._data = json.load(f)
            except ValueError:
                logging.error('Error decoding settings json')
                self._data = {}
        else:
            self._data = {}

    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self._data, f)

    @classmethod
    def from_file(cls, path):
        return cls(path)
