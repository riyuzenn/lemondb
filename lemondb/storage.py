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
    Any,
    Mapping,
)
from lemondb.middleware import (
    JsonMiddleware,
    BaseMiddleware as Middleware
)
from lemondb.utils import untypenize

def _increment_id(table: dict):
    if not table:
        return 0
        
    return int(max(list(table.keys()))) + 1

class Document(dict):
    """
    A Document class that handle document from the databse.
    Document act as list however it is in form of dictionary.
    """

    def __init__(self, value: Any, id: int=None):
        self.value = value
        self._id = id
        super().__init__(self.value)

    def __getitem__(self, __k) -> dict:
        return super().__getitem__(__k)

    def __getattr__(self, __k):
        return self.__getitem__(__k)

    @property
    def id(self):
        return self._id

    def to_dict(self):
        return self.value

class Storage:
    """
    Base class for all storage.
    """

    def read(self):
        raise NotImplementedError
    
    def write(self, data):
        raise NotImplementedError

    def delete(self, data):
        raise NotImplementedError

class LemonStorage(Storage):
    """
    A storage class used for handling file operations
    such as writting, reading and deleting item.
    """

    def __init__(
        self,
        path: str,
        middleware_cls: Middleware = JsonMiddleware #: The middleware for the document. 
        # Default: JsonMiddleware

    ):

        self.path = path
        try:
            self.middleware = middleware_cls()
        except TypeError:
            # TODO: Middleware class already initialized.
            self.middleware = middleware_cls
    

    def read(self, _untypenize: bool=True) -> dict:
        data = self.middleware.read(path=self.path)
        if _untypenize:
            for k,v in data.items():
                if not isinstance(v, list) \
                    and isinstance(v, dict):
                    #: Ignore the version
                    for _k,_v in v.items():
                        d = untypenize(_v)
                        data.update({k:v})

        return data


    def write(
        self, 
        item: Mapping, 
        table_name: str,
        mode: Optional[str] = 'r+',
        raw: bool=False
    ):
        """
        Write the item to the document
        """
        if raw:
            return self.middleware.write(item, path=self.path, mode=mode)

        data = self.read(False)
        table = data.get(table_name, None)
        
        if table == None:
            data[table_name] = item
        else:
            table.update(item)

        return self.middleware.write(data, path=self.path, mode=mode)


    def delete(self, item: Mapping, all: Optional[bool] = True):
        return self.middleware.delete(item, path=self.path, all=all)
    
    def _increment(self, table: dict, item: Mapping, raw=False) -> Mapping:
        """
        Increment the given item to the last given data.
        """
        if raw:
            _ = list(table.keys())[0]
            table = table[_]

        if isinstance(item, Document):
            document_id = item.id
        else:
            document_id = _increment_id(table)
            
        table.update({document_id: item})
        return table
