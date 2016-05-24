====
LFTP
====

LFTP is a librarian component which acts as a FTP server, providing a unified 
view of the content across multiple root directories.

------------
Installation
------------

The component has the following dependencies:

- librarian-dashboard_
- `pyftpdlib <https://github.com/giampaolo/pyftpdlib>`_

To enable this component, add it to the list of components in librarian_'s
`config.ini` file, e.g.::

    [app]
    +components =
        lftp


-------------
Configuration
-------------

``ftp.port``
    Port on which the FTP server listens

``ftp.basepaths``
    Content paths for which the FTP server will provide a unified view.

``ftp.chroot``
    Optional directory present across all `basepaths` to which content listing 
    and other FTP operations are limited to. Users cannot explore outside of this 
    diretory.

    The path specified should be relative to `basepaths` and contained within them

Example::

    [ftp]
    port = 21

    basepaths = 
        /var/data/content_dir1
        /opt/lftp/content_dir2

     chroot = guest/data/

The above config will start an FTP server on port 21, which serves the 
content present at `/var/data/content_dir1/guest/data/` and `/opt/lftp/content_dir2/guest/data/`
