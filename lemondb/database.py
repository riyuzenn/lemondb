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
    Linq
)
from lemondb.middleware import JsonMiddleware
from lemondb.document import Document
from lemondb.constants import ops
from lemondb.utils import iterate_dict
from lemondb.logger import logger
from lemondb.errors import SearchQueryError
import re



class LemonDB:
    """
    Note: This library is currently on a BETA / ALPHA. Not yet
    used for production since there is some bugs might occur.


    LemonDB is a simple and lightweight document oriented database 
    written in pure Python 3 tried on version: `3.9` & `3.8`. It 
    should work on versions  <= 3.7. This class handle all operation 
    including storing document on a file.

    Based on the performance, LemonDB comes first before the popular
    `TinyDB` however it is not said to be replaced the `TinyDB`.
    
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


    Note: LemonDB support table operation where you stored a data inside
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

        self.kwargs.__setitem__('table_name', self.default_table)
        self.table_name = self.kwargs.get('table_name', self.default_table)
        

        if self.table_name:
            self.default_table = self.table_name

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

        
        if not self.db_path.exists():
            self.plugin_cls._init_db()

    @logger.catch
    def table(self, name: str, **options):
        """
        The table for the database. If the given
        table name doesnt exist then create a new one.

        The table handles a sorted dictionary that contains
        the data.
        """

        data = self.document_cls.read()
        if name in list(data.keys()):
           for k in data.keys():
               if k == name:
                    db = LemonDB(self.name, table_name=name)
                    db.repr_name = 'LemonTable'
                    return db

    @logger.catch
    def tables(self):
        """
        Get all table name and return a list.
        """
        return [k for k in self.document_cls.read().keys()]


    @logger.catch
    def items(self, table_name: Optional[str] = None, **options):
        """
        Return all items from the given table, packed on a single list
        """

        return_dict = options.get('dict', False)
        data = self.document_cls.read()
        if table_name:        
            _items = [data[x] for x in data.keys() if x == table_name]
        else:
            _items = [{k:v} for k,v in data.items()]

        if return_dict:
            for k,v in data.items():
                _items = [{k:v} for k,v in v.items()]


        return _items


    @logger.catch
    def clear(self):
        """
        Clear all item from the database including the tables and
        create a new default table name.
        """

        data = self.document_cls.read()
        data.clear()
        self.plugin_cls._init_db()

    @logger.catch
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
    
    @logger.catch
    def insert_many(self, iterable: Iterable):
        """
        Simillar to `insert` however insert all items 
        from the given iterable / list. 
        """

        for i in iterable:
            self.insert(i)

    @logger.catch
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

    @logger.catch
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

        self.document_cls.write(data, mode='w')
        return True

    @logger.catch
    def search(self, query):
        """
        Search an item from the database. The query accept
        3 types. The first one is the standard `SearchQuery`,
        next is the `lambda` function and the `re` pattern.

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
        items = self.items(dict=True)
        result = []
        use_lambda = False
        use_re = False
        use_sq = False

        if isinstance(query, Lambda):
            use_lambda = True

        elif isinstance(query, SearchQuery):
            use_sq = True

        else:
            use_re = True

        
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
            lambda_wrapper = lambda x: ops[op](x[item], key)
            return _query.where(lambda_wrapper).to_list()

        if use_lambda:
            return _query.where(query).to_list()
        

        return result
        
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

    
