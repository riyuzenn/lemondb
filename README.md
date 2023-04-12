<div align="center">
  <h1>LemonDB</h1>
</div>

<div align="">
<table>
<tbody>
<td align="center">
:warning: messy code that leads to broken API ― i dont really know how i built this. who use this module, anyway?
</td>
</tbody>
</table>
</div>

### Reason why you should not use this for production or anything

- Broken API
- Uses worse searching algorithm that leads to slow operation when handling massive data
- Unfinished project


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

- ~~Different `types` are now supported!~~
- ~~Searching / filtering were improved.~~

```py
from lemondb import LemonDB
from datetime import datetime

# Adding datetime object
db = LemonDB('test.json')
db.insert({'name': 'John Doe', 'elapsed-time': datetime.now()})

# Searching now accept dict queries
db.find_one({'name': 'John Doe'})
```
