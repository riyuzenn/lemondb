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


from typing import Mapping

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


