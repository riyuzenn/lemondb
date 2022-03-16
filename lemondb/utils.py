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


from lemondb.types import (
    Mapping,
    datetime,
    type_mapping
)


def _typenize(data: dict):
    l = []
    _l = []
    for k,v in data.items():
        if isinstance(v, dict):
            _d, _l = _typenize(v)
        
        _type = type_mapping.get(type(v), None)
        
        if _type:
            l.append(_type)
        elif _l:
            l.append(_l)

        if isinstance(v, bytes):
            v = v.decode()
        elif isinstance(v, datetime):
            v = v.isoformat()

        data.update({k:v})
        
    return data, l

def typenize(data: dict):
    d, t = _typenize(data)
    if t:
        data.update({'$type': t})
    else:
        data.update({'$type': []})    
    return data

def untypenize(data):
    t = dict((v,k) for k,v in type_mapping.items())
    
    types = data.pop('$type')
    
    for d,i in zip(data.items(), types):
        k,v = d
        if isinstance(i, list) and isinstance(v, dict):
            v.update({'$type': i})
            untypenize(v)

        else:
            _type = t[i]


            if isinstance(_type, type):
                if _type == bytes:
                    v = v.encode()
                elif _type == datetime:
                    v = datetime.fromisoformat(v)
                else:
                    v =  _type(v)

            data.update({k:v})

    return data



def iterate_dict(item: Mapping):
    """
    Iterate through all nested dictionaries
    and yield them.

    Parameters:
        item (Mapping):
            The item /dict to be iterate

    """
    for k,v in item.items():
        if isinstance(v, Mapping):
            yield from iterate_dict(v)
        else:
            yield k,v 

def deco(dec, condition):
    """
    Set the function a decorator if the
    condition is True else ignore.

    Parameters:
        decorator (Function):
            A decorator function
        
        condition (bool):
            The codition inorder to set the decorator.

    """

    def wrapper(func):
        if not condition:
            #: Ignore the decorator.
            return func

        return dec(func)

    return wrapper


