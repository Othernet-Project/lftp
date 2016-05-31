"""
This module contains :py:class:`ControlServer`, which provides an Unix domain
based IPC API to enable/disable the FTP server.
"""

from __future__ import unicode_literals

import os
import json
import stat
import socket
import logging

from contextlib import contextmanager

from gevent.server import StreamServer


class ControlServer(object):
    def __init__(self, config, command_handler):
        self.socket_path = config['app.socket']
        self.command_handler = command_handler
        self.server = None

    def run(self):
        with self.open_socket() as sock:
            logging.info('Control server started at {}'.format(
                self.socket_path))
            self.server = StreamServer(sock, self.request_handler)
            self.server.serve_forever()

    def stop(self):
        if self.server and self.server.started:
            self.server.stop()

    def request_handler(self, client_socket, address):
        try:
            command = self.parse_request(self.read_request(client_socket))
            result = self.command_handler(command)
            self.send_response(client_socket, self.compose_response(result))
        except socket.error as exc:
            logging.exception('Unable to send response: {}'.format(exc))
        except Exception as exc:
            logging.exception(
                'Unexpected exception while handling command: {}'.format(exc))

    def prepare_socket(self):
        try:
            os.unlink(self.socket_path)
        except OSError:
            if os.path.exists(self.socket_path):
                raise
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(self.socket_path)
        try:
            os.chmod(self.socket_path, stat.S_IRWXU | stat.S_IRWXG)
        except OSError:
            logging.exception(
                'Error while setting file permissions for socket {}'.format(
                    self.socket_path))
            raise
        sock.listen(1)
        return sock

    @contextmanager
    def open_socket(self):
        sock = self.prepare_socket()
        try:
            yield sock
        finally:
            sock.close()

    @staticmethod
    def read_request(sock, buff_size=2048, encoding='utf8'):
        data = buff = sock.recv(buff_size)
        while buff and '\0' not in buff:
            buff = sock.recv(buff_size)
            data += buff
        return data[:-1].decode(encoding)

    @staticmethod
    def send_response(client_socket, response):
        if not response[-1] == '\0':
            response += '\0'
        client_socket.sendall(response)

    @staticmethod
    def parse_request(request_str):
        return json.loads(request_str)

    @staticmethod
    def compose_response(response):
        return json.dumps(response)
