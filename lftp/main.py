"""
This module contains the methods to bootstrap the FTP server
"""

from __future__ import unicode_literals

import os

from .ftpapp import FTPApplication


PKGDIR = os.path.dirname(os.path.abspath(__file__))


def main():
    app = FTPApplication(PKGDIR)
    app.run()


if __name__ == '__main__':
    main()
