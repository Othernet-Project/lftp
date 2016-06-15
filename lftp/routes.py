""" This module contains the routes and their handlers for LFTP """

from streamline import RouteBase

from librarian.core.exts import ext_container as exts


class FTPSettings(RouteBase):
    name = 'ftp:settings'
    path = '/ftp/settings/'
    kwargs = dict(unlocked=True)

    def post(self):
        enabled_param = self.request.params.get('ftp_enabled', '')
        enabled = enabled_param == 'ftp_enabled'
        exts.ftp_server.ftp_enable(enabled)
