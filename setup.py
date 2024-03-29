# Copyright (c) 2021 riyuzenn

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

from setuptools import setup, find_packages
from lemondb import __version__


def get_long_description():
    with open("README.md", encoding="utf-8") as f:
        readme = f.read()

    return readme

extras_require = {
    'logger': 'loguru>=0.5.3',
    'crypto': 'sidle>=0.0.4',
    'cli': 'hypecli>=0.0.8'
}

setup(
    
    name="lemondb", 
    description="Simple and lightweight document oriented database",
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author = 'riyuzenn',
    license = 'MIT',
    version = __version__,
    packages = [p for p in find_packages() if 'test' not in p],
    extras_require=extras_require

)
