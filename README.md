# LemonDB
> Development Status: Beta

Simple ang lightweight document oriented database written in pure `Python 3` (3.9)

## Examples
Data insertion Example:

```python
from lemondb import LemonDB
db = LemonDB('db')
db.insert({'name': 'John Doe'})
```

### Query Example

`LemonDB.Search` can accept 3 types of parameters:
- Standard `Query` class
- Regular Expression
- Lambda Functions

```python
from lemondb import LemonDB
from lemondb import Query
db = LemonDB('db')
db.insert_many([
  {'name': 'John Doe'},
  {'name': 'Elizabeth Doe'}
])

data = db.search(query.name == 'John Doe')
print(data)
# Output: John Doe

#: Using lambda
data = db.search(lambda x: x['name'] == 'John Doe')
print(data)
# Output: John Doe

#: Using regular expression
data = db.search(
  query='^J(.*?)e$' #: Match when the first string is J and endswith e
)
print(data)
# Output: John Doe
```

### Encrypted LemonDB
You can use Sidle Encryption within the LemonDB. Just use the `SidleMiddleware` and `SidlePlugin`

```python
from lemondb import LemonDB
from lemondb.middleware import SidleMiddleware
from lemondb.plugin import SidlePlugin

db = LemonDB(
  name = 'sidle_db',
  middleware_cls = SidleMiddleware(password='password123'),
  plugin_cls = SidlePlugin
)

db.insert({'name': 'John Doe'})

```
# Creating Middlewares & Plugins

By creating middleware, you need to use the base class `lemondb.middleware.base.BaseMiddleware`. The `BaseMiddleware`
class handle all operation like **read**, **write** and **delete**. While plugins handle the initializing of the
database operation and it is called whenever the `LemonDB` instance is initialized.

Just make sure to create a class based on the BaseClasses and inherit all functions, if the methods/functions are not
inherited properly, it will throw an `NotImplementedError`.

Finally,you can call your custom middleware or plugin using the `plugin_cls` and `middleware_cls` parameter for the
database. The default value is `JsonMiddleware` and `LemonPlugin`. Here is the example

```python
from lemondb import LemonDB
from middleware import CustomMiddleware
from plugin import CustomPlugin

db = LemonDB(
  name='db.json',
  middleware_cls=CustomMiddleware,
  plugin_cls=CustomPlugin
)
```
