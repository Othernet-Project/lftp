"""
This module contains the methods to bootstrap the FTP server application.
"""

from __future__ import unicode_literals

from gevent import monkey
monkey.patch_all(thread=False, select=False)

import os

from .ftpapp import FTPApplication


PKGDIR = os.path.dirname(os.path.abspath(__file__))


def main():
    app = FTPApplication(PKGDIR)
    app.run()


if __name__ == '__main__':
    main()
