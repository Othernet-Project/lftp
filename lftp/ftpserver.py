"""
This module contains LFTPServer, which manages the FTP server.
"""

from __future__ import unicode_literals

import os
import logging
import threading

from pyftpdlib.servers import MultiprocessFTPServer
from pyftpdlib.handlers import FTPHandler

from .ftp.authorizer import FTPAuthorizer
from .ftp.filesystem import UnifiedFilesystem


class LFTPServer(object):
    def __init__(self, config, setup):
        self.config = config
        self.setup = setup

        self.ftp_server = None
        self.ftp_server_thread = None

    @property
    def enabled(self):
        ftp_settings = self.setup.get('ftp', {})
        return ftp_settings.get('enabled', True)

    @enabled.setter
    def enabled(self, enabled):
        ftp_settings = self.setup.get('ftp', {})
        ftp_settings['enabled'] = enabled
        self.setup.append({'ftp': ftp_settings})

    @property
    def status(self):
        return self.enabled and self.ftp_server

    def setup_ftp(self):
        if self.ftp_server:
            return
        handler = FTPHandler
        authorizer = FTPAuthorizer()
        handler.authorizer = authorizer

        basepaths = self.get_basepaths()
        assert len(basepaths) > 0, 'Atleast one basepath expected'

        handler.abstracted_fs = UnifiedFilesystem
        handler.abstracted_fs.basepaths = basepaths
        handler.abstracted_fs.blacklist = self.config.get('ftp.blacklist')
        handler.use_sendfile = True
        authorizer.add_anonymous(basepaths[0])
        address = ('', self.config['ftp.port'])
        self.ftp_server = MultiprocessFTPServer(address, handler)

    def teardown_ftp(self):
        self.ftp_server.close_all()
        self.ftp_server = None
        logging.info('FTP server stopped')

    def start_ftp(self):
        # Start the ftp server on a separate thread so that it does not block
        # gevent's loop
        self.ftp_server_thread = _StoppableThread(self._run_ftp,
                                                  setup=self.setup_ftp,
                                                  teardown=self.teardown_ftp)
        self.ftp_server_thread.start()
        logging.info('FTP server started on port {}'.format(
            self.config['ftp.port']))

    def stop_ftp(self):
        if not self.ftp_server or not self.ftp_server_thread:
            return
        self.ftp_server_thread.stop()
        self.ftp_server_thread = None

    def start(self):
        if self.enabled:
            self.start_ftp()

    def _run_ftp(self):
        # Run the FTP io loop for `timeout` seconds
        self.ftp_server.serve_forever(blocking=False, timeout=0.5)

    def stop(self):
        self.stop_ftp()

    def ftp_enable(self, enabled):
        self.enabled = enabled
        if enabled and not self.ftp_server:
            self.setup_ftp()
            self.start_ftp()
        elif not enabled and self.ftp_server:
            self.stop_ftp()

    def get_basepaths(self):
        chroot = self.config.get('ftp.chroot') or ''
        return [os.path.abspath(os.path.join(path, chroot))
                for path in self.config['ftp.basepaths']]


class _StoppableThread(threading.Thread):
    """
    This class represents a stoppable thread which calls the provided callback
    in a loop until stopped. It accepts callbacks which are called just before
    and after the loop.
    """

    def __init__(self, run_handler, setup=None, teardown=None):
        super(_StoppableThread, self).__init__()

        self._run_handler = run_handler
        self._setup = setup
        self._teardown = teardown

        self._stop = threading.Event()

    def run(self):
        if self._setup:
            self._setup()
        while not self.stopped():
            self._run_handler()
        if self._teardown:
            self._teardown()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
