"""
This module contains lftp hooks for librarian component lifecycle.
"""

from .ftpserver import LFTPServer

from librarian.core.contrib.auth.users import User
from librarian.core.exports import hook


def install_users(handler):
    """
    LFTP setup hook which is called once during the setup of the ftp server and
    is supposed install superusers registered within librarian as write-capable
    ftp users.
    """
    superusers = User.from_group('superuser') or []
    for user in superusers:
        home = handler.abstracted_fs.basepaths[0]
        handler.authorizer.add_user(user.username,
                                    user.password,
                                    home,
                                    perm='elradfmw')


@hook('post_start')
def post_start(supervisor):
    ftp_server = LFTPServer(supervisor.config,
                            supervisor.exts.setup,
                            setup_hooks=(install_users,))
    ftp_server.start()
    supervisor.exts.ftp_server = ftp_server


@hook('shutdown')
def shutdown(supervisor):
    supervisor.exts.ftp_server.stop()


@hook('immediate_shutdown')
def immediate_shutdown(supervisor):
    supervisor.exts.ftp_server.stop()
