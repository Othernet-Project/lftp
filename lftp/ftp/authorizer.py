"""
This module contains pyftpdlib authorizer.
"""

from __future__ import unicode_literals

import os

import pbkdf2

from pyftpdlib.authorizers import DummyAuthorizer, AuthenticationFailed


class FTPAuthorizer(DummyAuthorizer):

    def add_user(self, username, password, homedir, perm='elr',
                 msg_login="Login successful.", msg_quit="Goodbye."):
        """
        Add a user to the virtual users table.
        AuthorizerError exceptions raised on error conditions such as
        invalid permissions, duplicate usernames.
        Optional perm argument is a string referencing the user's
        permissions explained below:
        Read permissions:
            - "e" = change directory (CWD command)
            - "l" = list files (LIST, NLST, STAT, MLSD, MLST, SIZE, MDTM
                                commands)
            - "r" = retrieve file from the server (RETR command)
        Write permissions:
            - "a" = append data to an existing file (APPE command)
            - "d" = delete file or directory (DELE, RMD commands)
            - "f" = rename file or directory (RNFR, RNTO commands)
            - "m" = create directory (MKD command)
            - "w" = store a file to the server (STOR, STOU commands)
            - "M" = change file mode (SITE CHMOD command)
        Optional msg_login and msg_quit arguments can be specified to
        provide customized response strings when user log-in and quit.
        """
        if self.has_user(username):
            raise ValueError('user %r already exists' % username)
        if not isinstance(homedir, unicode):
            homedir = homedir.decode('utf8')
        homedir = os.path.realpath(homedir)
        user = {
            'pwd': str(password),
            'home': homedir,
            'perm': perm,
            'operms': {},
            'msg_login': str(msg_login),
            'msg_quit': str(msg_quit)
        }
        self.user_table[username] = user

    def add_anonymous(self, homedir, **kwargs):
        """
        Add an anonymous user to the virtual users table.
        AuthorizerError exception raised on error conditions such as
        invalid permissions, missing home directory, or duplicate
        anonymous users.
        The keyword arguments in kwargs are the same expected by
        add_user method: "perm", "msg_login" and "msg_quit".
        The optional "perm" keyword argument is a string defaulting to
        "elr" referencing "read-only" anonymous user's permissions.
        Using write permission values ("adfmwM") results in a
        RuntimeWarning.
        """
        self.add_user('anonymous', '', homedir, **kwargs)

    def validate_authentication(self, username, password, handler):
        """
        Raises AuthenticationFailed if supplied username and
        password don't match the stored credentials, else return
        None.
        """
        msg = "Authentication failed."
        if not self.has_user(username):
            if username == 'anonymous':
                msg = "Anonymous access not allowed."
            raise AuthenticationFailed(msg)
        if username != 'anonymous':
            encrypted = self.user_table[username]['pwd']
            if encrypted != pbkdf2.crypt(password, encrypted):
                raise AuthenticationFailed(msg)
