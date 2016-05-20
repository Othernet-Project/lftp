"""
This module contains :py:class:`LFTPClient`
"""

import json
import socket


class LFTPException(Exception):
    pass


class LFTPClient(object):

    def __init__(self, socket_path):
        self.socket_path = socket_path

    def enable_ftp(self):
        return self.run_command('enable_ftp')

    def disable_ftp(self):
        return self.run_command('disable_ftp')

    def run_command(self, command, params={}):
        command_json = {}
        command_json['command'] = command
        command_json['params'] = params
        response_json = self.send_command(command_json)
        success = response_json['success']
        if success:
            return success
        else:
            raise LFTPException(response_json['msg'])

    def send_command(self, command_json):
        message = json.dumps(command_json) + '\0'
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.socket_path)
            sock.sendall(message)
            response = self.read_response(sock)
            return json.loads(response)
        except socket.error:
            if sock:
                sock.close()
            sock = None
            raise LFTPException('Could not connect to LFTP')

    def read_response(self, sock, buff_size=2028):
        data = buff = sock.recv(buff_size)
        while buff and '\0' not in buff:
            buff = sock.recv(buff_size)
            data += buff
        return data[:-1]
