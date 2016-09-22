"""
This module contains lftp hooks for librarian component lifecycle.
"""

import functools

from .ftpserver import LFTPServer

from librarian.core.contrib.auth.users import User
from librarian.core.exports import hook
from librarian.core.exts import ext_container as exts


READ_WRITE = 'elradfmw'


def user_created(handler, instance):
    """
    When a new superuser is created, add it to the list of authorized ftp
    users with read-write access.
    """
    if not instance.is_superuser:
        return
    # accept only superusers
    home = handler.abstracted_fs.basepaths[0]
    handler.authorizer.add_user(instance.username,
                                instance.password,
                                home,
                                perm=READ_WRITE)


def install_users(handler):
    """
    LFTP setup hook which is called once during the setup of the ftp server and
    is supposed install superusers registered within librarian as write-capable
    ftp users.
    """
    superusers = User.from_group('superuser') or []
    home = handler.abstracted_fs.basepaths[0]
    for user in superusers:
        handler.authorizer.add_user(user.username,
                                    user.password,
                                    home,
                                    perm=READ_WRITE)
    exts.events.subscribe(User.USER_CREATED_EVENT,
                          functools.partial(user_created, handler))


def register_onmodify(handler):
    """
    Register a callback function to be invoked when a path is being modified
    in some way (created, deleted, renamed, ...).
    """
    handler.abstracted_fs.on_modified.append(exts.fsal.refresh_path)


@hook('post_start')
def post_start(supervisor):
    ftp_server = LFTPServer(supervisor.config,
                            supervisor.exts.setup,
                            setup_hooks=(install_users, register_onmodify))
    ftp_server.start()
    supervisor.exts.ftp_server = ftp_server


@hook('shutdown')
def shutdown(supervisor):
    supervisor.exts.ftp_server.stop()


@hook('immediate_shutdown')
def immediate_shutdown(supervisor):
    supervisor.exts.ftp_server.stop()
