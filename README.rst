====
LFTP
====

LFTP is a lean and configurable FTP server application which provides a unified 
view of the content across multiple root directories.

It provides an alternate TCP based IPC calls to enable/disable the FTP server.

------
Config
------
LFTP is configured via a ini-style configuration file, containing `[section]` 
header and `name = value` entries. `confloader` is used to parse the config 
file.

The config for LFTP has two main sections:
 - app section
 - ftp section

A sample config can be found at `lftp/config.ini`

app section
^^^^^^^^^^^
This section contains app-level configurations, specifying the Unix domain 
socket for IPC calls and the path for settings file. Eg.::

    [app]
    # Socket for IPC calls
    socket = /var/run/lftp.ctrl

    # Path for the settings file, which is used to store runtime generated settings
    settings = /opt/lftp/settings.json


ftp section
^^^^^^^^^^^
This section contains the FTP server component configuration. It specifies 
FTP connection settings and the content directory paths. Eg.::

    [ftp]
    host = 127.0.0.1
    port = 21

    # Content paths for which the FTP will provide a unified view.
    basepaths = 
        /var/data/content_dir1
        /opt/lftp/content_dir2

     chroot = guest/data/

The above config will start an FTP server at `127.0.0.1:21` which serves the 
content present at `/var/data/content_dir1/guest/data/` and `/opt/lftp/content_dir2/guest/data/`

-------------
Settings JSON
-------------
LFTP maintains its runtime generated config at the path specified by the config 
key `app.settings` as a JSON file. This file is used to store application data
based on changes in its runtime status, like the current status of FTP 
server component, in a flat structure. The file is not meant to be modified by 
external applications.

Currently, the following data are tracked by the settings file:
  - `ftp_enabled`
      Boolean which represents if the FTP server component is enabled. Defaults to `true`

A typical settings file: ::

    {
        "ftp_enabled": true
    }
