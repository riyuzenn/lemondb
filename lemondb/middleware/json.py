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


import pathlib
from lemondb.middleware.base import BaseMiddleware
from lemondb.serializer import JSONSerializer
from lemondb.types import (
    Optional,
    Mapping,
    Dict,
    Any
)
from lemondb.utils import iterate_dict

class JsonMiddleware(BaseMiddleware):
    """
    A main class for handling JSON data inorder to read
    and write and delete item.
    """
    
    serializer: JSONSerializer

    def __init__(self, serializer: Optional[str] = 'json'):
        self.serializer = JSONSerializer(serializer)
        super().__init__()
        
    def read(self, path: str) -> Dict[str, Any]:
        """
        Read the file and return the data

        Parameter:
            path (str):
                The path for the file to be red. It can 
                be pathlib.Path instance or a str.
        """

        if isinstance(path, pathlib.Path):
            path = path.absolute()
        else:
            path = path

        with open(path, 'r+') as f:
            return self.serializer.load(f)

    def write(
        self, 
        item: Mapping, 
        path: str, 
        mode: Optional[str] = 'r+'
    ):
        
        """
        Write the given data to the file
        """
        if isinstance(path, pathlib.Path):
            path = path.absolute()
        else:
            path = path

        if not path.exists():
            raise FileNotFoundError('"%s" not found' % (path.absolute()))

        data = self.read(path); data.update(item)
        with open(path, mode) as f:
            self.serializer.dump(data, f)

            
    def delete(
        self, 
        key: Mapping, 
        path: str, 
        all: Optional[bool] = True
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
        
        
        self.write(data, path, mode='w')