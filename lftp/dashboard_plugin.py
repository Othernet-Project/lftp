"""
This module contains the DashboardPlugin for FTP.
"""

from __future__ import unicode_literals

from bottle_utils.i18n import lazy_gettext as _

from librarian.core.exts import ext_container as exts
from librarian.presentation.dashboard.dashboard import DashboardPlugin


class FTPDashboardPlugin(DashboardPlugin):
    # Translators, used as dashboard section title for FTP
    heading = _('FTP Settings')
    name = 'ftp'

    def get_template(self):
        return 'ftp/dashboard'

    def get_context(self):
        ftp_server = exts.ftp_server
        return dict(status=ftp_server.status)
