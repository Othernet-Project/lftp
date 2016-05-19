"""
This module contains FTPApplication which manages the FTP server
"""

from __future__ import unicode_literals

import os
import logging

from pyftpdlib.servers import FTPServer
from pyftpdlib.handlers import FTPHandler
from confloader import get_config_path, ConfDict

from .utils.logs import configure_logger
from .ftp.filesystem import prepare_filesystem_class
from .ftp.authorizer import FTPAuthorizer


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
        self.setup_ftp_server()

    def configure(self, root_dir):
        default_path = os.path.join(root_dir, self.DEFAULT_CONFIG_FILENAME)
        self.config_path = get_config_path(default=default_path)
        self.config = ConfDict.from_file(self.config_path,
                                         defaults=self.CONFIG_DEFAULTS)
        self.config['root'] = root_dir

    def configure_logger(self):
        configure_logger(self.config)

    def setup_ftp_server(self):
        handler = FTPHandler
        authorizer = FTPAuthorizer()
        handler.authorizer = authorizer

        basepaths = self.get_basepaths()
        assert len(basepaths) > 0, 'Atleast one basepath expected'

        handler.abstracted_fs = prepare_filesystem_class(basepaths)
        authorizer.add_anonymous(basepaths[0])
        address = (self.config['ftp.host'], self.config['ftp.port'])
        self.ftp_server = FTPServer(address, handler)

    def run(self):
        address = self.ftp_server.address
        logging.info('FTP server started at {}:{}'.format(
            address[0], address[1]))
        self.ftp_server.serve_forever()

    def get_basepaths(self):
        chroot = self.config.get('ftp.chroot') or ''
        return [os.path.abspath(os.path.join(path, chroot))
                for path in self.config['ftp.basepaths']]
