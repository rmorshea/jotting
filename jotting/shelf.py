import sys

if sys.version_info >= (3, 5):
    from ._shelf_py35 import *
else:
    from ._shelf_py27 import *
