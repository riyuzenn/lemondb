<div align="center">
  <h1>LemonDB</h1>
</div>

<div align="">
<table>
<tbody>
<td align="center">
:warning: messy code tha leads to broken API. who use this module, anyway?
</td>
</tbody>
</table>
</div>

LemonDB is a simple and lightweight document oriented database written in pure Python 3 tried on version: `3.9` & `3.8`. It should work on versions <= 3.7. This class handle all operation including storing document on a file.

Example:
```python
from lemondb import LemonDB
db = LemonDB('test.db')
db.insert_many([{'name': 'zenn'}, {'name': 'John Doe'}, {'name': 'Elizabeth Doe'}])

# Search from database using `find` or `search`
for i in db.find('Doe').where(lambda x: x['name'].startswith('John')):
  print(i)
  #: {'name': 'John Doe'}
  
#: You can use the query or dict
from lemondb import Query
query = Query()
print(db.find_one(query.name == 'zenn')))
#: {'name': 'zenn'}

print(db.find_one({'name': 'zenn'}))
#: {'name': 'zenn'}

```

## 📌 New Features in 1.x Series!

- Different `types` are now supported!  
- Searching / filtering were improved.

Have you ever wanted to serialize a datetime object? and other type object that standard JSON could'nt serialized?
Well lemondb now support those. Search & filtering were improved. LemonDB now using cursors. Don't believe me? Try this out

```py
from lemondb import LemonDB
from datetime import datetime

# Adding datetime object
db = LemonDB('test.json')
db.insert({'name': 'John Doe', 'elapsed-time': datetime.now()})

# Searching now accept dict queries
db.find_one({'name': 'John Doe'})
```
