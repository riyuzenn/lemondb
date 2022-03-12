<div align="center">
  <h1>LemonDB</h1>
</div>

LemonDB is a simple and lightweight document oriented database written in pure Python 3 tried on version: `3.9` & `3.8`. It should work on versions <= 3.7. This class handle all operation including storing document on a file.

Example:
```python
from lemondb import LemonDB
db = LemonDB('test.db')
db.insert_many([{'name': 'Zenqi'}, {'name': 'John Doe'}, {'name': 'Elizabeth Doe'}])

# Search from database using `find` or `search`
for i in db.find('Doe').where(lambda x: x['name'].startswith('John')):
  print(i)
  #: {'name': 'John Doe'}
  
#: You can use the query or dict
from lemondb import Query
query = Query()
print(db.find_one(query.name == 'Zenqi')))
#: {'name': 'Zenqi'}

print(db.find_one({'name': 'Zenqi'}))
#: {'name': 'Zenqi'}

```
