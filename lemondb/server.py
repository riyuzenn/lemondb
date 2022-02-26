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


from lemondb.types import (
    Optional,
    Mapping
)
try:
    from sidle.enc import SidleEncryption
except ModuleNotFoundError:
    SidleEncryption = None

import socket
import json
import sys

class BaseServer:
    """
    Base class for the server.
    """

    def create(self):
        """Base Server for creating server. Notimplemented"""
        raise NotImplementedError
        
    def run(self):
        """Run the server given the host."""
        raise NotImplementedError

class BaseClient:
    """
    Base class for handling client connection
    """
    
    def connect(self):
        raise NotImplementedError

    def send(self, data: Mapping):
        raise NotImplementedError
        

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

        key (Optional[str]):
            The password key for the server. Optional. Set it to None if 
            you don't want to add password key.

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
        key: Optional[str] = None, 
        **options
    ):
        """
        Parameters:
        
            host (str):
                The host of the server to be bind to. The host pattern should
                be 0.0.0.0:3000 where 3000 is the port and 0.0.0.0 is the host
                ofcourse.

            key (Optional[str]):
                The password key for the server. Optional. Set it to None if 
                you don't want to add password key.

            Keyword Arguments (kwargs):
            
                reuse_socket (Optional[bool]: True):
                    Allow the socket to be reused.
                
                client (Optional[int]: 1):
                    Set how many client the socket should listen to.

                buffer_value (Optional[int]: 65537):
                    The receive buffer value.

        """

        self.host = host
        self.key  = key
        self.opt  = options
        if SidleEncryption:
            self.enc  = SidleEncryption(self.enc_key)
        else:
            self.enc = None
            
        self.buff = self.opt.get('buffer_value', 65537)

        if isinstance(host, str):
            self.host = self.__parse_host(host)


    def create(self) -> socket.socket:
        """
        Create the socket server given the host and configuration.
        """
        #: Get all kwargs option 
        client = self.opt.get('client', 1)
        reuse_socket = self.opt.get('reuse_socket', True)

        self.socket = socket.socket(
            family=socket.AF_INET, 
            type=socket.SOCK_STREAM
        )
        if reuse_socket:
            
            self.socket.setsockopt(
                socket.SOL_SOCKET, 
                socket.SO_REUSEADDR, 
                1
            )
        
        self.socket.bind(self.host)
        self.socket.listen(client)
        self.server_loop = True

        return self.socket

    def run(self, dbclass):
        server = self.create()
        try:
            while self.server_loop:
                self._handle_request(server, dbclass)

        except KeyboardInterrupt:
            sys.exit()

    def _handle_request(self, server: socket.socket, dbclass):
        """
        Handle all request sent to the server.
        """
        connection, address = server.accept()
        raw_data = connection.recv(self.buff)
        
        #: The sent data should be json formatted.
        if raw_data:
            decrypted = json.loads(
                self.enc.decrypt(raw_data)
            )

            op = decrypted.get('op', None)
            data = decrypted.get('data', None)
        
        try:
            operation = dbclass.__getattribute__(op)
            operation(data)
        except AttributeError:
            dbclass.logger.error('"%s" is not an operation' % (op))


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
        key: Optional[str] = None,
        **option
    ):

        self.host = host
        self.key  = key
        self.opt  = option

        if isinstance(host, str):
            self.host = self.__parse_host(host)

        if option.get('auto_connect', True):
            self.connect()


    def connect(self):
        """
        Create a connection between the socket server that
        handles data and inorder to send data.
        """

        self.__initialize_socket()
        try:
            self._socket.connect(self.host)
        except Exception:
            return False


        return True
        

    def send(self, op: str, data: Mapping):
        """
        Send raw data given the operation to the
        socket server.
        """

        all_op = ['insert', 'update', 'delete', 'search']
        if op not in all_op:
            raise TypeError('%s is not an operation' % (op))

        raw = json.dumps({
            'op': op,
            'data': data
        })

        self._socket.send(
            self.enc.encrypt(raw)
        )

        return raw


    def __initialize_socket(self):
        """
        Initialize socket object
        """
        self._socket = socket.socket(
            family=socket.AF_INET, 
            type=socket.SOCK_STREAM
        )
        return self._socket

    def __parse_host(self, host: str):
        lst = host.split(':')
        try:
            _host, port = lst
        except Exception:
            raise
        
        return (_host, int(port))

    
