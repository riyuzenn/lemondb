# Copyright (c) 2021 Zenqi

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from tkinter import E
from lemondb.types import (
    Optional,
    Mapping
)
try:
    from sidle.enc import SidleEncryption
except ModuleNotFoundError:
    SidleEncryption = None

import socketserver
import json
import sys
import socket
import time

class BaseServer:
    """
    Base class for the server.
    """

    def run(self):
        raise NotImplementedError

class BaseClient:
    """
    Base class for handling client connection
    """

    def send(self, data: Mapping):
        raise NotImplementedError

class _LemonHandler(socketserver.DatagramRequestHandler):
    """
    Request Handler for LemonServer
    """
    def send_operation(self, op, data, kwargs, _data):

        if op.__name__ == 'update':
            item = _data.get('item')
            send = op(data, item)

        elif data:
            send = op(data)
        elif kwargs and data:
            send = op(data, **kwargs)
        else:
            send = op()

        return send

    def handle(self):
        db = self.server.db
        enc = self.server.enc
        logger = db.logger
        socket = self.request[1]
        try:
            _data = json.loads(enc.decrypt(self.request[0].strip()))
        except ValueError:
            _data = None
            if logger:
                logger.error('Error Parsing Data: {d}; Ignoring'.format(d=_data))
        
        if logger:
            logger.info('Received Data From : {h}'.format(h=self.client_address))        

        op = _data.get('op')
        data = _data.get('data', {})
        kwargs = _data.get('kwargs', {})
        if not hasattr(db, op):
            raise AttributeError('Operation: {} not found'.format(op))
        
        op = db.__getattribute__(op)
        try:
            send = self.send_operation(op, data, kwargs, _data)
        except Exception as e:
            send = {'error': e}

        socket.sendto(enc.encrypt(json.dumps(send)), self.client_address)


class LemonServer(BaseServer):
    """
    LemonServer is a socket server that used to store LemonDB over
    the socket connection. The database is stored on the lemondb environment
    (~/.lemondb). It can do all operation and the packets / data sent from
    the client should be encrypted using SidleEncryption. See LemonClient
    for the example client. 

    Parameters:
        
        host (str):
            The host of the server to be bind to. The host pattern should
            be 0.0.0.0:3000 where 3000 is the port and 0.0.0.0 is the host
            ofcourse.

    Example (Cannot be used directly):

        >>> server = LemonServer('0.0.0.0:3000', 'simple_password', ...)
        >>> server.run()

    """
    
    #: Initialize socket object.
    socket: socket.socket
    server_loop: bool
    
    #: Initialize Sidle encryption object.
    enc: SidleEncryption
    enc_key: str = 'lemondb.server/0.1'

    def __init__(
        self, 
        host: str, 
        db,
        **options
    ):
        """
        Parameters:
        
            host (str):
                The host of the server to be bind to. The host pattern should
                be 0.0.0.0:3000 where 3000 is the port and 0.0.0.0 is the host
                ofcourse.

            Keyword Arguments (kwargs):
            
                reuse_socket (Optional[bool]: True):
                    Allow the socket to be reused.
                
                client (Optional[int]: 1):
                    Set how many client the socket should listen to.

                buffer_value (Optional[int]: 65537):
                    The receive buffer value.

        """

        self.host = host
        self.db = db
        self.opt  = options
        if SidleEncryption:
            self.enc  = SidleEncryption(self.enc_key)
        else:
            raise RuntimeError('Sidle encryption is missing')        

        if isinstance(host, str):
            self.host = self.__parse_host(host)


    def run(self):
        start = time.time()
        reuse_addr = self.opt.pop('reuse_addr', True)

        try:
            with socketserver.UDPServer(self.host, _LemonHandler) as server:
                server.allow_reuse_address = reuse_addr
                server.db = self.db
                server.enc = self.enc
                server.serve_forever()

        except KeyboardInterrupt:
            if self.db.logger:
                self.db.logger.error('Server Killed; Total time: {:.2f}s'.format(time.time() - start))

  

    def __parse_host(self, host: str):
        lst = host.split(':')
        try:
            _host, port = lst
        except Exception:
            raise
        
        return (_host, int(port))

class LemonClient(BaseClient):
    """
    LemonClient is a client handler for the server.
    It handle the operation of sending data and connection
    via LemonServer. Also it has an encryption for the LemonServer
    which is lemondb.server/{version} 
    """

    #: Initialize Socket object
    _socket: socket.socket

    #: Initialize Sidle encryption object.
    enc: SidleEncryption
    enc_key: str = 'lemondb.server/0.1'

    def __init__(
        self, 
        host: str, 
        **option
    ):

        self.host = host
        self.opt  = option

        if isinstance(host, str):
            self.host = self.__parse_host(host)

        if SidleEncryption:
            self.enc  = SidleEncryption(self.enc_key)
        else:
            raise RuntimeError('Sidle encryption is missing')        

        self.__initialize_socket()
        

    def send(self, data: dict, buffer: int=1024):
        """
        Send raw data given the operation to the
        socket server.
        """
        
        data = self.enc.encrypt(json.dumps(data))
        self._socket.sendto(data, self.host)
        recv = self._socket.recv(buffer)
    
        return json.loads(self.enc.decrypt(recv))



    def __initialize_socket(self):
        """
        Initialize socket object
        """
        self._socket = socket.socket(
            family=socket.AF_INET, 
            type=socket.SOCK_DGRAM
        )
        return self._socket

    def __parse_host(self, host: str):
        lst = host.split(':')
        try:
            _host, port = lst
        except Exception:
            raise
        
        return (_host, int(port))

    
