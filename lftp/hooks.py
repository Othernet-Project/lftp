"""
This module contains lftp hooks for librarian component lifecycle.
"""

from .ftpserver import LFTPServer
from .dashboard_plugin import FTPDashboardPlugin


def initialize(supervisor):
    ftp_server = LFTPServer(supervisor.config, supervisor.exts.setup)
    ftp_server.start()
    supervisor.exts.ftp_server = ftp_server
    supervisor.exts.dashboard.register(FTPDashboardPlugin)


def shutdown(supervisor):
    supervisor.exts.ftp_server.stop()
