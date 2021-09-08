# LemonDB
> Development Status: Beta

Simple ang lightweight document oriented database

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
