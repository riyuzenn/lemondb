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

import importlib
from lemondb.serializer.base import BaseSerializer
from lemondb.types import Optional


class JSONSerializer(BaseSerializer):
    """
    A simple JSON Serializer class for handling 
    dump and loading json from different JSON serializer
    like `simplejson`, `rapidjson`, `ujson` without changing
    the standard json format.

    Available serializer:
        `json`
        `simplejson`
        `ujson`
        `hyperjson`
        `rapidjson`
    
    Example:
        >>> from lemondb.serializer import Serializer
        >>> json = Serializer(name='json') #: standard json serializer
        >>> json.dumps(...)
        >>> ...
        >>> simplejson = Serializer(name='simplejson')
        >>> simplejson.dumps(...)
        >>> ...
    
    """

    _available_serializer = [
        'json', 'ujson', 'simplejson', 'rapidjson',
        'hyperjson'
    ]

    def __init__(self, name: Optional[str] = 'json'):
        """
        Initialize JSON Serializer
        """

        if name not in self._available_serializer:
            raise ValueError('"%s" is not found' % (name))

        try:
            self.serializer = importlib.import_module(name)
        except ImportError:
            self.serializer = importlib.import_module('json')

    def dump(self, *args, **kwargs):
        """
        Dump the JSON Object onto a File IO
        """
        return self.serializer.dump(*args, **kwargs)

    def dumps(self, *args, **kwargs):
        """
        Dump the JSON Object to a string
        """
        return self.serializer.dumps(*args, **kwargs)

    def load(self, *args, **kwargs):
        """
        Load the JSON Object from the File IO given
        """
        return self.serializer.load(*args, **kwargs)

    def loads(self, *args, **kwargs):
        """
        Load the JSON Object from the string given
        """
        return self.serializer.loads(*args, **kwargs)

