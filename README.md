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

