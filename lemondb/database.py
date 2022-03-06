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

import os
from lemondb.plugin import (
    BasePlugin,
    LemonPlugin
)
import pathlib
from lemondb.types import (
    Optional,
    Middleware,
    Any,
    Dict,
    Lambda,
    Iterable,
    Mapping
)
from lemondb.query import (
    SearchQuery,
    Linq,
    LemonCursor
)
from lemondb.server import (
    LemonServer,
    LemonClient
)
import socket
from urllib.parse import urlparse
from lemondb.middleware import JsonMiddleware
from lemondb.document import Document
from lemondb.constants import ops
from lemondb.utils import iterate_dict
from lemondb.logger import logger
from lemondb.errors import SearchQueryError
import re

def catch_exceptions(decorator=None):
    condition = True if logger else False
    if not decorator:
        decorator = logger.catch if logger else None

    def deco(func):
        if not condition:
            return func
        return decorator(func)
        
    return deco


class LemonDB:
    """
    NOTE: This library is currently on a BETA / ALPHA. Not yet
    used for production since there is some bugs might occur.
    
    Release Changes: v.0.0.3:
        The new release v.0.0.3 has added new features. The new
        Socket Server & Client feature so that you can run the
        database on a VPS or any hosting server. 

    NOTE: For Server & Client used. Kindly pass keyword argument
    host_checking to automatically detect if it is client or
    server or manually pass keyword arguments if the given name
    is client or server to avoid slow performance. 

    LemonDB is a simple and lightweight document oriented database 
    written in pure Python 3 tried on version: `3.9` & `3.8`. It 
    should work on versions  <= 3.7. This class handle all operation 
    including storing document on a file.

    For Server & Client, make sure to use the lemondb:// as the scheme
    for the server. This recognized and parsed the host, port and the
    keyword argument given by the query string. 

    Based on performance, LemonDB comes in first place ahead of the 
    popular `TinyDB`, but it is not expected to replace `TinyDB`.
    

    Here are the result for the database operation that store 
    1000 random generated strings.

    LemonDB: 20.848030 / 20.85 seconds
    TinyDB: 53.912508 / 53.91 seconds

    It is actually 2x faster than the TinyDB. It can be a little bit
    faster since LemonDB support different type of JSON Serialization
    that is faster than the standard `json` library. It supports:
    
    - `simplejson (Estimated result for 1000 insert operation: 27.86 sec)`
    - `ujson (Estimated result for 1000 insert operation: 22.88 sec)`
    - `hyperjson (Estimated result for 1000 insert operation: 20.18 sec)`


    NOTE: LemonDB support table operation where you stored a data inside
    a table. You can create / get the table by calling the `table` method:
        
        >>> from lemondb import LemonDB
        >>> db = LemonDB('lemon.json')
        >>> names = db.table('name') #: Create / Get the table .
        >>> names.insert({'name': 'John Doe'})
        >>> {'name': 'John Doe'}

    Last but not the least, LemonDB support a database encryption with 
    password also known as Sidle Encryption (https://github.com/znqi/sidle). 
    By default LemonDB allows you to install the `sidle` library in order 
    to do the operation. You can access it by using the standard middleware:
    `lemondb.middleware.SidleMiddleware` that accept a positional arguments
    `password`. Also, make sure to include the `lemon.plugin.SidlePlugin`.

        >>> from lemondb import LemonDB
        >>> from lemondb.plugin impor SidlePlugin
        >>> from lemondb.middleware import SidleMiddleware
        >>> ...
        >>> db = (
        >>>     'test.json',
        >>>     middleware_cls=SidleMiddleware('password'),
        >>>     plugin_cls=SidlePlugin
        >>> ...

    Parameters:

        :param name (str):
            The name of the database. It can be a file name.

        :param plugin_cls (BasePlugin : Optional):
            The base plugin for Lemon DB. The plugin runs
            everytime the database is called or initialized.
            Default value: LemonPlugin

        :param middleware_cls (BaseMiddleware : Optional):
            The middleware for the document that handles read,
            write and delete operation on the file given.
            Default Value: JsonMiddleware


        :param document_cls (Document):
            Set the document class for creating documents.
            Default Value: Document

    Server Example:
        >>> from lemondb import LemonDB
        >>> db = LemonDB('lemondb://0.0.0.0:3000', server=True)

    Client Example:
        >>> from lemondb import LemonDB
        >>> db = LemonDB('lemondb://localhost:3000', client=True)
        >>> db.insert({'name': 'John Doe'})

    Example:

        >>> from lemondb import LemonDB
        >>> db = LemonDB('test.json')
        >>> db.insert({
        >>>         'name': 'John Doe'
        >>>     })
        >>> {'name': 'John Doe'}
        >>> ...
        >>> #: For query searching
        >>> from lemondb import Query
        >>> query = Query()
        >>> db.search(query.name == 'John Doe')
        >>> [{'name': 'John Doe'}]

    
    """

    #: The path for the database.
    db_path: pathlib.Path

    #: The default table for the database
    default_table: str = "_table"

    #: LemonCLient Instance
    #: versionAdded: 0.0.3
    client_instance: LemonClient = None

    #: LemonServer Instance
    #: versionAdded: 0.0.3
    server_instance: LemonClient = None


    def __init__(
        self,
        name: str,
        plugin_cls: Optional[BasePlugin] = None,
        middleware_cls: Optional[Middleware] = None,
        document_cls: Optional[Document] = None,
        **kwargs
    ):

        """
        Initialize Lemon DB

        Parameters:

            :param name (str):
                The name of the database. It can be a file name.

            :param plugin_cls (BasePlugin : Optional):
                The base plugin for Lemon DB. The plugin runs
                everytime the database is called or initialized.
                Default value: LemonPlugin

            :param middleware_cls (BaseMiddleware : Optional):
                The middleware for the document that handles read,
                write and delete operation on the file given.
                Default Value: JsonMiddleware


            :param document_cls (Document):
                Set the document class for creating documents.
                Default Value: Document

        Example:

            >>> from lemondb import LemonDB
            >>> db = LemonDB('test.json')
            >>> db.insert({'name': 'John Doe'})

        """

        self.name = name
        self.kwargs = kwargs
        self.db_path = pathlib.Path(self.name)
        self.repr_name = type(self).__name__
        self.plugin_cls = plugin_cls

        self.server = self.kwargs.get('server', False)
        self.client = self.kwargs.get('client', False)

        if logger and self.kwargs.get('debug', False):
            #: added -> v0.0.4
            self.set_logger()

        if not plugin_cls:
            self.plugin_cls = LemonPlugin()
        else:
            self.plugin_cls = plugin_cls

        if not middleware_cls:
            self.middleware_cls = JsonMiddleware()
        else:
            self.middleware_cls = middleware_cls

        if not document_cls:
            self.document_cls = Document(
                path=self.db_path, 
                middleware_cls=self.middleware_cls
            )
        else:
            self.document_cls = document_cls

        
        if not 'table_name' in self.kwargs:
            self.kwargs.__setitem__('table_name', self.default_table)
        
        self.table_name = self.kwargs.get('table_name', self.default_table)
    

        if self.table_name:
            self.default_table = self.table_name

        if self.kwargs.get('host_checking', False):
            if self.__check_if_server_client():
                self.client = True
            elif self.__check_if_server_client == 0:
                self.server = True
        
        if self.server:
            parsed = self.__parse_url(self.name)
            db_dir = pathlib.Path().home() / '.lemondb' / 'db'
            if not db_dir.exists():
                os.mkdir(db_dir.absolute())
            
            self.name = str(
                (db_dir / 'db' ).absolute()
            )
            self.document_cls = Document(
                path=(db_dir / 'db' ).absolute(),
                middleware_cls=self.middleware_cls
            )

            self.run_plugin(plugin_cls=plugin_cls)
            self.plugin_cls._init_db()

            self.server_instance = LemonServer(
                host=(parsed['host'], parsed['port'])
            )
            self.server_instance.run(self)
        
        elif self.client:
            parsed = self.__parse_url(self.name)
            self.client_instance = LemonClient(
                host=(parsed['host'], parsed['port'])
            )

        self.run_plugin(plugin_cls=plugin_cls)

        
        if not self.db_path.exists():
            self.plugin_cls._init_db()

        if self.server:
            self.repr_name = 'LemonServer'
        elif self.client:
            self.repr_name = 'LemonClient'

        

    @catch_exceptions()
    def table(self, name: str, **options):
        """
        The table for the database. If the given
        table name doesnt exist then create a new one.

        The table handles a sorted dictionary that contains
        the data.
        """

        options.__setitem__('table_name', name)
        
        return LemonDB(
            name=name, 
            plugin_cls=self.plugin_cls,
            middleware_cls=self.middleware_cls, 
            document_cls=self.document_cls,
            **options
        )

    @catch_exceptions()
    def tables(self):
        """
        Get all table name and return a list.
        """
        return [k for k in self.document_cls.read().keys()]


    @catch_exceptions()
    def items(self, table_name: Optional[str] = None, **options):
        """
        Return all items from the given table, packed on a single list
        """

        return_dict = options.get('dict', False)
        item = options.get('item', False)
        data = self.document_cls.read()
        
        if item:
            l = []
            for k,v in data.items():
                for i,v in v.items():
                    l.append(v)
            return l

        if table_name:        
            _items = [data[x] for x in data.keys() if x == table_name]
        else:
            _items = [{k:v} for k,v in data.items()]

        if return_dict:
            for k,v in data.items():
                _items = [{k:v} for k,v in v.items()]


        return _items


    @catch_exceptions()
    def clear(self):
        """
        Clear all item from the database including the tables and
        create a new default table name.
        """

        data = self.document_cls.read()
        data.clear()
        self.plugin_cls._init_db()

    @catch_exceptions()
    def insert(self, item: Mapping, **options):
        """
        Insert a item to the database. The item should
        be a mapping `(dict)`.
        
        Parameter:
            :param item (Mapping):
                The item to be added to the database.

        Example:
            >>> from lemondb import LemonDB
            >>> db = LemonDB('test')
            >>> db.insert({'name': 'zenqi'})

        Retun:
            The item to be inserted.

        """
        #: If the data is set, then convert it to list.
        if isinstance(item, set):
            item = list(item)
        
        if self.client_instance:
            self.client_instance.send(
                op='insert',
                data=item
            )
            return item
            
        
        raw_data = self.document_cls.read()
        raw = False
        if not self.db_path.exists():
            self.plugin_cls._init_db()
        
        table = options.pop('table', self.default_table)
        if table:
            _r_d = {}

            if table in raw_data.keys():
                for k,v in raw_data.items():
                    if k == table:
                        _r_d = {k:v}
                    
            else:
                _r_d = {table: {}}
            
            raw = True
            if table == self.default_table:

                item = self.document_cls._increment(
                    data=_r_d, item=item)


            else:
                item = self.__construct_table(
                    table=table, 
                    data=_r_d,
                    raw=item
                )
            
        self.document_cls.write(item, raw=raw)
        return item
    
    @catch_exceptions()
    def insert_many(self, iterable: Iterable):
        """
        Simillar to `insert` however insert all items 
        from the given iterable / list. 
        """
        
        for i in iterable:
            if self.client_instance:
                self.client_instance.send(
                    op='insert_many',
                    data=i
                )
            else: self.insert(i)

        return iterable

    @catch_exceptions()
    def delete(
        self, 
        query: Any, 
        all: Optional[bool] = True
    ):
        
        """
        Delete a key from a query given. The query accept
        3 types. Similar to `search`. 

        Parameter:
            query (Any):
                The query of the key to delete.

            all (Optional[Boolean]):
                (added on v0.0.2)

                Set if all existing keys/simillar value
                to be deleted. Default Value: `True`

        Examples:
            >>> query = Query()
            >>> db.delete(query.name == 'John Doe')
            >>> ...

        Return:
            The deleted item.

        """
        if self.client_instance:
            self.client_instance.send(
                op='delete',
                data=query
            )
        
        if isinstance(query, Mapping):
            self.document_cls.delete(query, all=True)
            return query

        else:
            try:
                if all:
                    data = self.search(query)
                else:
                    data = self.search(query)[0]
            
            except IndexError:
                # TODO: No result found on a search.
                return None

            self.document_cls.delete(data, all=True)
            return data

    @catch_exceptions()
    def update(self, query: Any, item: Mapping):
        """
        ADDED: `v0.0.2`
        
        Update the data from the default given table name.
        This perform a `search` query that can be 3 types,
        and update the first result of the query.

        Parameters:
            query (Any):
                The query syntax for searching item

            item (Mapping):
                The item to be replace

        Example:

            >>> from lemondb import LemonDB, Query
            >>> db = LemonDB('test.json')
            >>> query = Query()
            >>> ...
            >>> db.insert({'name': 'John Doe', 'password': '1234'})
            >>> ...
            >>> db.update(
            >>>     query.name == 'John Doe', 
            >>>     {'password': 'newpassword'}
            >>> )
            >>> ...

        """

        _ = self.search(query)
        
        if not _:
            #: TODO: Searching failed. No result found
            raise SearchQueryError('The search query doesnt exist on the table/database')

        result = _[0]
        data = self.document_cls.read()
        for table, value in list(data.items()):
            for k,v in list(value.items()):
                if v == result:
                    data[table][k].update(item)
                    break

        self.document_cls.write(data, mode='w', raw=True)
        return item

    @catch_exceptions()
    def search(self, query=None, **options):
        """
        Search an item from the database. The query accept
        4 types. The first one is the standard `SearchQuery`,
        next is the `lambda` function, dict query and the `re` pattern.

        Parameter:
            query (Any):
                The query of the key to search.
    

        Example:
            >>> from lemondb import LemonDB, Query
            >>> db = LemonDB('test.json')
            >>> db.insert({'name': 'John Doe'})
            >>> ...
            >>> query = Query()
            >>> db.search(query.name == 'John Doe')
            >>> [{"name": "John Doe"}]
        
        Return:
            The list of possible result for the queries.

        """
        rate = options.pop('rate', None)
        
        if self.client_instance:
            self.client_instance.send(
                op='search',
                data=query
            )

        items = self.items(dict=True)
        result = []
        use_lambda = False
        use_re = False
        use_sq = False

        if isinstance(query, Lambda):
            use_lambda = True

        elif isinstance(query, SearchQuery):
            use_sq = True
        
        elif isinstance(query, dict):
            use_dict = True

        elif query != None:
            use_re = True

        if not query:
            c = LemonCursor(self.items(item=True))
            if rate and rate <= 1:
                c = c.all()[:rate][0]
            elif rate:
                c = c.all[:rate]

            return c

        if use_dict:
            query = list(query.items())
            c = LemonCursor([])
            for i in self.items(item=True):
                item = list(i.items())
                #: Convert the list of items into set and check for same key, value
                if set(query).intersection(item):
                    c.add_query_result(i)    

            return c


        reconstructed_list = []
        
        for i in items:
            for k,v in i.items():

                if use_re:
                    for _, rv in iterate_dict(v):
                        if re.search(query, str(rv), re.IGNORECASE):
                            result.append(v)
                            
                else:
                    reconstructed_list.append(v)
        
        
        _query = Linq(reconstructed_list)
        if use_sq:
            
            op, key, item = query()
            def wrapper(i):
                if isinstance(key, str):
                    _key = key.lower()
                    m = re.search(_key, i[item], re.IGNORECASE)
                    if m:
                        return ops[op](i[item], m.group())
                    else: 
                        #: If there is no match, then just ignore.
                        return ops[op](i[item], key)

                return ops[op](i[item], key)

            c = LemonCursor(_query.where(wrapper).to_list())
            if rate and rate <= 1:
                c = c.all()[:rate][0]
            elif rate:
                c = c.all[:rate]
            
            return c
        
        if use_lambda:
            c = LemonCursor(_query.where(query).to_list())
            if rate and rate <= 1:
                c = c.all()[:rate][0]
            elif rate:
                c = c.all[:rate]

            return c

        c = LemonCursor(result)
        if rate and rate <= 1:
            c = c.all()[:rate][0]
        elif rate:
            c = c.all[:rate]

        return c

    @catch_exceptions()
    def find_one(self, query=None):
        """
        Fetch the query and return the first appearance from the
        database. 

        Example:
            >>> db.find_one({'name': 'John Doe'})
            >>> {'name': 'John Doe', 'user_id': 19123713123}

        """
        return self.search(query, rate=1)

    @catch_exceptions()
    def find(self, query=None, **options):
        return self.search(query, **options)


    def __len__(self):
        data = self.document_cls.read()
        return len(data[self.default_table])


    def __repr__(self) -> str:
        return "{name}(table_name=\"{table}\", length={length}, table_count={table_count})".format(
            name=self.repr_name,
            table=self.default_table,
            length=len(self),
            table_count=len(self.tables()),
        )

    def __construct_table(
        self, 
        table: str, 
        data: Mapping, 
        raw: Optional[Mapping] = {},
    ):

        """
        Create a table for the given data
        """

        if not raw:
            _ = {table: {}}
        elif raw and data:
            _ = self.document_cls._increment(data, raw)
        else:
            _ = self.document_cls._increment({table: {}}, raw)

        data.update(_); return data

    
    def __check_if_server_client(self):
        """
        Check if the db name is server or client
        """

        # Match if the given db name is a server pattern
        pattern = re.compile(
            r'^(?:lemondb|http)s?://' # lemondb:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )

        m = re.match(pattern, self.name)
        
        if m:
            #: Try if it is client or server
            parsed = self.__parse_url(self.name)
            try:
                sock = socket.socket()
                sock.connect((parsed['host'], parsed['port']))
                return 1 #: 1 means client

            except socket.error:
                return 0 #: 0 means server
            

        return None

    def __parse_url(self, url: str):
        """
        Parse the url and return a dictionary.
        Version Added: 0.0.3
        """

        parsed = urlparse(url)
        return {
            'scheme': parsed.scheme,
            'host': parsed.hostname,
            'port': parsed.port,
            'query': parsed.query,
        }

    def run_plugin(self, plugin_cls: Any):
        """
        Seperate function to run plugin.
        Version Added: 0.0.3
        """

        try:
            #: Run the plugin and give all parameters
            self.plugin_cls.run(
                name=self.name,
                document_cls=self.document_cls,
                plugin_cls=self.plugin_cls,
                middleware_cls=self.middleware_cls,
                **self.kwargs
            )
        except TypeError:
            self.plugin_cls = plugin_cls()
            self.plugin_cls.run(
                name=self.name,
                document_cls=self.document_cls,
                plugin_cls=self.plugin_cls,
                middleware_cls=self.middleware_cls,
                **self.kwargs
            )

    def set_logger(self):
        self.logger = logger


    find.__doc__ = search.__doc__