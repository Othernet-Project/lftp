"""
This module contains utility methods related to logging
"""

from __future__ import unicode_literals

import logging.config
import sys


def configure_logger(config):
    logging.config.dictConfig({
        'version': 1,
        'root': {
            'handlers': ['file', 'console'],
            'level': logging.DEBUG,
        },
        'handlers': {
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'filename': config['logging.output'],
                'maxBytes': config['logging.size'],
                'backupCount': config['logging.backups'],
            },
            'console': {
                'class': 'logging.StreamHandler',
                'level': logging.INFO,
                'formatter': 'default',
                'stream': sys.stdout
            }
        },
        'formatters': {
            'default': {
                'format': config['logging.format'],
                'datefmt': config['logging.date_format'],
            },
        },
    })
