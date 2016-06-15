"""
This module contains lftp hooks for librarian component lifecycle.
"""

from .ftpserver import LFTPServer

from librarian.core.exports import hook


@hook('post_start')
def post_start(supervisor):
    ftp_server = LFTPServer(supervisor.config, supervisor.exts.setup)
    ftp_server.start()
    supervisor.exts.ftp_server = ftp_server


@hook('shutdown')
def shutdown(supervisor):
    supervisor.exts.ftp_server.stop()


@hook('immediate_shutdown')
def immediate_shutdown(supervisor):
    supervisor.exts.ftp_server.stop()
