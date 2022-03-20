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
from lemondb.plugin.base import BasePlugin
import json
from lemondb.types import (
    Optional
)

class LemonPlugin(BasePlugin):
    """
    The base plugin for LemonDB. This create a standard
    JSON db.
    """

    def __init__(self, **options):
        self.options = options
        super(LemonPlugin, self).__init__(**self.options)

    def _init_db(self, version: str):
        """
        Initialize the db if not exist.
        """

        path = pathlib.Path(self.name)
        with open(path.absolute(), 'w') as f:
            json.dump({
                '__version__': version, 
                self.kwargs.get('table_name'): {}
            }, f)
        

    def run(
        self, 
        name=None, 
        document_cls=None, 
        plugin_cls=None, 
        middleware_cls=None, 
        **kwargs
    ):

        self.name = name
        self.document_cls = document_cls
        self.plugin_cls = plugin_cls
        self.middleware_cls = middleware_cls
        self.kwargs = kwargs
        
