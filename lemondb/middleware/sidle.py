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

try:
    from sidle.enc import SidleEncryption
    import sidle.errors as error
except ModuleNotFoundError:
    SidleEncryption = None


from lemondb.middleware import BaseMiddleware
from lemondb.types import (
    Optional,
    Mapping,
    Dict,
    Any
)
import pathlib
from lemondb.serializer import JSONSerializer

class SidleMiddleware(BaseMiddleware):
    """
    A encryption middleware for `SidleEncryption`.
    That can encrypted with password
    """

    serializer: SidleEncryption
    def __init__(self, password: str, jsonserializer: Optional[str] = 'json'):
        """
        Initialize SidleMiddleware.

        Parameter:
            password (str):
                The password key for the database.
        """

        if not SidleEncryption:
            raise ModuleNotFoundError('Sidle is not installed. `pip install sidle` might solved this')

        self.password = password
        self.serializer = SidleEncryption(self.password)
        self.json = JSONSerializer(jsonserializer)

    def read(self, path: str) -> Dict[str, Any]:
        if isinstance(path, pathlib.Path):
            path = path.absolute()
        else:
            path = path


        with open(path, 'rb') as f:
            raw = self.serializer.decrypt(
                f.read()
            )
            if not raw:
                raise error.PasswordError("\"%s\" is not a valid password" % (self.password))

            if isinstance(raw, bytes):
                raw = raw.decode()
            else:
                raw = str(raw)
                
            data = self.json.loads(
                s=raw
            )
        
        return data

    def write(
        self, 
        item: Mapping, 
        path: str, 
        mode: Optional[str] = 'rb+'
    ):
        
        """
        Write the given item with encryption
        """
        if mode == 'w':
            mode = 'wb'
        elif mode == 'w+':
            mode == 'wb+'
            
        if isinstance(item, dict):
            item = self.json.dumps(item)
        else:
            item = item

        item = self.serializer.encrypt(item)

        if isinstance(path, pathlib.Path):
            path = path.absolute()
        else:
            path = path
            
        with open(path, mode) as f:
            f.write(item)

    def delete(
        self, 
        key: str, 
        path: str, 
        all: Optional[bool]
    ):
        """
        Delete the given key and write to the given
        file path
        """

        data = self.read(path)
        
        #: TODO: Kindly remember that we convert
        #: the data.items into a list to avoid
        #: RuntimeError: changed sized during iteration
        #: This happens because it return a iterator
        #: instead of a list.

        for table, value in list(data.items()):
            for k,v in list(value.items()):
                if isinstance(key, (tuple, list)):
                    if v in key:
                        del data[table][k]
                        
                    

                if key == v and all:
                    del data[table][k]
                    
                elif key == v and not all:
                    del data[table][k]
                    break
        
        
        self.write(data, path, mode='wb')   