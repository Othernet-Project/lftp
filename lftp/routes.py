""" This module contains the routes and their handlers for LFTP """

from bottle import request


def set_settings():
    ftp_enabled_param = request.params.get('ftp_enabled', '')
    enabled = ftp_enabled_param == 'ftp_enabled'
    request.app.supervisor.exts.ftp_server.ftp_enable(enabled)


def routes(config):
    skip_plugins = config['app.skip_plugins']
    return (
        ('ftp_settings:save', set_settings,
         'POST', '/ftp/settings/', dict(unlocked=True, skip=skip_plugins)),
    )
