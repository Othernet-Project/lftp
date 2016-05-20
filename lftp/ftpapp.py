"""
This module contains FTPApplication which manages the FTP server
"""

from __future__ import unicode_literals

import os
import logging
import threading

from pyftpdlib.servers import FTPServer
from pyftpdlib.handlers import FTPHandler
from confloader import get_config_path, ConfDict

from .utils.settings import Settings
from .utils.system import on_interrupt
from .utils.logs import configure_logger
from .ftp.authorizer import FTPAuthorizer
from .control.server import ControlServer
from .ftp.filesystem import prepare_filesystem_class


class FTPApplication(object):
    DEFAULT_CONFIG_FILENAME = 'config.ini'
    CONFIG_DEFAULTS = {
        'catchall': True,
        'autojson': True
    }

    def __init__(self, root_dir):
        self.configure(root_dir)
        self.configure_logger()

        self.ftp_server = None
        self.ftp_server_thread = None
        self.control_server = None
        self.settings = Settings.from_file(self.config['app.settings'])

        self.setup_control_server()
        on_interrupt(self.stop)

    @property
    def ftp_enabled(self):
        return self.settings.get('ftp_enabled', True)

    @ftp_enabled.setter
    def ftp_enabled(self, value):
        self.settings['ftp_enabled'] = value
        self.settings.save()

    def configure(self, root_dir):
        default_path = os.path.join(root_dir, self.DEFAULT_CONFIG_FILENAME)
        self.config_path = get_config_path(default=default_path)
        self.config = ConfDict.from_file(self.config_path,
                                         defaults=self.CONFIG_DEFAULTS)
        self.config['root'] = root_dir

    def configure_logger(self):
        configure_logger(self.config)

    def setup_ftp_server(self):
        if self.ftp_server:
            return
        handler = FTPHandler
        authorizer = FTPAuthorizer()
        handler.authorizer = authorizer

        basepaths = self.get_basepaths()
        assert len(basepaths) > 0, 'Atleast one basepath expected'

        handler.abstracted_fs = prepare_filesystem_class(basepaths)
        authorizer.add_anonymous(basepaths[0])
        address = (self.config['ftp.host'], self.config['ftp.port'])
        self.ftp_server = FTPServer(address, handler)
        logging.info('FTP server configured at {}:{}'.format(
            address[0], address[1]))

    def teardown_ftp_server(self):
        logging.info('Stopping FTP server')
        self.ftp_server.close_all()
        self.ftp_server = None

    def setup_control_server(self):
        self.control_server = ControlServer(self.config, self.command_handler)

    def start_ftp_server(self):
        self.ftp_server_thread = _FTPThread(self.setup_ftp_server,
                                            self._run_ftp,
                                            self.teardown_ftp_server)
        self.ftp_server_thread.start()

    def stop_ftp_server(self):
        if not self.ftp_server or not self.ftp_server_thread:
            return
        self.ftp_server_thread.stop()
        self.ftp_server_thread.join()
        self.ftp_server_thread = None

    def run(self):
        if self.ftp_enabled:
            self.start_ftp_server()
        try:
            self.control_server.run()
        except KeyboardInterrupt:
            logging.info('Shutting down...')
            self.stop()

    def _run_ftp(self):
        self.ftp_server.serve_forever(blocking=False, timeout=1)

    def stop(self):
        self.stop_ftp_server()
        self.control_server.stop()

    def command_handler(self, command):
        if command['command'] == 'enable_ftp':
            return self.handle_ftp_enable(True)
        elif command['command'] == 'disable_ftp':
            return self.handle_ftp_enable(False)
        return {
            'success': False,
            'msg': 'Unknown command: {}'.format(command['command'])
        }

    def handle_ftp_enable(self, enabled):
        self.ftp_enabled = enabled
        if enabled and not self.ftp_server:
            self.setup_ftp_server()
            self.start_ftp_server()
        elif not enabled and self.ftp_server:
            self.stop_ftp_server()
        return {'success': True}

    def get_basepaths(self):
        chroot = self.config.get('ftp.chroot') or ''
        return [os.path.abspath(os.path.join(path, chroot))
                for path in self.config['ftp.basepaths']]


class _FTPThread(threading.Thread):
    def __init__(self, setup, run_loop, teardown):
        super(_FTPThread, self).__init__()

        self._setup = setup
        self._run_loop = run_loop
        self._teardown = teardown
        self._stop = threading.Event()

    def run(self):
        self._setup()
        while not self.stopped():
            self._run_loop()
        self._teardown()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
