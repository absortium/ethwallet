__author__ = 'andrew.shvv@gmail.com'

import json
import socket

import requests
from requests.exceptions import ConnectionError as RequestsConnectionError

from .constants import GETH_DEFAULT_RPC_PORT
from .exceptions import (ConnectionError, BadStatusCode, BadJson)


class HTTPInterface():
    def __init__(self, host='localhost', port=GETH_DEFAULT_RPC_PORT, tls=False):
        self.host = host
        self.port = port
        self.tls = tls

    def send(self, data, *args, **kwargs):
        scheme = 'http'
        if self.tls:
            scheme += 's'
        url = '{}://{}:{}'.format(scheme, self.host, self.port)
        try:
            r = requests.post(url, data=json.dumps(data), *args, **kwargs)
        except RequestsConnectionError:
            raise ConnectionError

        if r.status_code != 200:
            raise BadStatusCode(r.status_code)

        try:
            return r.json()
        except ValueError:
            raise BadJson(r.text)


MSGLEN = 4096


class IPCInterface():
    def __init__(self, ipc=None):
        self.ipc = ipc
        self.sock = None

    def _connect(self, sock=None, *args, **kwargs):
        if sock is None:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        else:
            sock = sock

        sock.connect(self.ipc)

        # Tell the socket not to block on reads.
        sock.settimeout(0)

        return sock

    def send(self, data):
        data = json.dumps(data).encode()

        self.sock = self._connect()
        self._send(data)
        return self._receive()

    def _send(self, msg):
        totalsent = 0
        while totalsent < MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                break
            totalsent = totalsent + sent

    def _receive(self):
        chunks = []
        bytes_recd = 0

        ready = select.select([self.sock], [], [], 10)

        print(ready)
        if ready[0]:
            while bytes_recd < MSGLEN:
                try:
                    chunk = self.sock.recv(min(MSGLEN - bytes_recd, 32))
                    if chunk == b'':
                        break
                except socket.timeout:
                    break

                chunks.append(chunk)
                bytes_recd = bytes_recd + len(chunk)

        data = b''.join(chunks).decode()
        try:
            return json.loads(data)
        except ValueError:
            raise BadJson(data)
