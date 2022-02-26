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

import os
import sys
import pathlib

env_dir = pathlib.Path().home() / '.lemondb'
log_dir = env_dir / 'logs'

if not env_dir.exists():
    os.mkdir(env_dir)
elif env_dir.is_file():
    os.remove(str(env_dir.absolute()))
    os.mkdir(env_dir)

log_path = str((log_dir / 'lemon-logs').absolute())

try:
    import loguru
    logger = loguru.logger
except ModuleNotFoundError:
    logger = None

if logger:
    logger.remove()
    logger.add(log_path, rotation="100 MB", compression='zip')
    logger.add(
        sys.stdout, 
        format='<green>[{time:HH:mm:ss}]</green> |  <magenta>{level}</magenta>  | <lvl>{message}</lvl>', 
        level='INFO'
    )
    logger.opt(colors=True)