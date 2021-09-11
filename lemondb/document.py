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
    Middleware,
    List,
    Dict
)
from lemondb.middleware import JsonMiddleware


class Document:
    """
    A document class used for handling file operations
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
    
    def __getattr__(self, item: str):
        return self.__getitem__(
            key=item
        )

    def __getitem__(
        self, 
        key: str, 
        default: Optional[Any] = None
    ):

        pass

    def read(self) -> dict:
        return self.middleware.read(path=self.path)

    def write(
        self, 
        item: Mapping, 
        raw: Optional[bool] = False
    ):
        """
        Write the item to the document
        """

        data = self.read()
        if not raw:
            item = self._increment(
                data=data,
                item=item
            )
        else:
            item = item

        
        return self.middleware.write(item, path=self.path)


    def delete(self, item: Mapping, all: Optional[bool] = True):
        return self.middleware.delete(item, path=self.path, all=all)
    
    def _increment(self, data: Mapping, item: Mapping) -> Mapping:
        """
        Increment the given item to the last given data.
        """

        raw = []
        for k, v in data.items():
            if v:
                raw = list(v.items())
            else:
                v.update({'0': item}); return data


        k,v = raw[-1]
        i = {int(k) + 1: item}
        for k,v in data.items(): v.update(i)

        return data
